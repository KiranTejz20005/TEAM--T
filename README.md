# FinScribe.ai — Automated MD&A Draft Generator

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.0-blue.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

🌐 **Live Website:** [FinScribe.ai](https://finscribe-ai-0c6xvfms.sites.blink.new/)

---

## 🎯 Problem Statement

**Financial analysts spend 60-80% of their time on manual, repetitive tasks** when preparing Management Discussion & Analysis (MD&A) reports:

### Key Challenges:

1. **Manual Data Extraction**: Extracting financial data from PDFs, Excel sheets, and various formats is time-consuming and error-prone
2. **Complex Calculations**: Computing Year-over-Year (YoY), Quarter-over-Quarter (QoQ) changes, and financial ratios manually
3. **Narrative Generation**: Writing coherent, compliant MD&A narratives that explain trends and drivers
4. **Lack of Traceability**: Difficulty in citing source documents and ensuring audit trails
5. **Inconsistent Quality**: Human errors in calculations and narrative inconsistencies
6. **Slow Turnaround**: Takes days to weeks to produce comprehensive MD&A reports

### The Impact:

* **Lost Productivity**: Analysts spend 40+ hours per quarter on MD&A preparation
* **Compliance Risks**: Manual processes increase risk of regulatory non-compliance
* **Delayed Insights**: Slow reporting delays strategic decision-making
* **High Costs**: Manual analysis is expensive and doesn't scale

--

## 💡 Our Solution

**FinScribe.ai** is an AI-powered financial analysis assistant that automates MD&A generation using:

* **RAG (Retrieval-Augmented Generation)**: Grounds all narratives in source documents with citations
* **LLM-Powered Summarization**: Uses Google Gemini to generate SEC-compliant narratives
* **Automated KPI Computation**: Calculates financial ratios, trends, and deltas automatically
* **Multi-Agent System**: Specialized AI agents for different analysis tasks
* **Guardrails & Evaluation**: Ensures accuracy, compliance, and quality of outputs

### What We Deliver (MVP):

✅ **Automated MD&A Draft Generation**

* Upload financial statements (PDF, Excel, CSV)
* Automatic extraction of key metrics
* YoY/QoQ trend analysis
* Sectioned markdown output (Executive Summary, Results of Operations, Liquidity, Risks)

✅ **RAG-Based Citation System**

* Every claim linked to source documents
* Chunk-level citations for audit trails
* Confidence scores for generated content

✅ **Interactive Chat Interface**

* Ask questions about uploaded financial data
* Natural language queries
* Voice-enabled assistant

✅ **Financial Analytics Dashboard**

* Visual KPI tracking
* Trend analysis and forecasting
* Comparative analysis

---

## 🏗️ Architecture

### Technology Stack

**Backend (Python)**

* **Framework**: FastAPI (async, high-performance)
* **LLM**: Google Gemini 1.5 Flash (free tier, 1M tokens/min)
* **Vector DB**: ChromaDB (embeddings & semantic search)
* **RAG**: LangChain (document chunking, retrieval)
* **ML/AI**: Sentence Transformers, Scikit-learn
* **Data Processing**: Pandas, NumPy
* **Document Parsing**: PyMuPDF, pdfplumber, openpyxl

**Frontend (React)**

* **Framework**: React 18 with Hooks
* **UI**: TailwindCSS
* **Data Fetching**: React Query
* **Visualization**: Plotly, Recharts , Matplotlib

**AI/ML Components**

1. **Multi-Agent System**: Coordinator, Analyst, Researcher, Validator agents
2. **RAG Service**: Document chunking, embedding, semantic retrieval
3. **Financial Analyzer**: KPI computation, ratio analysis
4. **Guardrails**: Numeric validation, compliance checks, hallucination detection
5. **Evaluator**: Response quality scoring, citation validation

### System Flow

```
User Upload → Document Processor → Data Extraction → KPI Engine
                                                          ↓
User Query → RAG Retriever → Context Builder → LLM (Gemini) → Guardrails → Response
                                                          ↓
                                              MD&A Generator → Sectioned Draft
```

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

* Python 3.11+
* Node.js 18+
* Google Gemini API Key 

### Step 1: Clone & Setup

```bash
cd TEAM--T
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
copy env.example .env
# Edit .env and add your GEMINI_API_KEY

# Initialize database
python init_db.py

# Start backend server
python -m app.main
```

Backend will run on: **[http://localhost:8000](http://localhost:8000)**
API Docs: **[http://localhost:8000/docs](http://localhost:8000/docs)**

### Step 3: Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start frontend
npm start
```

Frontend will run on: **[http://localhost:3000](http://localhost:3000)**

---

**Built with ❤️ for Financial Analysts**

*Automating the boring stuff so you can focus on insights.*
