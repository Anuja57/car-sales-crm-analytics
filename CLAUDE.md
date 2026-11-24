# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-Based Data Analytics for CRM Optimization — a Streamlit web application that ingests three CRM CSVs, runs an automated data-science pipeline (EDA → cleaning → ML), and renders three interactive Plotly dashboards powered by Claude AI narrative insights. A parallel React + FastAPI migration is in progress (see `docs/superpowers/plans/2026-04-03-react-fastapi-migration.md`).

## Running the App

**Streamlit (current):**
```bash
pip install -r requirements.txt
streamlit run app.py
# Opens at http://localhost:8501
```

**FastAPI backend (migration):**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# API at http://localhost:8000; CORS allows localhost:5173 and localhost:3000
```

**React frontend (migration):**
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

Set `ANTHROPIC_API_KEY` in the environment (or `.env`) to enable AI insights. The app runs without it.

## Architecture

```
app.py                        ← Entry point: global CSS, _file_slot helper, sidebar,
                                pipeline trigger, tab router
pipeline/
  data_loader.py              ← load_data() — accepts file paths or UploadedFile objects
  data_cleaner.py             ← clean_leads/calls/testdrives() — returns (df, eda_dict)
  ml_engine.py                ← Three analyses, each returns a results dict (see below)
  ai_insights.py              ← get_*_insights() — calls Claude, returns markdown string
dashboards/
  agent_performance.py        ← render_agent_dashboard(agent_results, api_key)
  customer_connectivity.py    ← render_connectivity_dashboard(conn_results, api_key)
  lead_conversion.py          ← render_lead_dashboard(conv_results, api_key)
utils/
  helpers.py                  ← AGENT_NAMES, MODEL_MAP, LEAD_SOURCE_MAP, label_* functions
backend/
  main.py                     ← FastAPI: POST /api/analyze + /api/insights/{agent|connectivity|conversion}
  serializer.py               ← NumpyEncoder, df_to_records, safe_dict (np.int64/float32/Timestamp → JSON)
  pipeline/                   ← Copies of root pipeline files; ai_insights.py uses dict-based prompts
  utils/                      ← Copy of helpers.py (separate namespace for FastAPI deployment)
frontend/
  src/
    api/client.js             ← analyzeFiles(), getInsights() — Axios calls to FastAPI
    components/               ← FileSlot, KPICard, ChartCard, AIInsightPanel
    pages/                    ← AgentPerformance, CustomerConnectivity, LeadConversion, EdaSummary
```

## Session State Keys

All pipeline output is stored in `st.session_state` so re-renders don't re-run the ML:

| Key | Contents |
|---|---|
| `slot_leads` / `slot_calls` / `slot_td` | UploadedFile objects from `_file_slot()` |
| `analysis_done` | bool — gates the pipeline from running twice |
| `agent_results` / `conn_results` / `conv_results` | dicts returned by `ml_engine.py` |
| `load_info` / `leads_eda` / `calls_eda` / `td_eda` | loader + EDA summary dicts |
| `agent_ai_insight` / `conn_ai_insight` / `lead_ai_insight` | cached Claude responses |

Reset clears all the above keys explicitly (not `st.session_state.clear()`) to avoid wiping widget state.

## ML Pipeline

| Dashboard | Algorithm | Input | Output dict keys |
|---|---|---|---|
| Agent Performance | K-Means (k=3) + weighted composite score | calls + test-drives | `agent_metrics`, `feature_cols` |
| Customer Connectivity | Rule-based engagement score | calls | `customer_metrics`, `time_series`, `location_stats`, `lead_type_dist` |
| Lead Conversion | Random Forest (150 trees, balanced) | leads | `leads_scored`, `feature_importance`, `funnel`, `source_stats`, `model_stats` |

### Non-obvious ML details

- **Agent K-Means:** Features scaled with `MinMaxScaler` before clustering. Composite score weights: total_calls 0.25, hot_lead_ratio 0.20, test_drives_assigned 0.20, callback_rate 0.15, td_conversion_rate 0.15, unique_customers 0.05. Tiers bucketed at 67th/33rd percentiles (not equal-width bins).
- **Connectivity score:** Lead-type weights: Hot=3, Warm=2, Cold=1. Combined as `calls×0.4 + callback_rate×0.3 + lead_type_weight×0.3`, normalised per dataset.
- **Random Forest fallback:** If fewer than 2 classes or fewer than 20 rows exist in the leads data, scoring reverts to rule-based: `td_taken×0.5 + is_hot_inbound×0.3 + (lead_age<30)×0.2`.
- **Agent–TD join:** Agent metrics aggregated from calls only; test-drive stats are left-joined on `agent_name` afterwards.
- **Lead age reference:** Calculated as `ref_date − created_at` where `ref_date = max(created_at)`, ensuring relative consistency within a batch.

## Key Data Quirks

- `created_by` in calls is `float64` (e.g. `7200223.0`) — `label_agent()` handles `int(float(x))` conversion before dict lookup; unmapped IDs return `f"Agt-{key[-3:]}"`
- `status` and `test_drive_status` in leads are also floats — cleaners normalise via `str(x).split(".")[0]`
- Leads (Nov–Dec 2023) and calls (Sept 2023) share no direct join key — analysed independently
- All three files use numeric IDs for agents, models, and lead sources; human-readable labels live in `utils/helpers.py`
- Null sentinel: both string `'NULL'` and `pd.NaN` are treated uniformly via a `NULL_VALUES` set in the cleaners; all dates use `pd.to_datetime(..., errors='coerce')`

## Styling Conventions

- Font: Poppins (Google Fonts, loaded via `@import` in global CSS block in `app.py`)
- Page background: `#F1F5F9`; sidebar + header: `rgb(240, 253, 244)` (light mint green)
- KPI cards: white, `1px solid #E2E8F0` border, `3px solid #1D4ED8` top accent
- All dashboard-level CSS is in `app.py`; card-level HTML is in each dashboard's `_kpi()` function
- React frontend uses the same palette with Tailwind utility classes and Recharts (replaces Plotly)
