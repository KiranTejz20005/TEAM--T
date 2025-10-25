"""
MD&A Drafting Pipeline (RAG + Summarization)

This module loads tabular financial statement extracts, computes YoY/QoQ deltas and
KPIs, chunks filings into retrievable text snippets, builds a vector index (Chroma),
and uses Gemini to generate a sectioned MD&A-style draft with citations.

Usage (as a library): import functions from this file in a notebook or script.
Usage (CLI): python mda_pipeline.py --data_dir ./data/ --company "AAPL" --out mda_aapl.md

Requirements:
- pandas, numpy
- chromadb
- sentence-transformers
- google-generativeai (GEMINI_API_KEY in env)

Data expectations:
- CSV extracts with columns including at least: company (or ticker), period/date, concept/tag, value
- Flexible column mapping is supported via function parameters.
"""
from __future__ import annotations

import os
import sys
import json
import argparse
from typing import List, Dict, Any, Optional, Tuple

import pandas as pd
import numpy as np

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

try:
    import google.generativeai as genai
except Exception:  # graceful if not installed
    genai = None

DEFAULT_EMBED_MODEL = "all-MiniLM-L6-v2"

# ----------------------------
# Data Loading & Preparation
# ----------------------------

def load_financials(
    data_dir: str,
    file_pattern: str = "*.csv",
    company_col: str = "company",
    period_col: str = "period",
    concept_col: str = "concept",
    value_col: str = "value",
) -> pd.DataFrame:
    """Load financial statement extracts from a directory of CSV files.

    Returns a normalized DataFrame with columns: company, period, concept, value
    """
    from glob import glob
    all_files = glob(os.path.join(data_dir, file_pattern))
    frames = []
    for fp in all_files:
        try:
            df = pd.read_csv(fp)
            cols = {company_col: "company", period_col: "period", concept_col: "concept", value_col: "value"}
            missing = [k for k in cols if k not in df.columns]
            if missing:
                # Try lowercase guess
                lower_map = {c.lower(): c for c in df.columns}
                cols = {
                    (company_col if company_col in df.columns else lower_map.get(company_col.lower(), company_col)): "company",
                    (period_col if period_col in df.columns else lower_map.get(period_col.lower(), period_col)): "period",
                    (concept_col if concept_col in df.columns else lower_map.get(concept_col.lower(), concept_col)): "concept",
                    (value_col if value_col in df.columns else lower_map.get(value_col.lower(), value_col)): "value",
                }
            sub = df.rename(columns=cols)[["company", "period", "concept", "value"]].copy()
            frames.append(sub)
        except Exception as e:
            print(f"Warning: skipping {fp} due to error: {e}")
    if not frames:
        raise FileNotFoundError(f"No CSV files found under {data_dir} matching {file_pattern}")
    full = pd.concat(frames, ignore_index=True)
    # Clean types
    full["value"] = pd.to_numeric(full["value"], errors="coerce")
    full = full.dropna(subset=["company", "period", "concept"]).reset_index(drop=True)
    return full


