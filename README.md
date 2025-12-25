# 🔒 Privacy-Preserving Data Analyzer

A comprehensive system for analyzing sensitive data while protecting individual privacy through differential privacy, PII detection, and data anonymization.

## ✨ Features

- **🔍 PII Detection** - Automatic detection of 14+ PII types using Microsoft Presidio
- **🎭 Anonymization** - 6 strategies: masking, suppression, generalization, perturbation, tokenization, hashing
- **🔐 Differential Privacy** - Laplace, Gaussian, and Exponential mechanisms with budget tracking
- **🤖 LLM Analysis** - Privacy-aware insights using OpenRouter bytedance-seed/seed-1.6-flash
- **⚠️ Risk Assessment** - k-anonymity, l-diversity, t-closeness metrics
- **✅ Compliance** - GDPR, HIPAA, CCPA compliance scoring
- **📊 Web Interface** - Modern dark theme dashboard

## 🚀 Quick Start

### Installation

```bash
cd privacy-preserving-data-analyzer
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

### Configuration

Copy `.env.example` to `.env` and add your OpenRouter API key:

```bash
OPENROUTER_API_KEY=sk-or-v1-your-api-key
```

### Run Web Interface

```bash
cd src
python main.py server
```

Open http://localhost:8000 in your browser.

### Command Line Analysis

```bash
cd src
python main.py analyze --input ../data/samples/sample_customer_data.csv --output report.html --epsilon 1.0
```

## 📁 Project Structure

```
privacy-preserving-data-analyzer/
├── src/
│   ├── data_ingestion/    # CSV, JSON, Excel loaders
│   ├── pii_detection/     # Presidio-based PII detection
│   ├── anonymization/     # Anonymization strategies
│   ├── differential_privacy/  # DP mechanisms
│   ├── llm_analysis/      # OpenRouter LLM integration
│   ├── risk_assessment/   # Privacy risk calculation
│   ├── reporting/         # HTML report generation
│   ├── web/              # FastAPI + HTML/CSS/JS
│   └── main.py           # CLI entry point
├── data/samples/          # Sample datasets
└── requirements.txt
```

## 🛡️ Privacy Guarantees

This system provides (ε, δ)-differential privacy:

- **Epsilon (ε)** - Privacy loss parameter (default: 1.0)
- **Delta (δ)** - Failure probability (default: 0.00001)

Lower epsilon = stronger privacy (but reduced utility).

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web dashboard |
| `/api/v1/upload` | POST | Upload data file |
| `/api/v1/analyze` | POST | Run analysis |
| `/api/v1/privacy-budget` | GET | Get budget status |
| `/api/v1/generate-report` | POST | Generate HTML report |

## 📜 License

MIT License
