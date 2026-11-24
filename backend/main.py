"""FastAPI backend for CRM Analytics AI."""

import sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

        cust = conn_r["customer_metrics"]

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


class AgentInsightRequest(BaseModel):
    api_key:   str
    metrics:   list
    tier_dist: dict
    avg_score: float

class ConnInsightRequest(BaseModel):
    api_key:        str
    segments:       dict
    avg_calls:      float
    avg_cb_rate:    float
    lead_type_dist: list

class ConvInsightRequest(BaseModel):
    api_key:      str
    funnel:       dict
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
