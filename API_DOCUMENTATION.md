# FinMDA-Bot API Documentation

## Overview

FinMDA-Bot provides a comprehensive REST API for financial document analysis, conversational AI, and advanced analytics. This documentation covers all available endpoints, request/response schemas, and usage examples.

## Base URL

```
https://finmda-bot.onrender.com/api/v1
```

## Authentication

All API requests require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Rate Limiting

- **Rate Limit**: 60 requests per minute per user
- **Headers**: Rate limit information is included in response headers
- **Exceeded**: Returns 429 status code with retry-after header

## Common Response Formats

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Error Response
```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Endpoints

### 1. Health Check

#### GET /health

Check the health status of the API and its dependencies.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "database_status": "healthy",
  "services_status": {
    "database": "healthy",
    "openai_api": "configured",
    "upload_directory": "ready",
    "chroma_directory": "ready"
  }
}
```

### 2. Document Management

#### POST /documents/upload

Upload and process a financial document.

**Request:**
- **Content-Type**: `multipart/form-data`
- **Body**: File upload with metadata

**Parameters:**
- `file` (required): Document file (PDF, Excel, CSV)
- `metadata` (optional): Additional document metadata

**Response:**
```json
{
  "document_id": 123,
  "filename": "financial_report.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "upload_date": "2024-01-01T00:00:00Z",
  "processing_status": "completed"
}
```

**Example:**
```bash
curl -X POST "https://finmda-bot.onrender.com/api/v1/documents/upload" \
  -H "Authorization: Bearer <token>" \
  -F "file=@financial_report.pdf"
```

#### GET /documents/

List all uploaded documents.

**Query Parameters:**
- `skip` (optional): Number of documents to skip (default: 0)
- `limit` (optional): Maximum number of documents to return (default: 100)

**Response:**
```json
[
  {
    "id": 123,
    "filename": "financial_report.pdf",
    "file_type": "pdf",
    "file_size": 1024000,
    "upload_date": "2024-01-01T00:00:00Z",
    "is_processed": true,
    "processing_error": null
  }
]
```

#### GET /documents/{document_id}

Get detailed information about a specific document.

**Response:**
```json
{
  "id": 123,
  "filename": "financial_report.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "upload_date": "2024-01-01T00:00:00Z",
  "is_processed": true,
  "processing_error": null,
  "extracted_text": "Document content...",
  "extracted_tables": [...],
  "metadata": {...}
}
```

#### DELETE /documents/{document_id}

Delete a document and its associated data.

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

### 3. Conversational AI

#### POST /chat/query

Process a conversational query using the multi-agent system.

**Request:**
```json
{
  "query": "What is the revenue trend for this quarter?",
  "session_id": 456,
  "document_id": 123,
  "context": {
    "additional_info": "Any additional context"
  }
}
```

**Response:**
```json
{
  "response": "Based on the financial data, revenue has increased by 15% this quarter...",
  "session_id": 456,
  "message_id": 789,
  "confidence_score": 0.92,
  "citations": [
    {
      "document_id": 123,
      "chunk_index": 0,
      "relevance_score": 0.95,
      "source": "Document 123, Chunk 0",
      "content": "Revenue for Q3 was $1,000,000..."
    }
  ],
  "processing_time": 1.5,
  "model_used": "gpt-4"
}
```

#### POST /chat/sessions

Create a new chat session.

**Request:**
```json
{
  "document_id": 123,
  "session_name": "Q3 Analysis"
}
```

**Response:**
```json
{
  "id": 456,
  "document_id": 123,
  "session_name": "Q3 Analysis",
  "created_at": "2024-01-01T00:00:00Z",
  "last_activity": "2024-01-01T00:00:00Z",
  "message_count": 0
}
```

#### GET /chat/sessions/{session_id}

Get chat session details.

**Response:**
```json
{
  "id": 456,
  "document_id": 123,
  "session_name": "Q3 Analysis",
  "created_at": "2024-01-01T00:00:00Z",
  "last_activity": "2024-01-01T00:00:00Z",
  "message_count": 5
}
```

#### GET /chat/sessions/{session_id}/messages

Get chat messages for a session.

**Query Parameters:**
- `skip` (optional): Number of messages to skip (default: 0)
- `limit` (optional): Maximum number of messages to return (default: 50)