def compute_kpis_and_deltas(df: pd.DataFrame, company: Optional[str] = None) -> pd.DataFrame:
    """Compute YoY and QoQ deltas for key concepts and generate KPIs.

    Returns a DataFrame indexed by [company, period] with columns for key metrics
    and YoY/QoQ deltas where possible.
    """
    if company:
        df = df[df["company"] == company].copy()
        if df.empty:
            raise ValueError(f"No rows for company={company}")

    # Choose a few standard concepts (adjust to your dataset naming)
    key_concepts = {
        "Revenue": ["Revenue", "Revenues", "SalesRevenueNet"],
        "GrossProfit": ["GrossProfit"],
        "OperatingIncome": ["OperatingIncome", "OperatingIncomeLoss"],
        "NetIncome": ["NetIncome", "NetIncomeLoss"],
    }

    # Pivot to wide form: rows=(company, period), cols=concepts
    # Use first matching tag per standard concept
    recs = []
    for std, tags in key_concepts.items():
        sub = df[df["concept"].isin(tags)].copy()
        if sub.empty:
            continue
        # If duplicates, take sum by (company, period)
        grp = sub.groupby(["company", "period"], as_index=False)["value"].sum()
        grp["std_concept"] = std
        recs.append(grp)
    if not recs:
        raise ValueError("No key concepts found to compute KPIs")

    merged = (
        pd.concat(recs, ignore_index=True)
        .pivot_table(index=["company", "period"], columns="std_concept", values="value", aggfunc="sum")
        .reset_index()
    )

    # Sort periods lexicographically; if your period is date-like, parse accordingly
    merged = merged.sort_values(["company", "period"]).reset_index(drop=True)

    # Group by company and compute deltas
    def _add_deltas(g: pd.DataFrame) -> pd.DataFrame:
        for col in [c for c in ["Revenue", "GrossProfit", "OperatingIncome", "NetIncome"] if c in g.columns]:
            # QoQ % change
            g[f"{col}_QoQ_pct"] = g[col].pct_change()
            # YoY % change (shift 4 if quarterly labels; adjust if different period granularity)
            g[f"{col}_YoY_pct"] = g[col].pct_change(periods=4)
        # Example KPI: Gross Margin
        if "Revenue" in g.columns and "GrossProfit" in g.columns:
            g["GrossMargin"] = np.where(g["Revenue"].abs() > 1e-9, g["GrossProfit"] / g["Revenue"], np.nan)
        return g

    enriched = merged.groupby("company", group_keys=False).apply(_add_deltas)
    return enriched


# ----------------------------
# Chunking & Indexing (RAG)
# ----------------------------

def build_text_chunks(df: pd.DataFrame, max_rows: int = 2000) -> List[Dict[str, Any]]:
    """Turn rows into brief textual statements with metadata for retrieval.

    Each chunk is a 1-2 sentence summary of the row's metric for a period, suitable for RAG.
    """
    chunks: List[Dict[str, Any]] = []
    df2 = df.head(max_rows).copy()
    for _, row in df2.iterrows():
        company = row.get("company")
        period = row.get("period")
        text_parts = [f"Company: {company}", f"Period: {period}"]
        for col in ["Revenue", "GrossProfit", "OperatingIncome", "NetIncome", "GrossMargin"]:
            if col in df2.columns and pd.notnull(row.get(col)):
                text_parts.append(f"{col}: {row[col]:,.0f}")
        for col in ["Revenue_QoQ_pct", "Revenue_YoY_pct", "GrossProfit_QoQ_pct", "GrossProfit_YoY_pct",
                    "OperatingIncome_QoQ_pct", "OperatingIncome_YoY_pct", "NetIncome_QoQ_pct", "NetIncome_YoY_pct"]:
            if col in df2.columns and pd.notnull(row.get(col)):
                text_parts.append(f"{col}: {row[col]*100:.1f}%")
        text = "; ".join(text_parts)
        chunks.append({
            "id": f"{company}_{period}",
            "text": text,
            "metadata": {"company": company, "period": str(period)},
        })
    return chunks


def build_index(chunks: List[Dict[str, Any]], persist_path: Optional[str] = None) -> Tuple[chromadb.Client, Any]:
    """Create a Chroma collection and upsert chunk embeddings."""
    client = chromadb.PersistentClient(path=persist_path, settings=Settings(anonymized_telemetry=False)) if persist_path else chromadb.Client(Settings(anonymized_telemetry=False))
    collection = client.get_or_create_collection(name="mda_chunks")
    # Embed
    embedder = SentenceTransformer(DEFAULT_EMBED_MODEL)
    texts = [c["text"] for c in chunks]
    embs = embedder.encode(texts, convert_to_numpy=True).tolist()
    ids = [c["id"] for c in chunks]
    metas = [c["metadata"] for c in chunks]
    collection.upsert(ids=ids, documents=texts, metadatas=metas, embeddings=embs)
    return client, collection


def retrieve(collection, query: str, top_k: int = 8) -> Dict[str, Any]:
    """Retrieve top_k chunks for a query."""
    # Use embedder again to get query embedding for better relevance
    embedder = SentenceTransformer(DEFAULT_EMBED_MODEL)
    q_emb = embedder.encode([query], convert_to_numpy=True).tolist()
    res = collection.query(query_embeddings=q_emb, n_results=top_k)
    return res


