"""AI Insights - prompt builders that accept plain dicts (no DataFrames)."""

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
