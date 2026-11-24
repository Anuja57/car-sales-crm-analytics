# React + FastAPI Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the CRM Analytics project into `backend/` (FastAPI + ML pipeline) and `frontend/` (React + Recharts), replacing the Streamlit app while keeping all three dashboards and AI insights.

**Architecture:** FastAPI exposes a single `POST /api/analyze` endpoint that accepts three CSV uploads and returns all ML results as JSON, plus three `POST /api/insights/{dashboard}` endpoints that proxy to Claude. React consumes these endpoints, renders Recharts visualisations, and manages all UI state client-side.

**Tech Stack:** FastAPI · Uvicorn · pandas · scikit-learn · anthropic · React 18 · Vite · Tailwind CSS v3 · Recharts · Axios

---

## File Map

### Backend (`backend/`)
| File | Responsibility |
|---|---|
| `backend/main.py` | FastAPI app, CORS, `/api/analyze`, `/api/insights/{dashboard}` |
| `backend/serializer.py` | `NumpyEncoder`, `df_to_records()`, `safe_dict()` helpers |
| `backend/requirements.txt` | Python dependencies |
| `backend/pipeline/__init__.py` | Package marker |
| `backend/pipeline/data_loader.py` | Copied from root — accepts file-like objects |
| `backend/pipeline/data_cleaner.py` | Copied from root |
| `backend/pipeline/ml_engine.py` | Copied from root |
| `backend/pipeline/ai_insights.py` | Adapted — prompt builders receive plain dicts, not DataFrames |
| `backend/utils/__init__.py` | Package marker |
| `backend/utils/helpers.py` | Copied from root |

### Frontend (`frontend/`)
| File | Responsibility |
|---|---|
| `frontend/package.json` | Dependencies (react, recharts, axios, tailwind) |
| `frontend/vite.config.js` | Vite config with `/api` proxy to `localhost:8000` |
| `frontend/tailwind.config.js` | Tailwind content paths + custom colours |
| `frontend/postcss.config.js` | PostCSS for Tailwind |
| `frontend/index.html` | HTML shell + Poppins font import |
| `frontend/src/main.jsx` | React root mount |
| `frontend/src/App.jsx` | Layout: sidebar + header + tab router + analysis trigger |
| `frontend/src/api/client.js` | `analyzeFiles(f1,f2,f3)` and `getInsights(dashboard, metrics, apiKey)` |
| `frontend/src/components/FileSlot.jsx` | Single upload slot: shows uploader or filename badge + X |
| `frontend/src/components/KPICard.jsx` | White card with blue top accent, label, value, delta |
| `frontend/src/components/ChartCard.jsx` | Titled white card wrapping any Recharts chart |
| `frontend/src/components/AIInsightPanel.jsx` | "Generate Insights" button + rendered insight text |
| `frontend/src/pages/AgentPerformance.jsx` | KPIs + 5 charts + leaderboard table + AI insights |
| `frontend/src/pages/CustomerConnectivity.jsx` | KPIs + 5 charts + detail table + AI insights |
| `frontend/src/pages/LeadConversion.jsx` | KPIs + funnel + 6 charts + top leads table + AI insights |
| `frontend/src/pages/EdaSummary.jsx` | Missing-data bars per file |

---

## Task 1: Backend — directory scaffold + serialiser

**Files:**
- Create: `backend/serializer.py`
- Create: `backend/requirements.txt`
- Create: `backend/pipeline/__init__.py`
- Create: `backend/utils/__init__.py`

- [ ] **Step 1: Create directory tree**

```bash
mkdir -p backend/pipeline backend/utils
```

- [ ] **Step 2: Write `backend/requirements.txt`**

```
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
python-multipart>=0.0.9
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
anthropic>=0.20.0
python-dotenv>=1.0.0
```

- [ ] **Step 3: Write `backend/serializer.py`**

```python
import json
import numpy as np
import pandas as pd


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, pd.Timestamp):
            return str(obj)
        return super().default(obj)


def df_to_records(df: pd.DataFrame) -> list:
    """Convert DataFrame to JSON-safe list of dicts."""
    return json.loads(json.dumps(df.to_dict("records"), cls=NumpyEncoder))


def safe_dict(d: dict) -> dict:
    """Recursively make a dict JSON-safe."""
    return json.loads(json.dumps(d, cls=NumpyEncoder))
```

- [ ] **Step 4: Create empty `__init__.py` files**

```bash
touch backend/pipeline/__init__.py backend/utils/__init__.py
```

- [ ] **Step 5: Verify serialiser works**

```bash
cd backend
python -c "
from serializer import df_to_records, safe_dict
import pandas as pd, numpy as np
df = pd.DataFrame({'a': [np.int64(1)], 'b': [np.float32(2.5)]})
print(df_to_records(df))   # [{'a': 1, 'b': 2.5}]
print(safe_dict({'x': np.float64(3.14)}))  # {'x': 3.14}
"
```

Expected output:
```
[{'a': 1, 'b': 2.5}]
{'x': 3.14}
```

---

## Task 2: Backend — copy pipeline & utils

**Files:**
- Create: `backend/pipeline/data_loader.py`
- Create: `backend/pipeline/data_cleaner.py`
- Create: `backend/pipeline/ml_engine.py`
- Create: `backend/utils/helpers.py`

- [ ] **Step 1: Copy files**

```bash
cp pipeline/data_loader.py  backend/pipeline/data_loader.py
cp pipeline/data_cleaner.py backend/pipeline/data_cleaner.py
cp pipeline/ml_engine.py    backend/pipeline/ml_engine.py
cp utils/helpers.py         backend/utils/helpers.py
```

- [ ] **Step 2: Fix import paths in copied files**

In `backend/pipeline/data_cleaner.py`, change:
```python
from utils.helpers import label_model, label_source, label_agent
```

In `backend/pipeline/ml_engine.py` — no import changes needed (no utils import).

