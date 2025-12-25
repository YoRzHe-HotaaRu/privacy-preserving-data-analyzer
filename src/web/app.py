"""FastAPI Web Application"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import tempfile

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

# Import our modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data_ingestion import load_file, CSVLoader
from src.pii_detection import PIIDetector
from src.anonymization import DataAnonymizer
from src.differential_privacy import DifferentialPrivacyEngine
from src.risk_assessment import RiskCalculator, ComplianceChecker
from src.reporting import ReportGenerator, generate_privacy_certificate

# Initialize FastAPI
app = FastAPI(
    title="Privacy-Preserving Data Analyzer",
    description="Analyze data while protecting privacy",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Initialize components
pii_detector = PIIDetector()
anonymizer = DataAnonymizer()
dp_engine = DifferentialPrivacyEngine(epsilon=1.0, delta=1e-5)
risk_calculator = RiskCalculator()
compliance_checker = ComplianceChecker()
report_generator = ReportGenerator()

# In-memory storage for session data
session_data: Dict[str, Any] = {}


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page."""
    html_path = static_dir / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding='utf-8'))
    return HTMLResponse(content="<h1>Privacy-Preserving Data Analyzer</h1><p>Static files not found.</p>")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and analyze a data file.
    
    Supports CSV, JSON, and Excel files.
    """
    # Validate file type
    allowed_extensions = ['.csv', '.json', '.xlsx', '.xls']
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(400, f"Unsupported file type. Allowed: {allowed_extensions}")
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Load data
        df = load_file(tmp_path)
        
        # Get data summary
        data_summary = {
            'filename': file.filename,
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'preview': df.head(5).to_dict(orient='records')
        }
        
        # Detect PII in sample
        pii_results = {}
        for col in df.columns:
            sample = df[col].dropna().head(5).astype(str).tolist()
            col_pii = []
            for val in sample:
                detected = pii_detector.detect(val)
                col_pii.extend(detected)
            if col_pii:
                pii_results[col] = {
                    'count': len(col_pii),
                    'types': list(set(p['entity_type'] for p in col_pii))
                }
        
        # Store in session
        session_id = datetime.now().strftime('%Y%m%d%H%M%S')
        session_data[session_id] = {
            'df': df,
            'filename': file.filename,
            'pii_results': pii_results
        }
        
        return {
            'session_id': session_id,
            'data_summary': data_summary,
            'pii_detected': pii_results,
            'pii_count': sum(r['count'] for r in pii_results.values()),
            'columns_with_pii': list(pii_results.keys())
        }
    
    finally:
        # Cleanup
        Path(tmp_path).unlink(missing_ok=True)


@app.post("/api/v1/analyze")
async def analyze_data(
    session_id: str,
    epsilon: float = Query(1.0, ge=0.01, le=10.0),
    anonymization_strategy: str = Query("mask", regex="^(mask|suppress|generalize|hash)$"),
    quasi_identifiers: Optional[str] = Query(None),
    sensitive_attribute: Optional[str] = Query(None)
):
    """
    Analyze data with privacy protection.
    
    Args:
        session_id: Session ID from upload
        epsilon: Privacy budget
        anonymization_strategy: Strategy to use
        quasi_identifiers: Comma-separated column names
        sensitive_attribute: Sensitive attribute column
    """
    if session_id not in session_data:
        raise HTTPException(404, "Session not found. Please upload data first.")
    
    data = session_data[session_id]
    df = data['df']
    pii_results = data['pii_results']
    
    # Parse quasi-identifiers
    qi_list = [q.strip() for q in quasi_identifiers.split(',')] if quasi_identifiers else []
    qi_list = [q for q in qi_list if q in df.columns]
    
    # Anonymize data
    pii_columns = {col: info['types'][0] for col, info in pii_results.items() if info['types']}
    anonymized_df = anonymizer.anonymize_dataframe(df, pii_columns)
    
    # Calculate privacy metrics
    dp_engine.reset_budget()
    dp_engine.epsilon = epsilon
    
    privacy_report = dp_engine.get_budget_report()
    
    # Risk assessment
    risk_results = {}
    if qi_list:
        risk_results = risk_calculator.calculate_all_metrics(
            df, qi_list, sensitive_attribute
        )
    
    # Compliance check
    pii_summary = {
        'total_pii': sum(r['count'] for r in pii_results.values()),
        'by_type': pii_results
    }
    compliance = compliance_checker.check_all(risk_results, pii_summary, True)
    
    return {
        'anonymized_preview': anonymized_df.head(10).to_dict(orient='records'),
        'anonymized_columns': list(pii_columns.keys()),
        'privacy_metrics': {
            'epsilon': epsilon,
            'delta': dp_engine.delta,
            'budget_used': privacy_report['used_epsilon'],
            'k_anonymity': risk_results.get('k_anonymity', {}).get('k', 'N/A'),
            'l_diversity': risk_results.get('l_diversity', {}).get('l', 'N/A')
        },
        'risk_assessment': risk_results,
        'compliance': compliance
    }


@app.get("/api/v1/privacy-budget")
async def get_privacy_budget():
    """Get current privacy budget status."""
    return dp_engine.get_budget_report()


@app.post("/api/v1/generate-report")
async def generate_report(session_id: str):
    """Generate HTML privacy report."""
    if session_id not in session_data:
        raise HTTPException(404, "Session not found")
    
    data = session_data[session_id]
    df = data['df']
    pii_results = data['pii_results']
    
    # Generate report data
    data_summary = {'row_count': len(df), 'column_count': len(df.columns)}
    pii_summary = {'total_pii': sum(r['count'] for r in pii_results.values()), 'by_type': pii_results}
    privacy_metrics = dp_engine.get_budget_report()
    privacy_metrics['epsilon'] = dp_engine.epsilon
    privacy_metrics['delta'] = dp_engine.delta
    
    risk_results = {'overall': {'risk_level': 'Low', 'overall_risk': 0.2, 'recommendations': []}}
    compliance = compliance_checker.check_all(risk_results, pii_summary, True)
    
    html = report_generator.generate_html_report(
        data_summary, pii_summary, privacy_metrics, risk_results, compliance
    )
    
    return HTMLResponse(content=html)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
