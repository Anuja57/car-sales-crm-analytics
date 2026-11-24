"""
AI Insights — calls Claude to produce executive-level summaries.

Each `get_*_insights()` function builds a context string from
aggregated metrics and returns structured text from Claude.
"""

import os
import anthropic

MODEL = "claude-sonnet-4-6"


def _client() -> anthropic.Anthropic:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not set.")
    return anthropic.Anthropic(api_key=key)


def _ask(prompt: str) -> str:
    """Send one-shot prompt and return assistant text."""
    client = _client()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=900,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


#  Agent Performance 

def get_agent_insights(agent_metrics_df) -> str:
    df = agent_metrics_df.copy()
    top3   = df.nsmallest(3, "rank")[["agent_name", "composite_score",
                                       "total_calls", "hot_lead_ratio",
                                       "callback_rate", "test_drives_assigned",
                                       "tier"]].to_string(index=False)
    bottom = df.nlargest(3, "rank")[["agent_name", "composite_score",
                                     "total_calls", "hot_lead_ratio",
                                     "callback_rate", "tier"]].to_string(index=False)
    tier_dist = df["tier"].value_counts().to_dict()
    avg_score = df["composite_score"].mean().round(1)

    prompt = f"""You are an automotive CRM analytics expert.
Below are agent performance metrics (car sales team):

TOP 3 AGENTS:
{top3}

BOTTOM 3 AGENTS:
{bottom}

OVERALL STATS:
- Average composite score: {avg_score}/100
- Tier distribution: {tier_dist}
- Total agents analysed: {len(df)}

Write a concise EXECUTIVE INSIGHT (max 200 words) covering:
1. **Key Strengths** – what top agents are doing well
2. **Improvement Areas** – patterns in low-performing agents
3. **Action Recommendations** – 3 specific, practical steps to raise team performance

Use plain language. The audience is non-technical sales managers.
Format with short bullet points under each heading."""

    return _ask(prompt)


#  Customer Connectivity 

def get_connectivity_insights(cust_df, time_series_df, ltd_df) -> str:
    seg_dist  = cust_df["segment"].value_counts().to_dict()
    avg_calls = cust_df["total_calls"].mean().round(2)
    cb_rate   = cust_df["callback_rate"].mean().round(1)
    ltd_dict  = dict(zip(ltd_df["lead_type"], ltd_df["count"]))
    hot_pct   = round(ltd_dict.get("Hot", 0) /
                      ltd_df["count"].sum() * 100, 1) if len(ltd_df) else 0
    peak_date = time_series_df.loc[time_series_df["call_count"].idxmax(),
                                    "call_date"].strftime("%Y-%m-%d") \
        if len(time_series_df) else "N/A"

    prompt = f"""You are an automotive CRM analytics expert.
Below are customer connectivity metrics:

CUSTOMER ENGAGEMENT SEGMENTS:
{seg_dist}

KEY METRICS:
- Average calls per customer: {avg_calls}
- Average callback scheduling rate: {cb_rate}%
- Lead type distribution: {ltd_dict}
- Hot lead percentage: {hot_pct}%
- Peak call day: {peak_date}

Write a concise EXECUTIVE INSIGHT (max 200 words) covering:
1. **Connectivity Health** – how well the team is engaging with customers
2. **Risk Signals** – segments or patterns showing poor connectivity
3. **Action Recommendations** – 3 specific steps to improve customer engagement

Use plain language. The audience is non-technical sales managers.
Format with short bullet points under each heading."""

    return _ask(prompt)


#  Lead Conversion 

def get_conversion_insights(funnel, source_stats_df, model_stats_df,
                             leads_scored_df) -> str:
    total        = funnel.get("Total Leads", 0)
    converted    = funnel.get("Converted / Closed", 0)
    conv_rate    = round(converted / total * 100, 1) if total else 0
    high_pot     = funnel.get("High Potential (Remaining)", 0)
    top_sources  = source_stats_df.nlargest(3, "conversion_rate")[
        ["source_name", "total", "conversion_rate"]].to_string(index=False)
    top_models   = model_stats_df.nlargest(3, "total")[
        ["model_name", "total", "conversion_rate"]].to_string(index=False)
    tier_dist    = leads_scored_df["score_tier"].value_counts().to_dict()

    prompt = f"""You are an automotive CRM analytics expert.
Below are lead conversion analysis metrics for a car dealership:

FUNNEL:
- Total Leads: {total}
- Converted/Closed: {converted} ({conv_rate}%)
- High-Potential Remaining: {high_pot}

LEAD SCORE TIERS:
{tier_dist}

TOP CONVERTING SOURCES:
{top_sources}

TOP CAR MODELS BY INTEREST:
{top_models}

Write a concise EXECUTIVE INSIGHT (max 200 words) covering:
1. **Conversion Performance** – how the funnel is performing
2. **Biggest Opportunities** – where the highest-potential leads are coming from
3. **Action Recommendations** – 3 specific steps to increase lead conversion

Use plain language. The audience is non-technical sales managers.
Format with short bullet points under each heading."""

    return _ask(prompt)