**Response:**
```json
[
  {
    "id": 789,
    "session_id": 456,
    "role": "user",
    "content": "What is the revenue trend?",
    "timestamp": "2024-01-01T00:00:00Z",
    "model_used": null,
    "confidence_score": null,
    "citations": null
  },
  {
    "id": 790,
    "session_id": 456,
    "role": "assistant",
    "content": "Based on the data...",
    "timestamp": "2024-01-01T00:00:00Z",
    "model_used": "gpt-4",
    "confidence_score": 0.92,
    "citations": [...]
  }
]
```

### 4. Financial Analytics

#### POST /analytics/ratios

Calculate financial ratios for a document.

**Request:**
```json
{
  "document_id": 123,
  "ratio_types": ["liquidity", "profitability", "leverage"],
  "period": "current"
}
```

**Response:**
```json
{
  "document_id": 123,
  "ratios": {
    "liquidity": {
      "current_ratio": 2.5,
      "quick_ratio": 2.0,
      "cash_ratio": 1.0
    },
    "profitability": {
      "gross_margin": 0.4,
      "net_margin": 0.15,
      "roe": 0.125
    },
    "leverage": {
      "debt_ratio": 0.4,
      "debt_to_equity": 0.67,
      "interest_coverage": 4.0
    }
  },
  "calculation_date": "2024-01-01T00:00:00Z",
  "confidence_score": 0.95
}
```

#### POST /analytics/forecast

Generate financial forecasts.

**Request:**
```json
{
  "document_id": 123,
  "metric": "revenue",
  "periods": 12,
  "method": "prophet"
}
```

**Response:**
```json
{
  "document_id": 123,
  "metric": "revenue",
  "forecast_data": [
    {
      "date": "2024-02-01",
      "value": 1100000,
      "lower_bound": 1050000,
      "upper_bound": 1150000
    }
  ],
  "confidence_intervals": [
    {
      "date": "2024-02-01",
      "lower": 1050000,
      "upper": 1150000
    }
  ],
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /analytics/trends

Analyze trends in financial data.

**Request:**
```json
{
  "document_id": 123,
  "metrics": ["revenue", "profit"],
  "time_period": "24_months"
}
```

**Response:**
```json
{
  "document_id": 123,
  "trends": {
    "revenue": {
      "trend_direction": "increasing",
      "trend_strength": 0.85,
      "slope": 10000,
      "r_squared": 0.92,
      "p_value": 0.001,
      "forecast_next_period": 1200000,
      "volatility": 0.05
    },
    "profit": {
      "trend_direction": "increasing",
      "trend_strength": 0.78,
      "slope": 5000,
      "r_squared": 0.88,
      "p_value": 0.002,
      "forecast_next_period": 180000,
      "volatility": 0.08
    }
  },
  "analysis_date": "2024-01-01T00:00:00Z"
}
```

#### GET /analytics/{document_id}/analyses

Get all analyses performed on a document.

**Query Parameters:**
- `analysis_type` (optional): Filter by analysis type

**Response:**
```json
[
  {
    "id": 1,
    "analysis_type": "ratios",
    "results": {...},
    "created_at": "2024-01-01T00:00:00Z",
    "confidence_score": 0.95,
    "validation_status": "validated"
  }
]
```

### 5. Advanced Features

#### POST /analytics/anomaly-detection

Detect anomalies in financial data.

**Request:**
```json
{
  "document_id": 123,
  "time_series_data": {
    "dates": ["2024-01-01", "2024-02-01"],
    "values": [1000000, 1100000]
  }
}
```

**Response:**
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "anomalies_detected": [
    {
      "type": "ratio_anomaly",
      "metric": "current_ratio",
      "value": 0.8,
      "normal_range": [1.0, 3.0],
      "severity": "high",
      "description": "Current ratio of 0.8 is outside normal range (1.0-3.0)"
    }
  ],
  "risk_level": "medium",
  "confidence_score": 0.85,
  "recommendations": [
    "Review financial ratios that are outside normal ranges"
  ]
}
```

#### POST /analytics/scenario-modeling

Create financial scenarios for what-if analysis.

