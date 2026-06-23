# 🚀 AI Financial Research Platform


## Overview

AI Financial Research Platform is a multi-agent system that combines market data, financial news, technical analysis, and document-based retrieval to generate comprehensive and explainable investment insights.

Inspired by platforms like Bloomberg and Perplexity, this project enables users to ask natural language questions such as:

```text
Should I invest in Nvidia?

Compare AMD and Nvidia.

What risks are mentioned in Tesla's annual report?

Summarize recent news about Microsoft.
```

The platform leverages ETL pipelines, Retrieval-Augmented Generation (RAG), and LangGraph-based agentic workflows to provide accurate and context-aware responses.

---

## Architecture

```text
                          User
                            │
                      React Frontend
                            │
                         FastAPI
                            │
                    LangGraph Workflow
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
 Market Agent          News Agent          RAG Agent
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    Technical Agent
                            │
                      Report Agent
                            │
                      Critic Agent
                            │
                       Final Answer
```

---

## Features

### Multi-Agent Workflow

- Planner Agent
- Market Data Agent
- News Analysis Agent
- Document RAG Agent
- Technical Analysis Agent
- Report Generation Agent
- Critic Agent

---

### Market Intelligence

- Stock price history
- Market capitalization
- Revenue and earnings
- Financial statements
- P/E ratio

---

### News Analysis

- Latest company news
- Sentiment analysis
- News summarization
- Source attribution

---

### Technical Analysis

Supports:

- RSI
- SMA
- EMA
- MACD
- Bollinger Bands

---

### Document Intelligence (RAG)

Upload:

- Annual reports
- Earnings transcripts
- Financial PDFs

Capabilities:

- Semantic search
- Metadata filtering
- Source citations
- Context-aware responses

---

### Evaluation Pipeline

Using:

- RAGAS
- DeepEval

Metrics:

- Faithfulness
- Context Precision
- Relevancy
- Hallucination Detection

---

### Production Features

- REST APIs
- PostgreSQL
- Redis caching
- Docker
- GitHub Actions
- AWS Deployment

---

# ETL Pipelines

## Market Data Pipeline

### Extract

- Yahoo Finance

### Transform

- Technical indicators
- Volatility metrics
- Derived features

### Load

PostgreSQL

---

## News Pipeline

### Extract

- GNews API

### Transform

- Cleaning
- Deduplication
- Sentiment analysis

### Load

PostgreSQL

---

## Document Pipeline

### Extract

- PDFs

### Transform

- Chunking
- Embedding generation

### Load

ChromaDB

---

## Tech Stack

### Backend

- FastAPI
- SQLAlchemy
- Pydantic

### Agent Framework

- LangGraph
- LangChain

### LLM

- Gemini 2.5 Flash
- OpenAI

### Vector Database

- ChromaDB

### Relational Database

- PostgreSQL

### Cache

- Redis

### Embedding Models

- BAAI/bge-small-en-v1.5
- Sentence Transformers

### Financial Data

- yfinance

### News

- GNews API

### Technical Indicators

- pandas-ta

### Evaluation

- RAGAS
- DeepEval

### Deployment

- Docker
- Docker Compose
- AWS EC2
- GitHub Actions

---

# Folder Structure

```text
ai-financial-research-platform/
│
├── app/
│   ├── agents/
│   ├── api/
│   ├── tools/
│   ├── workflows/
│   ├── rag/
│   ├── vectorstore/
│   ├── database/
│   ├── evaluation/
│   ├── cache/
│   ├── schemas/
│   ├── config/
│   └── main.py
│
├── frontend/
│
├── tests/
│
├── notebooks/
│
├── data/
│
├── docs/
│
├── docker/
│
├── requirements.txt
│
├── .env
│
└── README.md
```

---

# API Endpoints

## Chat

```http
POST /chat
```

Request:

```json
{
  "query": "Should I invest in Nvidia?"
}
```

---

## Analyze Company

```http
POST /analyze
```

Request:

```json
{
  "ticker": "NVDA"
}
```

---

## Compare Companies

```http
POST /compare
```

Request:

```json
{
  "ticker1": "NVDA",
  "ticker2": "AMD"
}
```

---

## Upload Documents

```http
POST /upload
Content-Type: multipart/form-data
```

## Document RAG Endpoints

Upload and index a PDF:

```http
POST /rag/ingest
Content-Type: application/json
```

```json
{
  "file_path": "data/documents/tesla_annual_report.pdf"
}
```

Retrieve relevant chunks with citations:

```http
POST /rag/query
Content-Type: application/json
```

```json
{
  "query": "What risks are mentioned in Tesla's annual report?",
  "k": 4
}
```

---

# Example Queries

```text
Should I invest in Tesla?

Compare Nvidia and AMD.

Summarize recent news about Microsoft.

What risks are discussed in Apple's annual report?

Explain Nvidia's revenue growth.

Analyze Amazon stock.
```

---

# Getting Started

## Clone Repository

```bash
git clone https://github.com/<username>/ai-financial-research-platform.git

cd ai-financial-research-platform
```

---

## Create Virtual Environment

```bash
python -m venv .venv

source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create:

```text
.env
```

Example:

```env
GOOGLE_API_KEY=
OPENAI_API_KEY=
GNEWS_API_KEY=

POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

REDIS_HOST=
REDIS_PORT=
```

---

## Run FastAPI

```bash
uvicorn app.main:app --reload
```

Document RAG dependencies:

```bash
pip install -r requirements.txt
```

The RAG pipeline uses:

- `PyPDFLoader` for PDF extraction
- `RecursiveCharacterTextSplitter` for chunking
- `BAAI/bge-small-en-v1.5` via Hugging Face embeddings
- `Chroma` for vector storage
- per-chunk source metadata for citation support

---

## Run React Frontend

```bash
cd frontend
npm install
npm run dev
```

---

# Roadmap

## Phase 1

- [x] Project Setup
- [ ] FastAPI Backend
- [ ] PostgreSQL

---

## Phase 2

- [ ] Market Data ETL
- [ ] News ETL
- [ ] Technical Indicators

---

## Phase 3

- [ ] Document RAG
- [ ] ChromaDB
- [ ] Source Citation

---

## Phase 4

- [ ] LangGraph Multi-Agent Workflow
- [ ] Report Agent
- [ ] Critic Agent

---

## Phase 5

- [ ] React UI
- [ ] Company Comparison

---

## Phase 6

- [ ] RAGAS Evaluation
- [ ] DeepEval
- [ ] Redis Cache
- [ ] Docker

---

## Phase 7

- [ ] GitHub Actions
- [ ] AWS Deployment

---

# Future Enhancements

- Portfolio Analysis Agent
- Watchlist Alerts
- Real-Time Streaming
- User Authentication
- Multi-User Support
- MLflow Integration
- Airflow Scheduler
- Kafka Event Pipeline

---

# Inspiration

- Bloomberg Terminal
- Perplexity AI
- Yahoo Finance
- Morningstar

---

# License

MIT License

---

## Author

**Priyanshi Dobariya**

AI Engineer | Python Developer | GenAI Enthusiast

GitHub: https://github.com/priyanshidobariya72-star
LinkedIn: https://linkedin.com/in/priyanshi-dobariya-974a58221

---
⭐ If you found this project interesting, consider giving it a star!
