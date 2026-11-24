"""Lead Conversion Dashboard — Streamlit + Plotly."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.helpers import COLORS


TIER_COLORS = {
    "High Potential":   "#16A34A",
    "Medium Potential": "#D97706",
    "Low Potential":    "#DC2626",
}


def _kpi(col, label, value, delta=None, color=None):
    delta_html = f"<p style='color:#64748B;font-size:12px;margin:4px 0 0;font-weight:400;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{delta}</p>" if delta else ""
    col.markdown(f"""
<div style='background:#FFFFFF;border-radius:6px;padding:18px 20px;
            border:1px solid #E2E8F0;border-top:3px solid #1D4ED8;min-height:96px;
            overflow:hidden;'>
  <p style='color:#64748B;font-size:11px;font-weight:600;margin:0;
            text-transform:uppercase;letter-spacing:0.06em;
            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{label}</p>
  <p style='color:#0F172A;font-size:24px;font-weight:700;margin:6px 0 0;
            letter-spacing:-0.02em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{value}</p>
  {delta_html}
</div>""", unsafe_allow_html=True)


def render_lead_dashboard(conv_results: dict, api_key: str = ""):
    leads   = conv_results["leads_scored"]
    funnel  = conv_results["funnel"]
    sources = conv_results["source_stats"]
    models  = conv_results["model_stats"]
    fi      = conv_results["feature_importance"]

    st.markdown("## Lead Conversion Analysis")

    #  KPIs 
    total     = funnel["Total Leads"]
    converted = funnel["Converted / Closed"]
    td_taken  = funnel["Test Drive Taken"]
    high_pot  = funnel["High Potential (Remaining)"]
    conv_rate = round(converted / total * 100, 1) if total else 0
    td_rate   = round(td_taken / total * 100, 1) if total else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    _kpi(c1, "Total Leads",          f"{total:,}",           color=COLORS["primary"])
    _kpi(c2, "Converted / Closed",   f"{converted:,}",       color=COLORS["success"],
         delta=f"{conv_rate}% conversion rate")
    _kpi(c3, "Test Drives Taken",    f"{td_taken:,}",        color=COLORS["info"],
         delta=f"{td_rate}% of leads")
    _kpi(c4, "High-Potential Leads", f"{high_pot:,}",        color=COLORS["warning"],
         delta="Unconverted — act now")
    _kpi(c5, "Avg Conv. Probability",
         f"{leads['conversion_prob'].mean() * 100:.1f}%",    color=COLORS["purple"])

    st.markdown("<br>", unsafe_allow_html=True)

    #  Row 1: Funnel + score tier pie 
    col_a, col_b = st.columns([2, 2])

    with col_a:
        st.markdown("### Lead Conversion Funnel")
        labels = list(funnel.keys())
        values = list(funnel.values())
        fig1 = go.Figure(go.Funnel(
            y=labels, x=values,
            textinfo="value+percent initial",
            marker=dict(color=["#2563EB", "#0891B2", "#16A34A", "#D97706"]),
            connector=dict(line=dict(color="#e5e7eb", width=2)),
        ))
        fig1.update_layout(
            height=360, paper_bgcolor="white",
            margin=dict(l=10, r=10, t=20, b=20),
            font=dict(size=13),
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.markdown("### ML Score Tier Distribution")
        tier_cnt = leads["score_tier"].value_counts().reset_index()
        tier_cnt.columns = ["tier", "count"]
        fig2 = px.pie(
            tier_cnt, names="tier", values="count",
            color="tier", color_discrete_map=TIER_COLORS,
            hole=0.45,
        )
        fig2.update_traces(textinfo="percent+label", pull=[0.05, 0, 0])
        fig2.update_layout(
            height=360, paper_bgcolor="white",
            showlegend=True, margin=dict(l=10, r=10, t=20, b=20),
        )
        st.plotly_chart(fig2, use_container_width=True)

    #  Conversion by source 
    st.markdown("### Lead Source Performance")
    col_c, col_d = st.columns(2)

    with col_c:
        fig3 = px.bar(
            sources, x="source_name", y="total",
            color="conversion_rate",
            color_continuous_scale=["#BFDBFE", "#1D4ED8"],
            text="total",
            labels={"total": "Leads", "source_name": "", "conversion_rate": "Conv%"},
        )
        fig3.update_traces(textposition="outside")
        fig3.update_layout(
            height=320, paper_bgcolor="white", plot_bgcolor="#f9fafb",
            xaxis_tickangle=-30, margin=dict(l=10, r=10, t=20, b=80),
            title="Total Leads by Source",
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        fig4 = px.bar(
            sources.sort_values("conversion_rate", ascending=False),
            x="source_name", y="conversion_rate",
            color="conversion_rate",
            color_continuous_scale=["#FEF3C7", "#16A34A"],
            text=sources.sort_values("conversion_rate", ascending=False)
                 ["conversion_rate"].apply(lambda x: f"{x:.1f}%"),
            labels={"conversion_rate": "Conv. Rate %", "source_name": ""},
        )
        fig4.update_traces(textposition="outside")
        fig4.update_layout(
            height=320, paper_bgcolor="white", plot_bgcolor="#f9fafb",
            xaxis_tickangle=-30, margin=dict(l=10, r=10, t=20, b=80),
            title="Conversion Rate by Source (%)",
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig4, use_container_width=True)

    #  Model interest + conversion 
    st.markdown("### Vehicle Model — Lead Interest & Conversion")
    col_e, col_f = st.columns(2)

    with col_e:
        fig5 = px.bar(
            models, x="model_name", y="total",
            color="td_taken",
            color_continuous_scale=["#BFDBFE", "#1D4ED8"],
            text="total",
            labels={"total": "Leads", "model_name": "", "td_taken": "Test Drives"},
            title="Leads per Model (shade = test drives taken)",
        )
        fig5.update_traces(textposition="outside")
        fig5.update_layout(
            height=320, paper_bgcolor="white", plot_bgcolor="#f9fafb",
            margin=dict(l=10, r=10, t=40, b=40),
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col_f:
        fig6 = px.bar(
            models.sort_values("conversion_rate", ascending=False),
            x="model_name", y="conversion_rate",
            color="conversion_rate",
            color_continuous_scale=["#FEF3C7", "#16A34A"],
            text=models.sort_values("conversion_rate", ascending=False)
                 ["conversion_rate"].apply(lambda x: f"{x:.1f}%"),
            labels={"conversion_rate": "Conv. Rate %", "model_name": ""},
            title="Conversion Rate by Model (%)",
        )
        fig6.update_traces(textposition="outside")
        fig6.update_layout(
            height=320, paper_bgcolor="white", plot_bgcolor="#f9fafb",
            margin=dict(l=10, r=10, t=40, b=40),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig6, use_container_width=True)

    #  Conversion probability distribution + lead age 
    col_g, col_h = st.columns(2)

    with col_g:
        st.markdown("### ML Conversion Probability Distribution")
        fig7 = px.histogram(
            leads, x="conversion_prob", nbins=20,
            color="score_tier", color_discrete_map=TIER_COLORS,
            labels={"conversion_prob": "Conversion Probability (0–1)"},
            barmode="overlay", opacity=0.75,
        )
        fig7.update_layout(
            height=300, paper_bgcolor="white", plot_bgcolor="#f9fafb",
            margin=dict(l=10, r=10, t=20, b=20),
        )
        st.plotly_chart(fig7, use_container_width=True)

    with col_h:
        st.markdown("### Lead Age vs Conversion Probability")
        fig8 = px.scatter(
            leads.sample(min(500, len(leads))),
            x="lead_age_days", y="conversion_prob",
            color="score_tier", color_discrete_map=TIER_COLORS,
            opacity=0.6, size_max=8,
            labels={"lead_age_days": "Lead Age (Days)", "conversion_prob": "Conv. Probability"},
        )
        fig8.update_layout(
            height=300, paper_bgcolor="white", plot_bgcolor="#f9fafb",
            margin=dict(l=10, r=10, t=20, b=20),
        )
        st.plotly_chart(fig8, use_container_width=True)

    #  Feature importance 
    st.markdown("### ML Feature Importance (What Drives Conversion?)")
    fi_df = pd.DataFrame(
        list(fi.items()), columns=["Feature", "Importance"]
    ).sort_values("Importance", ascending=True)
    fi_df["Feature"] = fi_df["Feature"].str.replace("_enc", "").str.replace("_", " ").str.title()
    fig9 = px.bar(
        fi_df, x="Importance", y="Feature", orientation="h",
        color="Importance",
        color_continuous_scale=["#BFDBFE", "#1D4ED8"],
        text=fi_df["Importance"].apply(lambda x: f"{x:.3f}"),
        labels={"Importance": "Feature Importance", "Feature": ""},
    )
    fig9.update_traces(textposition="outside")
    fig9.update_layout(
        height=300, paper_bgcolor="white", plot_bgcolor="#f9fafb",
        coloraxis_showscale=False, margin=dict(l=10, r=20, t=20, b=20),
    )
    st.plotly_chart(fig9, use_container_width=True)

    #  Lead status breakdown 
    col_i, col_j = st.columns(2)

    with col_i:
        st.markdown("### Lead Status Breakdown")
        status_cnt = leads["status_label"].value_counts().reset_index()
        status_cnt.columns = ["status", "count"]
        fig10 = px.pie(
            status_cnt, names="status", values="count",
            color_discrete_sequence=[COLORS["success"], COLORS["primary"]],
            hole=0.45,
        )
        fig10.update_traces(textinfo="percent+label")
        fig10.update_layout(
            height=300, paper_bgcolor="white",
            margin=dict(l=10, r=10, t=20, b=20),
        )
        st.plotly_chart(fig10, use_container_width=True)

    with col_j:
        st.markdown("### Test Drive Taken vs Not")
        td_cnt = leads["td_status_label"].value_counts().reset_index()
        td_cnt.columns = ["status", "count"]
        fig11 = px.pie(
            td_cnt, names="status", values="count",
            color_discrete_sequence=[COLORS["info"], COLORS["warning"], "#9CA3AF"],
            hole=0.45,
        )
        fig11.update_traces(textinfo="percent+label")
        fig11.update_layout(
            height=300, paper_bgcolor="white",
            margin=dict(l=10, r=10, t=20, b=20),
        )
        st.plotly_chart(fig11, use_container_width=True)

    #  Top high-potential leads table 
    st.markdown("### Top High-Potential Leads (Unconverted)")
    high_leads = leads[
        (leads["score_tier"] == "High Potential") & (leads["converted"] == 0)
    ].nlargest(20, "conversion_prob")[[
        "id", "model_name", "source_name", "lead_type_label",
        "td_status_label", "lead_age_days", "conversion_prob", "score_tier",
    ]].rename(columns={
        "id": "Lead ID", "model_name": "Model", "source_name": "Source",
        "lead_type_label": "Lead Type", "td_status_label": "Test Drive",
        "lead_age_days": "Age (Days)", "conversion_prob": "Conv. Prob.",
        "score_tier": "Tier",
    })

    def _style(row):
        c = {"High Potential": "#dcfce7",
             "Medium Potential": "#fef9c3",
             "Low Potential": "#fee2e2"}.get(row["Tier"], "white")
        return [f"background-color: {c}"] * len(row)

    st.dataframe(
        high_leads.style.apply(_style, axis=1).format({"Conv. Prob.": "{:.3f}"}),
        use_container_width=True, height=350,
    )

    #  AI Insights 
    st.markdown("---")
    st.markdown("### AI-Generated Executive Insights")

    if "lead_ai_insight" not in st.session_state:
        st.session_state.lead_ai_insight = None

    if api_key:
        if st.button("Generate AI Insights for Lead Conversion", key="btn_lead_ai"):
            with st.spinner("Analysing lead data with Claude AI…"):
                try:
                    import os
                    os.environ["ANTHROPIC_API_KEY"] = api_key
                    from pipeline.ai_insights import get_conversion_insights
                    st.session_state.lead_ai_insight = get_conversion_insights(
                        funnel, sources, models, leads
                    )
                except Exception as e:
                    st.error(f"Claude API error: {e}")
    else:
        st.info("Enter your Anthropic API key in the sidebar to unlock AI insights.")

    if st.session_state.lead_ai_insight:
        st.markdown(
            f"""<div style='background:#FFFFFF;border-radius:6px;padding:24px;
                border:1px solid #E2E8F0;border-left:3px solid #1D4ED8;
                color:#1E293B;font-size:14px;line-height:1.7;'>
            {st.session_state.lead_ai_insight.replace(chr(10),'<br>')}
            </div>""",
            unsafe_allow_html=True,
        )
