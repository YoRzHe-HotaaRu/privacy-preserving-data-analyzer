# 🔒 Privacy-Preserving Data Analyzer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/Differential%20Privacy-Enabled-purple?style=for-the-badge" alt="DP Enabled">
</p>

A comprehensive, production-ready system for analyzing sensitive data while protecting individual privacy through differential privacy mechanisms, PII detection, data anonymization, and compliance verification.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#%EF%B8%8F-configuration)
- [Usage](#-usage)
  - [Web Interface](#web-interface)
  - [Command Line Interface](#command-line-interface)
  - [Python API](#python-api)
- [API Reference](#-api-reference)
- [Privacy Guarantees](#%EF%B8%8F-privacy-guarantees)
- [Compliance](#-compliance)
- [Testing](#-testing)
- [Docker Deployment](#-docker-deployment)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

The Privacy-Preserving Data Analyzer is designed for organizations that need to extract insights from sensitive data while ensuring individual privacy is protected. It implements state-of-the-art privacy techniques including:

- **Differential Privacy**: Mathematical guarantees on privacy leakage
- **PII Detection**: Automatic identification of personally identifiable information
- **Data Anonymization**: Multiple strategies to de-identify sensitive data
- **Risk Assessment**: k-anonymity, l-diversity, and t-closeness metrics
- **Compliance Scoring**: Automated GDPR, HIPAA, and CCPA compliance checks

---

## ✨ Features

### 🔍 PII Detection
Automatic detection of **14+ PII types** using Microsoft Presidio:
- Names, emails, phone numbers
- Social Security Numbers (SSN)
- Credit card numbers
- Addresses and dates of birth
- Medical record numbers
- IP addresses, URLs
- Custom entity patterns

### 🎭 Anonymization Strategies
Six different anonymization techniques to suit various use cases:

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **Masking** | Replaces characters with `*` | Display redaction |
| **Suppression** | Removes values entirely | Complete removal |
| **Generalization** | Replaces with categories | Utility preservation |
| **Perturbation** | Adds controlled noise | Numeric data |
| **Tokenization** | Replaces with tokens | Reversible anonymization |
| **Hashing** | One-way cryptographic hash | Irreversible anonymization |

### 🔐 Differential Privacy
Implementation of core DP mechanisms with budget tracking:
- **Laplace Mechanism**: For numeric queries with known sensitivity
- **Gaussian Mechanism**: For (ε, δ)-DP guarantees
- **Exponential Mechanism**: For categorical/discrete outputs
- **Budget Management**: Track and manage privacy budget consumption

### 🤖 LLM-Powered Analysis
Privacy-aware insights using OpenRouter integration:
- Aggregate-only data analysis
- Safe query validation
- Response sanitization
- Privacy-preserving prompts

### ⚠️ Risk Assessment
Comprehensive privacy risk metrics:
- **k-Anonymity**: Measures group indistinguishability
- **l-Diversity**: Ensures sensitive attribute diversity
- **t-Closeness**: Limits attribute distribution distance
- **Re-identification Risk Scoring**: Quantifies attack vulnerability

### ✅ Compliance Verification
Automated compliance scoring for major regulations:
- **GDPR** (General Data Protection Regulation)
- **HIPAA** (Health Insurance Portability and Accountability Act)
- **CCPA** (California Consumer Privacy Act)

### 📊 Modern Web Interface
Interactive dark-theme dashboard featuring:
- Drag-and-drop file upload
- Real-time PII detection visualization
- Interactive privacy metrics display
- One-click report generation
- Privacy certificate generation

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Web Interface (FastAPI)                       │
│                    HTML/CSS/JS + REST API Endpoints                   │
└───────────────────────────────────┬──────────────────────────────────┘
                                    │
┌───────────────────────────────────▼──────────────────────────────────┐
│                          Core Pipeline                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Data      │  │    PII      │  │Anonymization│  │ Differential│  │
│  │  Ingestion  │─►│  Detection  │─►│   Engine    │─►│   Privacy   │  │
│  │             │  │  (Presidio) │  │             │  │   Engine    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
│                                                            │          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │          │
│  │    Risk     │  │ Compliance  │  │   Report    │◄───────┘          │
│  │ Assessment  │─►│   Checker   │─►│  Generator  │                   │
│  └─────────────┘  └─────────────┘  └─────────────┘                   │
└──────────────────────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼──────────────────────────────────┐
│                        LLM Analysis (Optional)                        │
│            OpenRouter API • Privacy-Aware Prompts • Safe Queries      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## � Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/privacy-preserving-data-analyzer.git
   cd privacy-preserving-data-analyzer
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy language model** (required for PII detection)
   ```bash
   python -m spacy download en_core_web_lg
   ```

5. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env and add your OpenRouter API key (optional, for LLM features)
   ```

---

## 🚀 Quick Start

### Option 1: Web Interface

```bash
cd src
python main.py server
```

Open http://localhost:8000 in your browser.

### Option 2: Command Line

```bash
cd src
python main.py analyze --input ../data/samples/sample_customer_data.csv --output report.html --epsilon 1.0
```

### Option 3: Python API

```python
from data_ingestion import load_file
from pii_detection import PIIDetector
from anonymization import DataAnonymizer
from differential_privacy import DifferentialPrivacyEngine

# Load data
df = load_file('customer_data.csv')

# Detect PII
detector = PIIDetector()
for col in df.columns:
    results = detector.detect(df[col].astype(str).tolist())

# Anonymize
anonymizer = DataAnonymizer()
anonymized_df = anonymizer.anonymize_dataframe(df, pii_columns)

# Apply differential privacy
dp_engine = DifferentialPrivacyEngine(epsilon=1.0, delta=1e-5)
private_mean = dp_engine.private_mean(df['salary'].values)
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following options:

```env
# OpenRouter API Configuration (optional - for LLM features)
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Model Configuration
LLM_MODEL=bytedance-seed/seed-1.6-flash
LLM_BASE_URL=https://openrouter.ai/api/v1

# Default Privacy Parameters
DEFAULT_EPSILON=1.0          # Privacy budget (lower = more private)
DEFAULT_DELTA=0.00001        # Failure probability
DEFAULT_K_ANONYMITY=5        # Minimum group size
DEFAULT_L_DIVERSITY=3        # Minimum distinct sensitive values
DEFAULT_T_CLOSENESS=0.2      # Maximum distribution distance

# Database (optional)
DATABASE_URL=sqlite:///data/privacy_analyzer.db

# Logging
LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Privacy Parameters

| Parameter | Description | Range | Default |
|-----------|-------------|-------|---------|
| `epsilon` (ε) | Privacy loss budget | 0.01 - 10.0 | 1.0 |
| `delta` (δ) | Failure probability | 1e-10 - 1e-3 | 1e-5 |
| `k_anonymity` | Minimum equivalence class size | 2 - 100 | 5 |
| `l_diversity` | Minimum distinct sensitive values | 2 - 20 | 3 |
| `t_closeness` | Maximum distribution distance | 0.0 - 1.0 | 0.2 |

---

## 📖 Usage

### Web Interface

1. **Upload Data**: Drag and drop or click to upload CSV, JSON, or Excel files
2. **Review PII Detection**: See automatically detected PII columns highlighted
3. **Configure Privacy**: Adjust epsilon, select anonymization strategy, set quasi-identifiers
4. **Analyze**: Run privacy-preserving analysis
5. **Download Report**: Generate and download HTML privacy report with certificate

### Command Line Interface

```bash
# Basic analysis
python main.py analyze --input data.csv

# With custom privacy budget
python main.py analyze --input data.csv --epsilon 0.5 --delta 1e-6

# Specify quasi-identifiers for k-anonymity
python main.py analyze --input data.csv --quasi "age,zipcode,gender" --sensitive "diagnosis"

# Generate report to specific path
python main.py analyze --input data.csv --output reports/my_report.html

# Run web server on custom port
python main.py server --port 9000 --host 127.0.0.1
```

### Python API

```python
# Full analysis pipeline
from main import analyze_data

results = analyze_data(
    input_path='customer_data.csv',
    output_path='privacy_report.html',
    epsilon=1.0,
    delta=1e-5,
    quasi_identifiers=['age', 'city', 'occupation'],
    sensitive_attribute='salary'
)

print(f"k-Anonymity: {results['privacy_metrics']['k_anonymity']}")
print(f"Compliance Score: {results['compliance']['gdpr']['score']}")
```

---

## 📡 API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web dashboard |
| `/api/health` | GET | Health check |
| `/api/v1/upload` | POST | Upload data file |
| `/api/v1/analyze` | POST | Run privacy analysis |
| `/api/v1/privacy-budget` | GET | Get budget status |
| `/api/v1/generate-report` | POST | Generate HTML report |

### Upload Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@customer_data.csv"
```

**Response:**
```json
{
  "session_id": "20231225120000",
  "data_summary": {
    "filename": "customer_data.csv",
    "row_count": 1000,
    "column_count": 10,
    "columns": ["id", "name", "email", ...],
    "preview": [...]
  },
  "pii_detected": {
    "email": {"count": 1000, "types": ["EMAIL_ADDRESS"]},
    "name": {"count": 1000, "types": ["PERSON"]}
  },
  "pii_count": 2000
}
```

### Analyze Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/analyze?session_id=20231225120000&epsilon=1.0&anonymization_strategy=mask"
```

**Query Parameters:**
- `session_id` (required): Session ID from upload
- `epsilon` (optional): Privacy budget (0.01-10.0, default: 1.0)
- `anonymization_strategy` (optional): mask, suppress, generalize, hash
- `quasi_identifiers` (optional): Comma-separated column names
- `sensitive_attribute` (optional): Sensitive column name

---

## 🛡️ Privacy Guarantees

### Differential Privacy

This system provides **(ε, δ)-differential privacy**:

$$P(M(D) \in S) \leq e^{\epsilon} \cdot P(M(D') \in S) + \delta$$

Where:
- **M** is the analysis mechanism
- **D** and **D'** are neighboring datasets (differing in one record)
- **ε (epsilon)** is the privacy loss parameter
- **δ (delta)** is the failure probability

**Interpretation:**
- **ε = 0.1**: Very strong privacy (minimal information leakage)
- **ε = 1.0**: Standard privacy (good balance)
- **ε = 10.0**: Weak privacy (prioritizes utility)

### Privacy Budget Management

The system tracks cumulative privacy loss across multiple queries:

```python
# Initialize with budget
dp_engine = DifferentialPrivacyEngine(epsilon=5.0)

# Each query consumes budget
result1 = dp_engine.private_mean(data1)  # Uses 1.0 epsilon
result2 = dp_engine.private_sum(data2)   # Uses 0.5 epsilon

# Check remaining budget
report = dp_engine.get_budget_report()
print(f"Used: {report['used_epsilon']}, Remaining: {report['remaining_epsilon']}")
```

---

## 📋 Compliance

### GDPR Compliance

Requirements checked:
- Data minimization
- Purpose limitation
- Lawfulness of processing
- Transparency
- Right to erasure (anonymization support)

### HIPAA Compliance

Requirements checked:
- PHI identification
- Minimum necessary standard
- De-identification verification
- Safe Harbor method compliance

### CCPA Compliance

Requirements checked:
- Personal information disclosure
- Consumer rights support
- Opt-out mechanisms
- Sale of personal information

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_pii_detection.py -v

# Run only fast tests (skip slow/benchmark tests)
pytest tests/ -v -m "not slow"

# Run performance benchmarks
pytest tests/test_performance.py -v --benchmark-only
```

### Test Coverage

The test suite covers:
- ✅ Data Ingestion (CSV, JSON, Excel)
- ✅ PII Detection (all entity types)
- ✅ Anonymization (all strategies)
- ✅ Differential Privacy (all mechanisms)
- ✅ Risk Assessment (k-anonymity, l-diversity, t-closeness)
- ✅ LLM Analysis (client, prompts, validators)
- ✅ Reporting (HTML generation, certificates)
- ✅ Web API (all endpoints)

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint
flake8 src/ tests/

# Type checking
mypy src/

# Security scan
bandit -r src/
```

---

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t privacy-analyzer:latest .
```

### Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -e OPENROUTER_API_KEY=your-key \
  -v $(pwd)/data:/app/data \
  --name privacy-analyzer \
  privacy-analyzer:latest
```

### Docker Compose

```yaml
version: '3.8'
services:
  privacy-analyzer:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## 📁 Project Structure

```
privacy-preserving-data-analyzer/
├── 📂 src/
│   ├── 📂 data_ingestion/         # File loaders (CSV, JSON, Excel)
│   │   ├── __init__.py
│   │   ├── base_loader.py         # Abstract base loader
│   │   ├── csv_loader.py          # CSV file support
│   │   ├── excel_loader.py        # Excel file support
│   │   └── json_loader.py         # JSON file support
│   │
│   ├── 📂 pii_detection/          # PII detection with Presidio
│   │   ├── __init__.py
│   │   ├── detector.py            # Main PII detector class
│   │   └── custom_entities.py     # Custom entity recognizers
│   │
│   ├── 📂 anonymization/          # Data anonymization strategies
│   │   ├── __init__.py
│   │   ├── anonymizer.py          # Main anonymizer class
│   │   └── strategies.py          # Anonymization strategies
│   │
│   ├── 📂 differential_privacy/   # DP mechanisms
│   │   ├── __init__.py
│   │   ├── dp_engine.py           # Core DP engine
│   │   └── budget_manager.py      # Privacy budget tracking
│   │
│   ├── 📂 llm_analysis/           # LLM-powered analysis
│   │   ├── __init__.py
│   │   ├── llm_client.py          # OpenRouter client
│   │   ├── prompt_engine.py       # Privacy-aware prompts
│   │   ├── insight_generator.py   # Generate insights
│   │   └── safe_query.py          # Query validation
│   │
│   ├── 📂 risk_assessment/        # Privacy risk calculation
│   │   ├── __init__.py
│   │   ├── risk_calculator.py     # k-anonymity, l-diversity, etc.
│   │   └── compliance_checker.py  # GDPR, HIPAA, CCPA checks
│   │
│   ├── 📂 reporting/              # Report generation
│   │   ├── __init__.py
│   │   ├── report_generator.py    # HTML report generator
│   │   └── privacy_certificate.py # Certificate generation
│   │
│   ├── 📂 web/                    # FastAPI web application
│   │   ├── app.py                 # FastAPI app
│   │   ├── 📂 static/
│   │   │   ├── index.html         # Main dashboard
│   │   │   ├── 📂 css/
│   │   │   └── 📂 js/
│   │   └── 📂 templates/
│   │
│   ├── 📂 config/                 # Configuration management
│   │   └── settings.py
│   │
│   ├── __init__.py
│   └── main.py                    # CLI entry point
│
├── 📂 tests/                      # Test suite
│   ├── conftest.py                # Pytest fixtures
│   ├── test_data_ingestion.py
│   ├── test_pii_detection.py
│   ├── test_anonymization.py
│   ├── test_differential_privacy.py
│   ├── test_risk_assessment.py
│   ├── test_llm_analysis.py
│   ├── test_reporting.py
│   ├── test_web_api.py
│   └── test_performance.py
│
├── 📂 data/
│   ├── 📂 samples/                # Sample datasets
│   │   └── sample_customer_data.csv
│   └── 📂 outputs/                # Generated reports
│
├── 📂 .github/
│   └── 📂 workflows/
│       └── ci.yml                 # CI/CD pipeline
│
├── .env.example                   # Environment template
├── .gitignore
├── .pre-commit-config.yaml        # Pre-commit hooks
├── Dockerfile                     # Docker configuration
├── pyproject.toml                 # Project configuration
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies
└── README.md                      # This file
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run tests and linting**
   ```bash
   pytest tests/ -v
   black src/ tests/
   flake8 src/ tests/
   ```
5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Code Style

- Follow PEP 8 guidelines
- Use Black for formatting (line length: 120)
- Sort imports with isort
- Add type hints where possible
- Write docstrings for all public functions/classes

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Microsoft Presidio](https://github.com/microsoft/presidio) - PII detection
- [OpenRouter](https://openrouter.ai/) - LLM API access
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [spaCy](https://spacy.io/) - NLP processing

---

<p align="center">
  <strong>Built with ❤️ for privacy</strong>
</p>
