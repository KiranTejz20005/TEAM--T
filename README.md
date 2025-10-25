# FinMDA-Bot — Financial Multi-Domain AI Assistant

**One-line:** FinMDA-Bot unifies PDFs, Excel/CSV, and market data into an explainable financial analyst you can talk to — auto-extract KPIs, generate MD&A-grade narratives, run scenarios, and produce auditor-ready exports.

---

## 🚀 Project Vision
Financial data lives in many formats (PDFs, spreadsheets, APIs). Analysts spend hours reconciling numbers and writing narrative commentary. FinMDA-Bot solves that by combining document intelligence, tabular analytics, and retrieval-augmented generation into a single conversational UX that delivers explainable, audit-ready insights.

---

## ✨ Highlights — Why FinMDA-Bot stands out
These are the **best, judge-worthy features** to include in an MVP:

### Core features
- **Document Intelligence:** Robust PDF/Excel/CSV parsing, table extraction, and schema validation.
- **KPI Engine:** Compute Revenue Growth, Gross Margin, Net Margin, ROE, EPS, Debt/Equity, Operating Cash Flow Ratio — with traceable source cells.
- **Conversational Interface (“Ask the Report”):** Natural-language Q&A on uploaded datasets and generated narratives.
- **RAG Grounding:** Seeded vector store + retrieval so every factual claim can be supported by a source snippet.
- **Reality Checker (Numeric Validator):** Cross-check every numeric mention against source data; flag discrepancies above threshold.
- **Audit Trail Sentence Provenance:** Click any sentence to view the supporting cell/Doc snippet + confidence score.

### High-impact extensions
- **Peer Benchmarking:** Auto-inject “vs. peers” commentary and percentile ranks.
- **Scenario Builder:** Base/Upside/Downside sliders that regenerate outlook sections with sensitivity tables.
- **Tone Slider:** Re-generate text with a management-tone setting (Conservative → Neutral → Bullish).
- **CFO One-Page Talking Points:** Bullet list + 60-second earnings script for execs.

### Additional capabilities
- DOCX/PDF export with tracked changes + audit package  
- Local LLM fallback (llama.cpp) for offline mode  
- Voice summaries (TTS)  
- Multi-user collaboration & versioning  
- Automated regulatory mapping (SEC Item alignment)

---

## 🧩 System Architecture (conceptual)