- [ ] **Step 3: Verify pipeline imports from backend/**

```bash
cd backend
python -c "
import sys; sys.path.insert(0,'.')
from pipeline.data_loader import load_data
from pipeline.data_cleaner import clean_leads, clean_calls, clean_testdrives
from pipeline.ml_engine import analyze_agent_performance, analyze_customer_connectivity, analyze_lead_conversion
print('All imports OK')
"
```

Expected: `All imports OK`

---

## Task 3: Backend — adapt ai_insights.py

**Files:**
- Create: `backend/pipeline/ai_insights.py`

The original `ai_insights.py` takes DataFrames. The API version receives plain dicts/lists (already serialised). Rewrite prompt-builders to accept these.

- [ ] **Step 1: Write `backend/pipeline/ai_insights.py`**

```python
"""AI Insights — prompt builders that accept plain dicts (no DataFrames)."""

import os
import anthropic

MODEL = "claude-sonnet-4-6"


def _ask(prompt: str) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not set.")
    client = anthropic.Anthropic(api_key=key)
    msg = client.messages.create(
        model=MODEL,
        max_tokens=900,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def get_agent_insights(metrics: list, tier_dist: dict, avg_score: float) -> str:
    sorted_m = sorted(metrics, key=lambda x: x.get("rank", 99))
    top3 = sorted_m[:3]
    bottom3 = sorted_m[-3:]

    def fmt(rows):
        return "\n".join(
            f"  {r['agent_name']}: score={r['composite_score']}, "
            f"calls={r['total_calls']}, hot%={r['hot_lead_ratio']}, "
            f"callback%={r['callback_rate']}, tier={r['tier']}"
            for r in rows
        )

    prompt = f"""You are an automotive CRM analytics expert.
Below are agent performance metrics (car sales team):

TOP 3 AGENTS:
{fmt(top3)}

BOTTOM 3 AGENTS:
{fmt(bottom3)}

OVERALL STATS:
- Average composite score: {avg_score:.1f}/100
- Tier distribution: {tier_dist}
- Total agents analysed: {len(metrics)}

Write a concise EXECUTIVE INSIGHT (max 200 words) covering:
1. **Key Strengths** - what top agents are doing well
2. **Improvement Areas** - patterns in low-performing agents
3. **Action Recommendations** - 3 specific, practical steps to raise team performance

Use plain language. Audience is non-technical sales managers.
Format with short bullet points under each heading."""
    return _ask(prompt)


def get_connectivity_insights(segments: dict, avg_calls: float,
                               avg_cb_rate: float, lead_type_dist: list) -> str:
    ltd = {r["lead_type"]: r["count"] for r in lead_type_dist}
    total = sum(ltd.values()) or 1
    hot_pct = round(ltd.get("Hot", 0) / total * 100, 1)

    prompt = f"""You are an automotive CRM analytics expert.
Below are customer connectivity metrics:

CUSTOMER ENGAGEMENT SEGMENTS: {segments}
KEY METRICS:
- Average calls per customer: {avg_calls:.2f}
- Average callback scheduling rate: {avg_cb_rate:.1f}%
- Lead type distribution: {ltd}
- Hot lead percentage: {hot_pct}%

Write a concise EXECUTIVE INSIGHT (max 200 words) covering:
1. **Connectivity Health** - how well the team is engaging with customers
2. **Risk Signals** - segments or patterns showing poor connectivity
3. **Action Recommendations** - 3 specific steps to improve customer engagement

Use plain language. Audience is non-technical sales managers.
Format with short bullet points under each heading."""
    return _ask(prompt)


def get_conversion_insights(funnel: dict, source_stats: list,
                             model_stats: list, score_tiers: dict) -> str:
    total = funnel.get("Total Leads", 0)
    converted = funnel.get("Converted / Closed", 0)
    conv_rate = round(converted / total * 100, 1) if total else 0

    top_src = sorted(source_stats, key=lambda x: x.get("conversion_rate", 0), reverse=True)[:3]
    top_mdl = sorted(model_stats, key=lambda x: x.get("total", 0), reverse=True)[:3]

    prompt = f"""You are an automotive CRM analytics expert.
Below are lead conversion metrics for a car dealership:

FUNNEL:
- Total Leads: {total}
- Converted/Closed: {converted} ({conv_rate}%)
- High-Potential Remaining: {funnel.get("High Potential (Remaining)", 0)}

LEAD SCORE TIERS: {score_tiers}

TOP CONVERTING SOURCES:
{chr(10).join(f"  {s['source_name']}: {s['conversion_rate']}% ({s['total']} leads)" for s in top_src)}

TOP MODELS BY INTEREST:
{chr(10).join(f"  {m['model_name']}: {m['total']} leads, {m['conversion_rate']}% converted" for m in top_mdl)}

Write a concise EXECUTIVE INSIGHT (max 200 words) covering:
1. **Conversion Performance** - how the funnel is performing
2. **Biggest Opportunities** - where highest-potential leads come from
3. **Action Recommendations** - 3 specific steps to increase lead conversion

Use plain language. Audience is non-technical sales managers.
Format with short bullet points under each heading."""
    return _ask(prompt)
```

---

## Task 4: Backend — FastAPI main.py

**Files:**
- Create: `backend/main.py`

- [ ] **Step 1: Write `backend/main.py`**

```python
"""FastAPI backend for CRM Analytics AI."""

import sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

from pipeline.data_loader   import load_data
from pipeline.data_cleaner  import clean_leads, clean_calls, clean_testdrives
from pipeline.ml_engine     import (analyze_agent_performance,
                                    analyze_customer_connectivity,
                                    analyze_lead_conversion)
from pipeline.ai_insights   import (get_agent_insights,
                                    get_connectivity_insights,
                                    get_conversion_insights)
from serializer import df_to_records, safe_dict

app = FastAPI(title="CRM Analytics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/analyze")
async def analyze(
    leads_file: UploadFile = File(...),
    calls_file: UploadFile = File(...),
    td_file:    UploadFile = File(...),
):
    try:
        leads_raw, calls_raw, td_raw, load_info = load_data(
            leads_file.file, calls_file.file, td_file.file
        )
        leads_clean, leads_eda = clean_leads(leads_raw)
        calls_clean, calls_eda = clean_calls(calls_raw)
        td_clean,    td_eda    = clean_testdrives(td_raw)

        agent_r = analyze_agent_performance(calls_clean, td_clean)
        conn_r  = analyze_customer_connectivity(calls_clean)
        conv_r  = analyze_lead_conversion(leads_clean, calls_clean)

        # Connectivity: add connectivity_score distribution
        cust = conn_r["customer_metrics"]
        score_dist = cust["connectivity_score"].round(0).astype(int).value_counts().sort_index()

        return {
            "load_info": load_info,
            "agent": {
                "metrics": df_to_records(agent_r["agent_metrics"]),
            },
            "connectivity": {
                "segments":      safe_dict(cust["segment"].value_counts().to_dict()),
                "avg_calls":     float(cust["total_calls"].mean()),
                "avg_cb_rate":   float(cust["callback_rate"].mean()),
                "time_series":   df_to_records(
                    conn_r["time_series"].assign(
                        call_date=conn_r["time_series"]["call_date"].astype(str)
                    )
                ),
                "location_stats":  df_to_records(conn_r["location_stats"]),
                "lead_type_dist":  df_to_records(conn_r["lead_type_dist"]),
                "model_interest":  df_to_records(
                    cust["models_interest"].value_counts().reset_index()
                    .rename(columns={"models_interest": "model", "count": "customers"})
                    .head(10)
                ),
            },
            "conversion": {
                "funnel":             safe_dict(conv_r["funnel"]),
                "source_stats":       df_to_records(conv_r["source_stats"]),
                "model_stats":        df_to_records(conv_r["model_stats"]),
                "feature_importance": safe_dict(
                    {k: float(v) for k, v in conv_r["feature_importance"].items()}
                ),
                "score_tiers":  safe_dict(
                    conv_r["leads_scored"]["score_tier"].value_counts().to_dict()
                ),
                "status_dist":  safe_dict(
                    conv_r["leads_scored"]["status_label"].value_counts().to_dict()
                ),
                "td_dist":      safe_dict(
                    conv_r["leads_scored"]["td_status_label"].value_counts().to_dict()
                ),
                "top_leads":    df_to_records(
                    conv_r["leads_scored"][
                        (conv_r["leads_scored"]["score_tier"] == "High Potential") &
                        (conv_r["leads_scored"]["converted"] == 0)
                    ].nlargest(20, "conversion_prob")[[
                        "id", "model_name", "source_name", "lead_type_label",
                        "td_status_label", "lead_age_days", "conversion_prob", "score_tier",
                    ]]
                ),
                "prob_dist":    df_to_records(
                    conv_r["leads_scored"][["conversion_prob", "score_tier"]]
                ),
            },
            "eda": {
                "leads":       {k: v for k, v in leads_eda.items() if k != "numeric_stats"},
                "calls":       {k: v for k, v in calls_eda.items() if k != "numeric_stats"},
                "testdrives":  {k: v for k, v in td_eda.items()    if k != "numeric_stats"},
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Insight request bodies ────────────────────────────────────────────────────

class AgentInsightRequest(BaseModel):
    api_key:   str
    metrics:   list
    tier_dist: dict
    avg_score: float

class ConnInsightRequest(BaseModel):
    api_key:       str
    segments:      dict
    avg_calls:     float
    avg_cb_rate:   float
    lead_type_dist: list

class ConvInsightRequest(BaseModel):
    api_key:     str
    funnel:      dict
    source_stats: list
    model_stats:  list
    score_tiers:  dict


@app.post("/api/insights/agent")
async def agent_insights(body: AgentInsightRequest):
    os.environ["ANTHROPIC_API_KEY"] = body.api_key
    try:
        text = get_agent_insights(body.metrics, body.tier_dist, body.avg_score)
        return {"insight": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/insights/connectivity")
async def connectivity_insights(body: ConnInsightRequest):
    os.environ["ANTHROPIC_API_KEY"] = body.api_key
    try:
        text = get_connectivity_insights(
            body.segments, body.avg_calls, body.avg_cb_rate, body.lead_type_dist
        )
        return {"insight": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/insights/conversion")
async def conversion_insights(body: ConvInsightRequest):
    os.environ["ANTHROPIC_API_KEY"] = body.api_key
    try:
        text = get_conversion_insights(
            body.funnel, body.source_stats, body.model_stats, body.score_tiers
        )
        return {"insight": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

- [ ] **Step 2: Install backend deps and smoke-test**

```bash
cd backend
pip install -r requirements.txt
python -c "from main import app; print('FastAPI app OK')"
```

Expected: `FastAPI app OK`

- [ ] **Step 3: Start the server**

```bash
cd backend
python main.py
```

Expected in terminal:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Task 5: Frontend — Vite + React scaffold

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/index.html`

- [ ] **Step 1: Write `frontend/package.json`**

```json
{
  "name": "crm-analytics-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev":   "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react":       "^18.3.1",
    "react-dom":   "^18.3.1",
    "recharts":    "^2.12.7",
    "axios":       "^1.7.2"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer":  "^10.4.19",
    "postcss":       "^8.4.38",
    "tailwindcss":   "^3.4.4",
    "vite":          "^5.3.1"
  }
}
```

- [ ] **Step 2: Write `frontend/vite.config.js`**

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

- [ ] **Step 3: Write `frontend/tailwind.config.js`**

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Poppins', 'sans-serif'],
      },
      colors: {
        mint:  { DEFAULT: 'rgb(240,253,244)', dark: 'rgb(220,252,231)' },
        brand: { DEFAULT: '#1D4ED8', dark: '#1E40AF' },
      },
    },
  },
  plugins: [],
}
```

- [ ] **Step 4: Write `frontend/postcss.config.js`**

```js
export default {
  plugins: { tailwindcss: {}, autoprefixer: {} },
}
```

- [ ] **Step 5: Write `frontend/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>CRM Analytics AI</title>
    <link
      href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap"
      rel="stylesheet"
    />
  </head>
  <body class="bg-slate-100 font-sans">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

- [ ] **Step 6: Install and verify scaffold**

```bash
cd frontend
npm install
npm run dev
```

Expected: Vite dev server starts at `http://localhost:5173` (blank page is fine at this point).

---

## Task 6: Frontend — API client + base files

**Files:**
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/index.css`
- Create: `frontend/src/api/client.js`

- [ ] **Step 1: Write `frontend/src/main.jsx`**

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

- [ ] **Step 2: Write `frontend/src/index.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 3: Write `frontend/src/api/client.js`**

```js
import axios from 'axios'

export async function analyzeFiles(leadsFile, callsFile, tdFile) {
  const form = new FormData()
  form.append('leads_file', leadsFile)
  form.append('calls_file', callsFile)
  form.append('td_file',    tdFile)
  const { data } = await axios.post('/api/analyze', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function getAgentInsights(metrics, tierDist, avgScore, apiKey) {
  const { data } = await axios.post('/api/insights/agent', {
    api_key:   apiKey,
    metrics,
    tier_dist: tierDist,
    avg_score: avgScore,
  })
  return data.insight
}

export async function getConnectivityInsights(segments, avgCalls, avgCbRate, leadTypeDist, apiKey) {
  const { data } = await axios.post('/api/insights/connectivity', {
    api_key:        apiKey,
    segments,
    avg_calls:      avgCalls,
    avg_cb_rate:    avgCbRate,
    lead_type_dist: leadTypeDist,
  })
  return data.insight
}

export async function getConversionInsights(funnel, sourceStats, modelStats, scoreTiers, apiKey) {
  const { data } = await axios.post('/api/insights/conversion', {
    api_key:      apiKey,
    funnel,
    source_stats: sourceStats,
    model_stats:  modelStats,
    score_tiers:  scoreTiers,
  })
  return data.insight
}
```

---

## Task 7: Frontend — shared components

**Files:**
- Create: `frontend/src/components/FileSlot.jsx`
- Create: `frontend/src/components/KPICard.jsx`
- Create: `frontend/src/components/ChartCard.jsx`
- Create: `frontend/src/components/AIInsightPanel.jsx`

- [ ] **Step 1: Write `frontend/src/components/FileSlot.jsx`**

```jsx
import { useRef } from 'react'

export default function FileSlot({ label, file, onSelect, onRemove }) {
  const inputRef = useRef()

  if (file) {
    return (
      <div className="mb-4">
        <p className="text-xs font-semibold text-green-800 uppercase tracking-wide mb-1">{label}</p>
        <div className="flex items-center">
          <div
            className="flex-1 bg-green-100 border border-green-200 rounded-l px-3 py-1.5
                        text-xs font-medium text-green-800 truncate"
            title={file.name}
          >
            {file.name}
          </div>
          <button
            onClick={onRemove}
            className="bg-green-100 border border-green-200 border-l-0 rounded-r
                       px-2.5 py-1.5 text-green-800 font-bold hover:bg-green-200
                       text-xs leading-none"
          >
            x
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="mb-4">
      <label className="block text-xs font-semibold text-green-800 uppercase tracking-wide mb-1">
        {label}
      </label>
      <button
        onClick={() => inputRef.current.click()}
        className="w-full border-2 border-dashed border-green-300 rounded px-3 py-2
                   text-xs text-green-700 hover:border-green-500 hover:bg-green-50
                   transition-colors text-left"
      >
        Click to upload CSV
      </button>
      <input
        ref={inputRef}
        type="file"
        accept=".csv"
        className="hidden"
        onChange={e => e.target.files[0] && onSelect(e.target.files[0])}
      />
    </div>
  )
}
```

- [ ] **Step 2: Write `frontend/src/components/KPICard.jsx`**

```jsx
export default function KPICard({ label, value, delta }) {
  return (
    <div className="bg-white border border-slate-200 border-t-[3px] border-t-blue-600
                    rounded p-4 min-h-[96px]">
      <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-widest mb-1.5">
        {label}
      </p>
      <p className="text-2xl font-bold text-slate-900 tracking-tight">{value}</p>
      {delta && <p className="text-xs text-slate-500 mt-1">{delta}</p>}
    </div>
  )
}
```

- [ ] **Step 3: Write `frontend/src/components/ChartCard.jsx`**

```jsx
export default function ChartCard({ title, children, className = '' }) {
  return (
    <div className={`bg-white border border-slate-200 rounded p-4 ${className}`}>
      {title && (
        <h3 className="text-[11px] font-semibold text-slate-500 uppercase tracking-widest mb-4">
          {title}
        </h3>
      )}
      {children}
    </div>
  )
}
```

- [ ] **Step 4: Write `frontend/src/components/AIInsightPanel.jsx`**

```jsx
import { useState } from 'react'

export default function AIInsightPanel({ apiKey, onGenerate, cachedInsight }) {
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  async function handleGenerate() {
    setLoading(true)
    setError(null)
    try {
      await onGenerate()
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mt-6">
      <hr className="border-slate-200 mb-6" />
      <h3 className="text-[11px] font-semibold text-slate-500 uppercase tracking-widest mb-4">
        AI-Generated Executive Insights
      </h3>

      {!apiKey && (
        <p className="text-sm text-slate-500 bg-slate-50 border border-slate-200 rounded px-4 py-3">
          Enter your Anthropic API key in the sidebar to unlock AI insights.
        </p>
      )}

      {apiKey && !cachedInsight && (
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded
                     hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Generating...' : 'Generate AI Insights'}
        </button>
      )}

      {error && (
        <p className="text-sm text-red-600 mt-2">{error}</p>
      )}

      {cachedInsight && (
        <div
          className="bg-white border border-slate-200 border-l-[3px] border-l-blue-600
                     rounded p-6 text-sm text-slate-700 leading-7 whitespace-pre-wrap"
        >
          {cachedInsight}
        </div>
      )}
    </div>
  )
}
```

---

## Task 8: Frontend — Agent Performance page

**Files:**
- Create: `frontend/src/pages/AgentPerformance.jsx`

- [ ] **Step 1: Write `frontend/src/pages/AgentPerformance.jsx`**

```jsx
import { useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell, ScatterChart, Scatter, ZAxis, ResponsiveContainer,
} from 'recharts'
import KPICard     from '../components/KPICard'
import ChartCard   from '../components/ChartCard'
import AIInsightPanel from '../components/AIInsightPanel'
import { getAgentInsights } from '../api/client'

const TIER_COLORS = { High: '#16A34A', Medium: '#D97706', Low: '#DC2626' }
const PALETTE = ['#2563EB','#16A34A','#D97706','#DC2626','#7C3AED',
                  '#0891B2','#DB2777','#65A30D','#EA580C','#6366F1','#14B8A6']

export default function AgentPerformance({ data, apiKey }) {
  const [insight, setInsight] = useState(null)
  const metrics = data.metrics

  const topAgent    = metrics[0]
  const avgScore    = (metrics.reduce((s, m) => s + m.composite_score, 0) / metrics.length).toFixed(1)
  const highCount   = metrics.filter(m => m.tier === 'High').length
  const totalCalls  = metrics.reduce((s, m) => s + m.total_calls, 0)
  const tierDist    = metrics.reduce((acc, m) => { acc[m.tier] = (acc[m.tier] || 0) + 1; return acc }, {})
  const tierData    = Object.entries(tierDist).map(([name, value]) => ({ name, value }))

  const ltData = metrics.map(m => ({
    name: m.agent_name,
    Hot:  m.hot_leads,
    Warm: m.warm_leads,
    Cold: m.cold_leads,
  }))

  async function generateInsight() {
    const text = await getAgentInsights(metrics, tierDist, parseFloat(avgScore), apiKey)
    setInsight(text)
  }

  return (
    <div>
      <h2 className="text-xl font-bold text-slate-900 mb-1">Agent Performance Analysis</h2>
      <p className="text-sm text-slate-500 mb-6">
        K-Means clustering ranks agents by call volume, lead quality, callback rate and test-drive outcomes.
      </p>

      {/* KPIs */}
      <div className="grid grid-cols-5 gap-4 mb-6">
        <KPICard label="Total Agents"          value={metrics.length} />
        <KPICard label="Total Calls Analysed"  value={totalCalls.toLocaleString()} />
        <KPICard label="Top Performer"         value={topAgent?.agent_name} />
        <KPICard label="Avg Performance Score" value={`${avgScore}/100`} />
        <KPICard label="High-Tier Agents"      value={`${highCount}/${metrics.length}`} />
      </div>

      {/* Score ranking + tier pie */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <ChartCard title="Agent Performance Score Ranking">
          <ResponsiveContainer width="100%" height={320}>
            <BarChart
              data={[...metrics].sort((a,b) => a.composite_score - b.composite_score)}
              layout="vertical" margin={{ left: 20, right: 30 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
              <YAxis dataKey="agent_name" type="category" width={90} tick={{ fontSize: 11 }} />
              <Tooltip formatter={v => [`${v}/100`, 'Score']} />
              <Bar dataKey="composite_score" radius={[0,3,3,0]}>
                {metrics.map((m, i) => (
                  <Cell key={i} fill={TIER_COLORS[m.tier] || '#2563EB'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Performance Tier Distribution">
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Pie data={tierData} dataKey="value" nameKey="name"
                   cx="50%" cy="50%" innerRadius={70} outerRadius={110}
                   label={({ name, percent }) => `${name} ${(percent*100).toFixed(0)}%`}
              >
                {tierData.map((e, i) => (
                  <Cell key={i} fill={TIER_COLORS[e.name] || '#94A3B8'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Calls + callback rate */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <ChartCard title="Calls Handled per Agent">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={[...metrics].sort((a,b) => b.total_calls - a.total_calls)}
                      margin={{ bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="agent_name" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="total_calls" name="Calls" radius={[3,3,0,0]}>
                {metrics.map((m, i) => <Cell key={i} fill={TIER_COLORS[m.tier] || '#2563EB'} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Callback Scheduling Rate (%)">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={[...metrics].sort((a,b) => b.callback_rate - a.callback_rate)}
                      margin={{ bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="agent_name" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={v => [`${v}%`, 'Callback Rate']} />
              <Bar dataKey="callback_rate" name="Callback %" radius={[3,3,0,0]}>
                {metrics.map((m, i) => <Cell key={i} fill={TIER_COLORS[m.tier] || '#2563EB'} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Lead type stacked */}
      <ChartCard title="Lead Type Handled per Agent" className="mb-4">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={ltData} margin={{ bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="Hot"  stackId="a" fill="#DC2626" radius={[0,0,0,0]} />
            <Bar dataKey="Warm" stackId="a" fill="#D97706" />
            <Bar dataKey="Cold" stackId="a" fill="#2563EB" radius={[3,3,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* Leaderboard table */}
      <ChartCard title="Agent Leaderboard" className="mb-4 overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-slate-200">
              {['Rank','Agent','Tier','Score','Calls','Hot Lead %','Callback %','Test Drives','TD Completion %'].map(h => (
                <th key={h} className="text-left py-2 px-2 font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {metrics.map((m, i) => {
              const bg = { High: 'bg-green-50', Medium: 'bg-yellow-50', Low: 'bg-red-50' }[m.tier] || ''
              return (
                <tr key={i} className={`border-b border-slate-100 ${bg}`}>
                  <td className="py-1.5 px-2 font-bold">{m.rank}</td>
                  <td className="py-1.5 px-2 font-medium">{m.agent_name}</td>
                  <td className="py-1.5 px-2">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold
                      ${ m.tier==='High'?'bg-green-100 text-green-800':
                         m.tier==='Medium'?'bg-yellow-100 text-yellow-800':
                         'bg-red-100 text-red-800'}`}>
                      {m.tier}
                    </span>
                  </td>
                  <td className="py-1.5 px-2">{m.composite_score}</td>
                  <td className="py-1.5 px-2">{m.total_calls}</td>
                  <td className="py-1.5 px-2">{m.hot_lead_ratio}%</td>
                  <td className="py-1.5 px-2">{m.callback_rate}%</td>
                  <td className="py-1.5 px-2">{m.test_drives_assigned}</td>
                  <td className="py-1.5 px-2">{m.td_conversion_rate}%</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </ChartCard>

      <AIInsightPanel apiKey={apiKey} onGenerate={generateInsight} cachedInsight={insight} />
    </div>
  )
}
```

---

## Task 9: Frontend — Customer Connectivity page

**Files:**
- Create: `frontend/src/pages/CustomerConnectivity.jsx`

- [ ] **Step 1: Write `frontend/src/pages/CustomerConnectivity.jsx`**

```jsx
import { useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell,
  ComposedChart, Line,
  ResponsiveContainer,
} from 'recharts'
import KPICard        from '../components/KPICard'
import ChartCard      from '../components/ChartCard'
import AIInsightPanel from '../components/AIInsightPanel'
import { getConnectivityInsights } from '../api/client'

const SEG_COLORS  = { 'Highly Engaged': '#16A34A', 'Moderately Engaged': '#D97706', 'Low Engagement': '#DC2626' }
const TYPE_COLORS = { Hot: '#DC2626', Warm: '#D97706', Cold: '#2563EB', Unknown: '#94A3B8' }

export default function CustomerConnectivity({ data, apiKey }) {
  const [insight, setInsight] = useState(null)
  const { segments, avg_calls, avg_cb_rate, time_series, location_stats, lead_type_dist, model_interest } = data

  const segData  = Object.entries(segments).map(([name, value]) => ({ name, value }))
  const totalLTD = lead_type_dist.reduce((s, r) => s + r.count, 0)
  const hotPct   = ((lead_type_dist.find(r => r.lead_type === 'Hot')?.count || 0) / (totalLTD || 1) * 100).toFixed(1)
  const highlyEngaged = segments['Highly Engaged'] || 0

  async function generateInsight() {
    const text = await getConnectivityInsights(segments, avg_calls, avg_cb_rate, lead_type_dist, apiKey)
    setInsight(text)
  }

  return (
    <div>
      <h2 className="text-xl font-bold text-slate-900 mb-1">Customer Connectivity Analysis</h2>
      <p className="text-sm text-slate-500 mb-6">
        Evaluates customer engagement using call frequency, callback rates and lead quality signals.
      </p>

      <div className="grid grid-cols-5 gap-4 mb-6">
        <KPICard label="Unique Customers"   value={Object.values(segments).reduce((s,v)=>s+v,0).toLocaleString()} />
        <KPICard label="Avg Calls/Customer" value={avg_calls.toFixed(1)} />
        <KPICard label="Avg Callback Rate"  value={`${avg_cb_rate.toFixed(1)}%`} />
        <KPICard label="Highly Engaged"     value={highlyEngaged} />
        <KPICard label="Hot Lead Share"     value={`${hotPct}%`} />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <ChartCard title="Customer Engagement Segments">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={segData} dataKey="value" nameKey="name"
                   cx="50%" cy="50%" innerRadius={65} outerRadius={105}
                   label={({ name, percent }) => `${name.split(' ')[0]} ${(percent*100).toFixed(0)}%`}
              >
                {segData.map((e, i) => <Cell key={i} fill={SEG_COLORS[e.name] || '#94A3B8'} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Lead Type Distribution (Calls)">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={lead_type_dist} dataKey="count" nameKey="lead_type"
                   cx="50%" cy="50%" innerRadius={65} outerRadius={105}
                   label={({ lead_type, percent }) => `${lead_type} ${(percent*100).toFixed(0)}%`}
              >
                {lead_type_dist.map((e, i) => <Cell key={i} fill={TYPE_COLORS[e.lead_type] || '#94A3B8'} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <ChartCard title="Daily Call Volume and Lead Type Trend" className="mb-4">
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={time_series}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="call_date" tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="cold_calls"  stackId="a" fill="#93C5FD" name="Cold" />
            <Bar dataKey="warm_calls"  stackId="a" fill="#FCD34D" name="Warm" />
            <Bar dataKey="hot_calls"   stackId="a" fill="#F87171" name="Hot" radius={[3,3,0,0]} />
            <Line dataKey="call_count" stroke="#1E40AF" strokeWidth={2.5} dot={{ r: 4 }} name="Total" />
          </ComposedChart>
        </ResponsiveContainer>
      </ChartCard>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <ChartCard title="Call Volume by Showroom Location">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={location_stats.slice(0,10)} margin={{ bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="location_label" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="calls" fill="#2563EB" radius={[3,3,0,0]} name="Calls" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Customer Interest by Car Model">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={model_interest} margin={{ bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="model" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="customers" fill="#0891B2" radius={[3,3,0,0]} name="Customers" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <AIInsightPanel apiKey={apiKey} onGenerate={generateInsight} cachedInsight={insight} />
    </div>
  )
}
```

---

## Task 10: Frontend — Lead Conversion page

**Files:**
- Create: `frontend/src/pages/LeadConversion.jsx`

- [ ] **Step 1: Write `frontend/src/pages/LeadConversion.jsx`**

```jsx
import { useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell,
  FunnelChart, Funnel, LabelList,
  ScatterChart, Scatter, ZAxis,
  ResponsiveContainer,
} from 'recharts'
import KPICard        from '../components/KPICard'
import ChartCard      from '../components/ChartCard'
import AIInsightPanel from '../components/AIInsightPanel'
import { getConversionInsights } from '../api/client'

const TIER_COLORS = { 'High Potential': '#16A34A', 'Medium Potential': '#D97706', 'Low Potential': '#DC2626' }
const FUNNEL_COLORS = ['#2563EB', '#0891B2', '#16A34A', '#D97706']

export default function LeadConversion({ data, apiKey }) {
  const [insight, setInsight] = useState(null)
  const { funnel, source_stats, model_stats, feature_importance, score_tiers,
          status_dist, td_dist, top_leads, prob_dist } = data

  const total     = funnel['Total Leads'] || 0
  const converted = funnel['Converted / Closed'] || 0
  const tdTaken   = funnel['Test Drive Taken'] || 0
  const highPot   = funnel['High Potential (Remaining)'] || 0
  const convRate  = total ? (converted / total * 100).toFixed(1) : 0
  const tdRate    = total ? (tdTaken / total * 100).toFixed(1) : 0
  const avgProb   = prob_dist.length
    ? (prob_dist.reduce((s, r) => s + r.conversion_prob, 0) / prob_dist.length * 100).toFixed(1)
    : 0

  const funnelData = Object.entries(funnel).map(([name, value], i) => ({ name, value, fill: FUNNEL_COLORS[i] }))
  const tierData   = Object.entries(score_tiers).map(([name, value]) => ({ name, value }))
  const fiData     = Object.entries(feature_importance)
    .map(([k, v]) => ({ name: k.replace(/_enc|_/g,' ').trim(), value: parseFloat(v.toFixed(3)) }))
    .sort((a, b) => a.value - b.value)

  async function generateInsight() {
    const text = await getConversionInsights(funnel, source_stats, model_stats, score_tiers, apiKey)
    setInsight(text)
  }

  return (
    <div>
      <h2 className="text-xl font-bold text-slate-900 mb-1">Lead Conversion Analysis</h2>
      <p className="text-sm text-slate-500 mb-6">
        Random Forest ML model scores each lead's conversion probability based on test-drive
        behaviour, source, vehicle interest and lead age.
      </p>

      <div className="grid grid-cols-5 gap-4 mb-6">
        <KPICard label="Total Leads"          value={total.toLocaleString()} />
        <KPICard label="Converted / Closed"   value={converted.toLocaleString()} delta={`${convRate}% conversion rate`} />
        <KPICard label="Test Drives Taken"    value={tdTaken.toLocaleString()} delta={`${tdRate}% of leads`} />
        <KPICard label="High-Potential Leads" value={highPot.toLocaleString()} delta="Unconverted — act now" />
        <KPICard label="Avg Conv. Probability" value={`${avgProb}%`} />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <ChartCard title="Lead Conversion Funnel">
          <ResponsiveContainer width="100%" height={300}>
            <FunnelChart>
              <Tooltip />
              <Funnel dataKey="value" data={funnelData} isAnimationActive>
                <LabelList position="center" fill="#fff" fontSize={12} fontWeight={600}
                           formatter={(v, e) => `${e?.name || ''}: ${v}`} />
                {funnelData.map((e, i) => <Cell key={i} fill={e.fill} />)}
              </Funnel>
            </FunnelChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="ML Score Tier Distribution">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={tierData} dataKey="value" nameKey="name"
                   cx="50%" cy="50%" innerRadius={65} outerRadius={105}
                   label={({ name, percent }) => `${name.split(' ')[0]} ${(percent*100).toFixed(0)}%`}
              >
                {tierData.map((e, i) => <Cell key={i} fill={TIER_COLORS[e.name] || '#94A3B8'} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <ChartCard title="Total Leads by Source">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={source_stats} margin={{ bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="source_name" tick={{ fontSize: 10 }} angle={-35} textAnchor="end" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="total" fill="#2563EB" radius={[3,3,0,0]} name="Leads" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Conversion Rate by Source (%)">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart
              data={[...source_stats].sort((a,b) => b.conversion_rate - a.conversion_rate)}
              margin={{ bottom: 60 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="source_name" tick={{ fontSize: 10 }} angle={-35} textAnchor="end" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={v => [`${v}%`, 'Conv. Rate']} />
              <Bar dataKey="conversion_rate" fill="#16A34A" radius={[3,3,0,0]} name="Conv. Rate %" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <ChartCard title="Leads per Model">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={model_stats} margin={{ bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="model_name" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="total" fill="#2563EB" radius={[3,3,0,0]} name="Leads" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="ML Feature Importance">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={fiData} layout="vertical" margin={{ left: 20, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 10 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#2563EB" radius={[0,3,3,0]} name="Importance" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <ChartCard title="Lead Status Breakdown">
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={Object.entries(status_dist).map(([name,value])=>({name,value}))}
                dataKey="value" nameKey="name"
                cx="50%" cy="50%" innerRadius={55} outerRadius={90}
                label={({ name, percent }) => `${name.split('/')[0]} ${(percent*100).toFixed(0)}%`}
              >
                {Object.keys(status_dist).map((_, i) => (
                  <Cell key={i} fill={['#16A34A','#2563EB'][i % 2]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Test Drive Taken vs Not">
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={Object.entries(td_dist).map(([name,value])=>({name,value}))}
                dataKey="value" nameKey="name"
                cx="50%" cy="50%" innerRadius={55} outerRadius={90}
                label={({ name, percent }) => `${name} ${(percent*100).toFixed(0)}%`}
              >
                {Object.keys(td_dist).map((_, i) => (
                  <Cell key={i} fill={['#0891B2','#D97706','#94A3B8'][i % 3]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Top leads table */}
      <ChartCard title="Top High-Potential Leads (Unconverted)" className="mb-4 overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-slate-200">
              {['Lead ID','Model','Source','Lead Type','Test Drive','Age (Days)','Conv. Prob.','Tier'].map(h => (
                <th key={h} className="text-left py-2 px-2 font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {top_leads.map((l, i) => (
              <tr key={i} className="border-b border-slate-100 bg-green-50">
                <td className="py-1.5 px-2">{l.id}</td>
                <td className="py-1.5 px-2">{l.model_name}</td>
                <td className="py-1.5 px-2">{l.source_name}</td>
                <td className="py-1.5 px-2">{l.lead_type_label}</td>
                <td className="py-1.5 px-2">{l.td_status_label}</td>
                <td className="py-1.5 px-2">{l.lead_age_days}</td>
                <td className="py-1.5 px-2 font-semibold">{(l.conversion_prob * 100).toFixed(1)}%</td>
                <td className="py-1.5 px-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-green-100 text-green-800">
                    {l.score_tier}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </ChartCard>

      <AIInsightPanel apiKey={apiKey} onGenerate={generateInsight} cachedInsight={insight} />
    </div>
  )
}
```

---

## Task 11: Frontend — EDA Summary page + App.jsx

**Files:**
- Create: `frontend/src/pages/EdaSummary.jsx`
- Create: `frontend/src/App.jsx`

- [ ] **Step 1: Write `frontend/src/pages/EdaSummary.jsx`**

```jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import ChartCard from '../components/ChartCard'

export default function EdaSummary({ data }) {
  const files = [
    { label: 'Leads',       eda: data.leads },
    { label: 'Calls',       eda: data.calls },
    { label: 'Test Drives', eda: data.testdrives },
  ]

  return (
    <div>
      <h2 className="text-xl font-bold text-slate-900 mb-1">EDA & Data Quality Summary</h2>
      <p className="text-sm text-slate-500 mb-6">
        Auto-generated exploratory data analysis performed before the ML pipeline.
      </p>
      {files.map(({ label, eda }) => (
        <ChartCard key={label} title={`${label} — ${eda.total_rows.toLocaleString()} rows x ${eda.total_cols} columns`} className="mb-4">
          <div className="grid grid-cols-3 gap-4 mb-4 text-center">
            <div>
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">Rows</p>
              <p className="text-xl font-bold text-slate-800">{eda.total_rows.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">Columns</p>
              <p className="text-xl font-bold text-slate-800">{eda.total_cols}</p>
            </div>
            <div>
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">Duplicates Removed</p>
              <p className="text-xl font-bold text-slate-800">{eda.duplicates}</p>
            </div>
          </div>

          {Object.keys(eda.missing_pct || {}).length > 0 ? (
            <>
              <p className="text-xs font-semibold text-slate-500 mb-2">Top Columns with Missing Data:</p>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart
                  data={Object.entries(eda.missing_pct)
                    .sort((a,b) => b[1]-a[1]).slice(0,15)
                    .map(([col, pct]) => ({ col, pct }))}
                  margin={{ bottom: 70 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="col" tick={{ fontSize: 9 }} angle={-40} textAnchor="end" />
                  <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
                  <Tooltip formatter={v => [`${v}%`, 'Missing']} />
                  <Bar dataKey="pct" name="Missing %" radius={[3,3,0,0]}>
                    {Object.keys(eda.missing_pct).slice(0,15).map((_, i) => (
                      <Cell key={i} fill={`hsl(${0 + i*8}, 80%, 55%)`} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </>
          ) : (
            <p className="text-sm text-green-700 bg-green-50 border border-green-200 rounded px-3 py-2">
              No missing data detected in this file.
            </p>
          )}
        </ChartCard>
      ))}
    </div>
  )
}
```

- [ ] **Step 2: Write `frontend/src/App.jsx`**

```jsx
import { useState, useRef } from 'react'
import { analyzeFiles } from './api/client'
import FileSlot           from './components/FileSlot'
import AgentPerformance   from './pages/AgentPerformance'
import CustomerConnectivity from './pages/CustomerConnectivity'
import LeadConversion     from './pages/LeadConversion'
import EdaSummary         from './pages/EdaSummary'

const TABS = ['Agent Performance', 'Customer Connectivity', 'Lead Conversion', 'EDA Summary']

export default function App() {
  const [files,      setFiles]      = useState({ leads: null, calls: null, td: null })
  const [apiKey,     setApiKey]     = useState('')
  const [results,    setResults]    = useState(null)
  const [activeTab,  setActiveTab]  = useState(0)
  const [loading,    setLoading]    = useState(false)
  const [error,      setError]      = useState(null)

  function setFile(key, f) { setFiles(p => ({ ...p, [key]: f })) }

  async function runAnalysis() {
    if (!files.leads || !files.calls || !files.td) return
    setLoading(true)
    setError(null)
    setResults(null)
    try {
      const data = await analyzeFiles(files.leads, files.calls, files.td)
      setResults(data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  function reset() {
    setFiles({ leads: null, calls: null, td: null })
    setResults(null)
    setError(null)
    setActiveTab(0)
  }

  const allUploaded = files.leads && files.calls && files.td

  return (
    <div className="flex h-screen overflow-hidden font-sans">

      {/* Sidebar */}
      <aside className="w-64 shrink-0 bg-[rgb(240,253,244)] border-r border-slate-200
                        flex flex-col overflow-y-auto">
        <div className="px-5 py-5 border-b border-green-200">
          <h1 className="text-base font-bold text-green-900">CRM Analytics AI</h1>
        </div>

        <div className="px-5 py-5 flex-1">
          <p className="text-[10px] font-semibold text-green-700 uppercase tracking-widest mb-3">
            Upload Data Files
          </p>
          <FileSlot label="Leads CSV"               file={files.leads} onSelect={f => setFile('leads', f)} onRemove={() => setFile('leads', null)} />
          <FileSlot label="Sales Completed Calls CSV" file={files.calls} onSelect={f => setFile('calls', f)} onRemove={() => setFile('calls', null)} />
          <FileSlot label="Test Drive Details CSV"  file={files.td}    onSelect={f => setFile('td',    f)} onRemove={() => setFile('td',    null)} />

          <hr className="border-green-200 my-4" />

          <p className="text-[10px] font-semibold text-green-700 uppercase tracking-widest mb-2">
            AI Insights (Optional)
          </p>
          <input
            type="password"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            placeholder="sk-ant-..."
            className="w-full text-xs border border-green-200 rounded px-3 py-2
                       bg-white text-slate-700 placeholder-slate-400 focus:outline-none
                       focus:border-blue-400"
          />

          <hr className="border-green-200 my-4" />

          <button
            onClick={runAnalysis}
            disabled={!allUploaded || loading}
            className="w-full bg-blue-600 text-white text-sm font-semibold rounded py-2
                       hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed mb-2"
          >
            {loading ? 'Analysing...' : 'Run Analysis'}
          </button>

          <button
            onClick={reset}
            className="w-full border border-green-300 text-green-800 text-sm font-medium
                       rounded py-2 hover:bg-green-100"
          >
            Reset / Clear
          </button>
        </div>

        <div className="px-5 py-4 border-t border-green-200">
          <p className="text-[10px] text-green-600 leading-5">
            <strong>Pipeline stages:</strong><br />
            1. Load &amp; Validate<br />
            2. EDA &amp; Clean<br />
            3. Feature Engineering<br />
            4. ML Analysis<br />
            5. Dashboard Render
          </p>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col overflow-hidden bg-slate-100">

        {/* Header */}
        <header className="bg-[rgb(240,253,244)] border-b border-slate-200 px-8 py-4 shrink-0">
          <h1 className="text-xl font-bold text-green-900 tracking-tight">
            AI-Based CRM Analytics Dashboard
          </h1>
        </header>

        <div className="flex-1 overflow-y-auto px-8 py-6">

          {/* Welcome */}
          {!results && !loading && (
            <div className="bg-white border border-slate-200 rounded p-10 text-center max-w-2xl mx-auto mt-10">
              <h2 className="text-lg font-bold text-blue-700 mb-3">Welcome to CRM Analytics AI</h2>
              <p className="text-sm text-slate-500 mb-6">
                Upload your three CRM CSV files in the sidebar to start the AI-driven analysis pipeline.
              </p>
              <div className="flex justify-center gap-6 flex-wrap">
                {[
                  ['Agent Performance',    'Ranks agents by calls, lead quality & test-drive results',      '#EFF6FF', '#1E40AF'],
                  ['Customer Connectivity','Evaluates engagement, reach & call patterns',                   '#F0FDF4', '#166534'],
                  ['Lead Conversion',      'ML-scores leads & spots highest-potential opportunities',       '#FFF7ED', '#92400E'],
                ].map(([title, desc, bg, color]) => (
                  <div key={title} style={{ background: bg }} className="rounded p-4 w-44 text-left">
                    <p style={{ color }} className="text-xs font-bold mb-1">{title}</p>
                    <p className="text-xs text-slate-500">{desc}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className="flex items-center justify-center h-48">
              <p className="text-slate-500 text-sm animate-pulse">Running analysis pipeline...</p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded px-4 py-3 text-sm text-red-700 mb-4">
              {error}
            </div>
          )}

          {/* Results */}
          {results && (
            <>
              {/* Summary strip */}
              <div className="grid grid-cols-4 gap-4 mb-6">
                {[
                  ['Leads Loaded',       results.load_info.leads_rows.toLocaleString()],
                  ['Calls Loaded',       results.load_info.calls_rows.toLocaleString()],
                  ['Test Drive Records', results.load_info.testdrive_rows.toLocaleString()],
                  ['ML Models Applied',  '2 (K-Means + RF)'],
                ].map(([label, value]) => (
                  <div key={label}
                       className="bg-white border border-slate-200 rounded px-4 py-3
                                  border-t-[3px] border-t-blue-600">
                    <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest">{label}</p>
                    <p className="text-xl font-bold text-slate-800 mt-1">{value}</p>
                  </div>
                ))}
              </div>

              {/* Tabs */}
              <div className="flex border-b border-slate-200 mb-6 bg-white rounded-t">
                {TABS.map((tab, i) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(i)}
                    className={`px-5 py-3 text-sm font-medium border-b-2 transition-colors
                      ${activeTab === i
                        ? 'border-blue-600 text-blue-700'
                        : 'border-transparent text-slate-500 hover:text-slate-700'}`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {activeTab === 0 && <AgentPerformance     data={results.agent}        apiKey={apiKey} />}
              {activeTab === 1 && <CustomerConnectivity data={results.connectivity}  apiKey={apiKey} />}
              {activeTab === 2 && <LeadConversion       data={results.conversion}    apiKey={apiKey} />}
              {activeTab === 3 && <EdaSummary           data={results.eda} />}
            </>
          )}
        </div>
      </main>
    </div>
  )
}
```

---

## Task 12: End-to-end verification

- [ ] **Step 1: Start backend**

```bash
cd backend
python main.py
# Expect: Uvicorn running on http://0.0.0.0:8000
```

- [ ] **Step 2: Start frontend (new terminal)**

```bash
cd frontend
npm run dev
# Expect: VITE ready at http://localhost:5173
```

- [ ] **Step 3: Open browser and upload all three CSVs**

Navigate to `http://localhost:5173`, upload `leads.csv`, `sales_completed_calls.csv`, `sales_test_drive_details.csv`, click **Run Analysis**.

Expected: Summary strip shows `1,000 / 1,002 / 1,000` records, all four tabs render correctly.

- [ ] **Step 4: (Optional) Test AI insights**

Add Anthropic API key in sidebar, click **Generate AI Insights** on Agent Performance tab.
Expected: Insight text appears below the leaderboard table.

---

## Self-Review

**Spec coverage:**
- [x] Backend FastAPI with analyze + insights endpoints
- [x] React frontend with all three dashboard pages + EDA tab
- [x] File upload with badge + X (FileSlot component)
- [x] KPI cards, chart cards, AI insight panel
- [x] Numpy serialisation for JSON safety
- [x] CORS configured for Vite dev server port

**No placeholders:** All code blocks are complete.

**Type consistency:** `df_to_records` returns `list`, `safe_dict` returns `dict` — used consistently. API response shape in `main.py` matches what each React page destructures.