# ----------------------------
# LLM Summarization (Gemini)
# ----------------------------

def _ensure_gemini():
    if genai is None:
        raise ImportError("google-generativeai is not installed. Please pip install google-generativeai")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not set in environment.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("models/gemini-1.5-flash")


def format_citations(res: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Make a compact citation list from Chroma results."""
    cites: List[Dict[str, Any]] = []
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    for i, (doc, meta) in enumerate(zip(docs, metas)):
        cites.append({
            "index": i + 1,
            "snippet": doc[:200] + ("..." if len(doc) > 200 else ""),
            "company": meta.get("company"),
            "period": meta.get("period"),
        })
    return cites


def draft_section(collection, section_title: str, query: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Retrieve context and ask Gemini to draft a section in markdown with footnote citations."""
    res = retrieve(collection, query, top_k=8)
    cites = format_citations(res)
    context = "\n\n".join(res["documents"][0]) if res.get("documents") else ""
    model = _ensure_gemini()
    prompt = f"""
You are an expert financial analyst drafting the MD&A section: {section_title}.
Use the CONTEXT to write a concise markdown section with bullet points and short paragraphs.
Include footnote-style citations like [^1], [^2] at appropriate claims and list the footnotes at the end of the section.
Keep it factual and grounded in the provided context snippets.

CONTEXT:
{context}

Instructions:
- Structure: A short intro (1-2 sentences), then bullet points for key insights.
- Focus on concrete drivers, notable deltas (YoY/QoQ), and material risks.
- Avoid over-speculation; base claims on context.
- End the section with a "Footnotes" list mapping [^n] to brief source snippet summaries.
"""
    resp = model.generate_content(prompt)
    text = getattr(resp, "text", "") or "(No content generated)"
    # Append footnotes
    foot = [f"[^{c['index']}] {c['company']} | {c['period']} | {c['snippet']}``" for c in cites]
    section = text.strip() + ("\n\nFootnotes\n" + "\n".join(foot) if foot else "")
    return section, cites


def draft_mdna(collection, company: Optional[str] = None) -> str:
    """Produce a full MD&A draft with three sections."""
    sections = []
    s1, _ = draft_section(collection, "Trends & Performance", f"Key trends and YoY/QoQ performance for {company or 'the company'}")
    sections.append(f"# Trends & Performance\n\n{s1}")
    s2, _ = draft_section(collection, "Revenue Drivers", f"Revenue drivers and segment highlights for {company or 'the company'}")
    sections.append(f"# Revenue Drivers\n\n{s2}")
    s3, _ = draft_section(collection, "Risks & Uncertainties", f"Material risks and uncertainties impacting {company or 'the company'}")
    sections.append(f"# Risks & Uncertainties\n\n{s3}")
    return "\n\n---\n\n".join(sections)


# ----------------------------
# CLI Runner
# ----------------------------

def run_cli(args: argparse.Namespace) -> None:
    df_raw = load_financials(
        data_dir=args.data_dir,
        file_pattern=args.file_pattern,
        company_col=args.company_col,
        period_col=args.period_col,
        concept_col=args.concept_col,
        value_col=args.value_col,
    )
    df_kpi = compute_kpis_and_deltas(df_raw, company=args.company)
    chunks = build_text_chunks(df_kpi)
    _, coll = build_index(chunks, persist_path=args.persist)
    md = draft_mdna(coll, company=args.company)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"MD&A draft written to {args.out}")
    else:
        print(md)


def main():
    p = argparse.ArgumentParser(description="Automated MD&A Draft (RAG + Summarization)")
    p.add_argument("--data_dir", required=True, help="Directory containing CSV extracts")
    p.add_argument("--file_pattern", default="*.csv", help="Glob pattern for input CSV files")
    p.add_argument("--company", default=None, help="Filter to a single company (optional)")
    p.add_argument("--company_col", default="company")
    p.add_argument("--period_col", default="period")
    p.add_argument("--concept_col", default="concept")
    p.add_argument("--value_col", default="value")
    p.add_argument("--persist", default=None, help="Chroma persistence directory (optional)")
    p.add_argument("--out", default=None, help="Output markdown path (optional)")
    args = p.parse_args()
    run_cli(args)


if __name__ == "__main__":
    main()
