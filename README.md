# FinMDA-Bot — Financial Multi-Domain AI Assistant

**One-line:** FinMDA-Bot unifies PDFs, Excel/CSV, and market data into an explainable financial analyst you can talk to — auto-extract KPIs, generate MD&A-grade narratives, run scenarios, and produce auditor-ready exports.

---

## 🚀 Project Vision
Financial data lives in many formats (PDFs, spreadsheets, APIs). Analysts waste hours reconciling numbers, extracting tables, and writing narrative commentary. FinMDA-Bot solves that by combining document intelligence, tabular analytics, and retrieval-augmented generation into a single conversational UX that delivers explainable, audit-ready insights for analysts, CFOs, auditors, and investors.

---

## 🧾 Problem Statement (clear, concrete, and measurable)
**Primary problem:** Financial professionals must manually collect data from disparate sources (PDF reports, Excel spreadsheets, and market APIs), reconcile conflicting or inconsistent numbers, and then produce narrative commentary (MD&A, investor notes) — a process that is slow, error-prone, and difficult to audit.

**Who is affected:** financial analysts, corporate finance teams, auditors, investor relations professionals, and startup founders preparing investor materials.

**Consequences today:**
- Analysts spend many hours (often 4–12 hours per report) reconciling data and drafting narratives.  
- Reports frequently contain unchecked numeric errors or ambiguous attributions, undermining trust with auditors and investors.  
- Lack of traceability: reviewers cannot easily see which data cells or documents support specific narrative sentences.  
- Limited contextual insights: teams lack quick peer/comparator context and scenario-driven outlooks integrated into the narrative.

**What we aim to fix:**  
- Reduce manual reconciliation and first-draft narrative generation time from hours to minutes.  
- Increase factual accuracy by automatically verifying numeric mentions against source data and surfacing mismatches.  
- Provide sentence-level provenance so every claim is traceable to a specific cell or document snippet.  
- Deliver contextual insights (peers, scenarios, tone-adjusted language) to improve decision-making and investor communication.

**Success criteria / measurable outcomes:**  
- Time-to-first-draft: < 5 minutes from upload → annotated MD&A for a typical 3-sheet dataset.  
- Numeric verification: ≥ 95% of numeric mentions in draft match source data or are flagged with provenance.  
- Evidence coverage: ≥ 80% of factual claims include a linked evidence snippet from the vector store or source files.  
- Usability: reviewers can view provenance for any sentence with ≤ 2 clicks.

**Scope & constraints:**  
- Input formats: PDFs, Excel (.xlsx/.xls), CSVs; optionally market API inputs for peer data.  
- Security: must support a local-processing option for sensitive data (no cloud upload required).  
- Primary output: human-editable MD&A-style narrative, KPI cards, charts, and an audit package (provenance JSON + source files).

---

## ✨ Highlights — Why FinMDA-Bot stands out
These are the best, judge-worthy features to include in an MVP:

### Core features
- **Document Intelligence:** Robust PDF/Excel/CSV parsing, table extraction, and schema validation with clear parsing previews.  
- **KPI Engine:** Compute Revenue Growth, Gross Margin, Net Margin, ROE, EPS, Debt/Equity, Operating Cash Flow Ratio — with traceable source cells and formula transparency.  
- **Conversational Interface (“Ask the Report”):** Natural-language Q&A across uploaded datasets, charts, and generated narratives.  
- **RAG Grounding:** Vectorized historical MD&A/snippets + retrieval so every factual claim can be supported by a source snippet (document id & excerpt).  
- **Reality Checker (Numeric Validator):** Cross-check numeric mentions in generated text against the source dataset and flag discrepancies above a configurable threshold.  
- **Audit Trail Sentence Provenance:** Click any sentence to reveal the supporting cell/CSV row or retrieved snippet, plus a confidence score and retrieval metadata.

### High-impact extensions
- **Peer Benchmarking:** Automatically compute peer percentile ranks and inject “vs. peers” commentary and one-line takeaways.  
- **Scenario Builder:** Base / Upside / Downside scenario sliders to regenerate outlook sections and produce sensitivity tables.  
- **Tone Slider:** Re-generate selected sections with a management-tone control (Conservative → Neutral → Bullish).  
- **CFO One-Page Talking Points:** Auto-generate executive bullets and a 60-second earnings script for investor calls.

### Additional capabilities
- DOCX / PDF export with tracked changes and appended audit package (provenance JSON + sources).  
- Local LLM fallback (e.g., llama.cpp) for offline or air-gapped environments.  
- Voice summaries (TTS) for executive briefings.  
- Multi-user collaboration & versioning with comment threading mapped to sentences and KPIs.  
- Automated regulatory mapping that aligns MD&A sections to SEC items and checklist items.

---

## 🧩 System Architecture (conceptual)