**Request:**
```json
{
  "base_data": {
    "revenue": 1000000,
    "expenses": 800000,
    "assets": 2000000
  },
  "scenario_name": "Revenue Increase 20%",
  "changes": {
    "revenue": 20
  },
  "scenario_type": "sensitivity"
}
```

**Response:**
```json
{
  "scenario_id": "scenario_1",
  "scenario_name": "Revenue Increase 20%",
  "scenario_type": "sensitivity",
  "base_data": {...},
  "changes": {...},
  "modified_data": {...},
  "results": {
    "financial_ratios": {...},
    "key_metrics": {...},
    "cash_flow_impact": {...}
  },
  "impact_analysis": {
    "overall_impact": "positive",
    "risk_assessment": "low",
    "key_changes": ["Revenue change: 20.0%"],
    "recommendations": ["Scenario shows positive impact"]
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /analytics/benchmarking

Benchmark company against industry standards.

**Request:**
```json
{
  "company_data": {
    "company_name": "TechCorp Inc.",
    "revenue": 1000000,
    "net_income": 150000,
    "total_assets": 2000000
  },
  "industry": "technology",
  "company_size": "medium"
}
```

**Response:**
```json
{
  "company_name": "TechCorp Inc.",
  "industry": "technology",
  "company_size": "medium",
  "benchmark_date": "2024-01-01T00:00:00Z",
  "ratios_analysis": {
    "current_ratio": {
      "company_value": 2.5,
      "industry_mean": 2.5,
      "industry_median": 2.2,
      "percentile": 75,
      "performance": "above_average",
      "score": 0.8,
      "interpretation": "Current ratio of 2.5 is above industry average (2.5). Good liquidity position."
    }
  },
  "performance_score": 0.75,
  "rankings": {
    "overall_rank": "good",
    "liquidity_rank": "above_average",
    "profitability_rank": "average"
  },
  "recommendations": [
    "Focus on innovation and R&D investment to maintain competitive advantage"
  ],
  "strengths": [
    "Current Ratio: 2.5 (above industry average)"
  ],
  "weaknesses": []
}
```

#### POST /analytics/report-generation

Generate automated financial reports.

**Request:**
```json
{
  "report_type": "executive_summary",
  "data": {
    "company_name": "TechCorp Inc.",
    "revenue": 1000000,
    "net_income": 150000
  },
  "template": "default",
  "format": "html"
}
```

**Response:**
```json
{
  "report_id": "report_20240101_120000",
  "report_type": "executive_summary",
  "template": "default",
  "format": "html",
  "generated_at": "2024-01-01T00:00:00Z",
  "content": {
    "overview": {
      "title": "Company Overview",
      "content": "TechCorp Inc. is a company with annual revenue of $1,000,000..."
    },
    "key_metrics": {
      "title": "Key Financial Metrics",
      "metrics": [...]
    }
  },
  "charts": [...],
  "tables": [...],
  "summary": {
    "total_sections": 4,
    "key_findings": [...],
    "recommendations_count": 3
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |
| 503 | Service Unavailable - Service temporarily unavailable |

## SDKs and Libraries

### Python SDK
```python
from finmda_bot import FinMDAClient

client = FinMDAClient(api_key="your_api_key")
response = client.upload_document("financial_report.pdf")
```

### JavaScript SDK
```javascript
import { FinMDAClient } from 'finmda-bot-js';

const client = new FinMDAClient({ apiKey: 'your_api_key' });
const response = await client.uploadDocument('financial_report.pdf');
```

## Webhooks

FinMDA-Bot supports webhooks for real-time notifications:

### Document Processing Complete
```json
{
  "event": "document.processing.complete",
  "data": {
    "document_id": 123,
    "status": "completed",
    "processing_time": 5.2
  }
}
```

### Analysis Complete
```json
{
  "event": "analysis.complete",
  "data": {
    "analysis_id": 456,
    "type": "ratios",
    "confidence_score": 0.95
  }
}
```

## Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| Document Upload | 10 requests | 1 hour |
| Chat Queries | 100 requests | 1 hour |
| Analytics | 50 requests | 1 hour |
| Health Check | 1000 requests | 1 hour |

## Support

For API support and questions:
- **Email**: support@finmda-bot.com
- **Documentation**: https://docs.finmda-bot.com
- **Status Page**: https://status.finmda-bot.com
