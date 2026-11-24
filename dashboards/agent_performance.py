"""Agent Performance Dashboard — Streamlit + Plotly."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.helpers import COLORS, TIER_COLORS


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


def render_agent_dashboard(agent_results: dict, api_key: str = ""):
    df   = agent_results["agent_metrics"]

    st.markdown("## Agent Performance Analysis")

    #  KPI row 
    c1, c2, c3, c4, c5 = st.columns(5)
    total_agents  = len(df)
    total_calls   = int(df["total_calls"].sum())
    top_agent_row = df[df["rank"] == 1].iloc[0]
    top_name      = top_agent_row["agent_name"]
    avg_score     = df["composite_score"].mean()
    high_count    = int((df["tier"] == "High").sum())

    _kpi(c1, "Total Agents",          total_agents,              color=COLORS["primary"])
    _kpi(c2, "Total Calls Analysed",  f"{total_calls:,}",        color=COLORS["info"])
    _kpi(c3, "Top Performer",         top_name,                  color=COLORS["success"])
    _kpi(c4, "Avg Performance Score", f"{avg_score:.1f}/100",    color=COLORS["warning"])
    _kpi(c5, "High-Tier Agents",      f"{high_count}/{total_agents}", color=COLORS["purple"])

    st.markdown("<br>", unsafe_allow_html=True)

    #  Row 1: ranking bar + pie 
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown("### Agent Performance Score Ranking")
        fig = px.bar(
            df.sort_values("composite_score", ascending=True),
            x="composite_score", y="agent_name",
            color="tier", orientation="h",
            color_discrete_map=TIER_COLORS,
            text=df.sort_values("composite_score")["composite_score"].apply(lambda x: f"{x:.0f}"),
            labels={"composite_score": "Score (0–100)", "agent_name": ""},
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=380, paper_bgcolor="white", plot_bgcolor="#f9fafb",
            legend_title="Tier", font=dict(size=13),
            margin=dict(l=10, r=20, t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("### Performance Tier Distribution")
        tier_cnt = df["tier"].value_counts().reset_index()
        tier_cnt.columns = ["tier", "count"]
        fig2 = px.pie(
            tier_cnt, names="tier", values="count",
            color="tier", color_discrete_map=TIER_COLORS,
            hole=0.45,
        )
        fig2.update_traces(textinfo="percent+label", pull=[0.05, 0, 0])
        fig2.update_layout(
            height=380, paper_bgcolor="white",
            showlegend=True, margin=dict(l=10, r=10, t=20, b=20),
        )
        st.plotly_chart(fig2, use_container_width=True)

    #  Row 2: calls + callback rate 
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("### Calls Handled per Agent")
        fig3 = px.bar(
            df.sort_values("total_calls", ascending=False),
            x="agent_name", y="total_calls",
            color="tier", color_discrete_map=TIER_COLORS,
            text="total_calls",
            labels={"total_calls": "Calls", "agent_name": ""},
        )
        fig3.update_traces(textposition="outside")
        fig3.update_layout(
            height=320, paper_bgcolor="white", plot_bgcolor="#f9fafb",
            showlegend=False, margin=dict(l=10, r=10, t=20, b=60),
            xaxis_tickangle=-30,
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        st.markdown("### Callback Scheduling Rate (%)")
        fig4 = px.bar(
            df.sort_values("callback_rate", ascending=False),
            x="agent_name", y="callback_rate",
            color="tier", color_discrete_map=TIER_COLORS,
            text=df.sort_values("callback_rate", ascending=False)["callback_rate"].apply(
                lambda x: f"{x:.1f}%"),
            labels={"callback_rate": "Callback Rate %", "agent_name": ""},
        )
        fig4.update_traces(textposition="outside")
        fig4.update_layout(
            height=320, paper_bgcolor="white", plot_bgcolor="#f9fafb",
            showlegend=False, margin=dict(l=10, r=10, t=20, b=60),
            xaxis_tickangle=-30,
        )
        st.plotly_chart(fig4, use_container_width=True)

    #  Row 3: hot lead ratio + test-drive scatter 
    col_e, col_f = st.columns(2)

    with col_e:
        st.markdown("### Hot-Lead Ratio per Agent (%)")
        fig5 = px.bar(
            df.sort_values("hot_lead_ratio", ascending=False),
            x="agent_name", y="hot_lead_ratio",
            color="tier", color_discrete_map=TIER_COLORS,
            text=df.sort_values("hot_lead_ratio", ascending=False)["hot_lead_ratio"].apply(
                lambda x: f"{x:.1f}%"),
            labels={"hot_lead_ratio": "Hot Lead %", "agent_name": ""},
        )
        fig5.update_traces(textposition="outside")
        fig5.update_layout(
            height=320, paper_bgcolor="white", plot_bgcolor="#f9fafb",
            showlegend=False, margin=dict(l=10, r=10, t=20, b=60),
            xaxis_tickangle=-30,
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col_f:
        st.markdown("### Calls vs Test Drives (Bubble = Score)")
        fig6 = px.scatter(
            df, x="total_calls", y="test_drives_assigned",
            size="composite_score", color="tier",
            color_discrete_map=TIER_COLORS,
            text="agent_name", hover_data=["composite_score", "tier"],
            size_max=40,
            labels={"total_calls": "Total Calls", "test_drives_assigned": "Test Drives"},
        )
        fig6.update_traces(textposition="top center")
        fig6.update_layout(
            height=320, paper_bgcolor="white", plot_bgcolor="#f9fafb",
            margin=dict(l=10, r=10, t=20, b=20),
        )
        st.plotly_chart(fig6, use_container_width=True)

    #  Lead type stacked bar 
    st.markdown("### Lead Type Handled per Agent")
    lt_df = df[["agent_name", "hot_leads", "warm_leads", "cold_leads"]].copy()
    lt_df = lt_df.melt("agent_name", var_name="Lead Type", value_name="Count")
    lt_df["Lead Type"] = lt_df["Lead Type"].map(
        {"hot_leads": "Hot", "warm_leads": "Warm", "cold_leads": "Cold"}
    )
    fig7 = px.bar(
        lt_df, x="agent_name", y="Count", color="Lead Type",
        color_discrete_map={"Hot": "#DC2626", "Warm": "#D97706", "Cold": "#2563EB"},
        barmode="stack",
        labels={"agent_name": ""},
    )
    fig7.update_layout(
        height=300, paper_bgcolor="white", plot_bgcolor="#f9fafb",
        xaxis_tickangle=-30, margin=dict(l=10, r=10, t=20, b=60),
    )
    st.plotly_chart(fig7, use_container_width=True)

    #  Agent leaderboard table 
    st.markdown("### Agent Leaderboard")
    display_cols = {
        "rank": "Rank", "agent_name": "Agent", "tier": "Tier",
        "composite_score": "Score", "total_calls": "Calls",
        "hot_lead_ratio": "Hot Lead %", "callback_rate": "Callback %",
        "test_drives_assigned": "Test Drives", "td_conversion_rate": "TD Completion %",
        "unique_customers": "Unique Customers",
    }
    table = df[list(display_cols.keys())].rename(columns=display_cols)

    def _style(row):
        color = {"High": "#dcfce7", "Medium": "#fef9c3", "Low": "#fee2e2"}.get(row["Tier"], "white")
        return [f"background-color: {color}"] * len(row)

    st.dataframe(
        table.style.apply(_style, axis=1).format(
            {"Score": "{:.1f}", "Hot Lead %": "{:.1f}", "Callback %": "{:.1f}",
             "TD Completion %": "{:.1f}"}
        ),
        use_container_width=True, height=350,
    )

    #  AI Insights 
    st.markdown("---")
    st.markdown("### AI-Generated Executive Insights")

    if "agent_ai_insight" not in st.session_state:
        st.session_state.agent_ai_insight = None

    if api_key:
        if st.button("Generate AI Insights for Agent Performance", key="btn_agent_ai"):
            with st.spinner("Analysing agent data with Claude AI…"):
                try:
                    import os
                    os.environ["ANTHROPIC_API_KEY"] = api_key
                    from pipeline.ai_insights import get_agent_insights
                    st.session_state.agent_ai_insight = get_agent_insights(df)
                except Exception as e:
                    st.error(f"Claude API error: {e}")
    else:
        st.info("Enter your Anthropic API key in the sidebar to unlock AI insights.")

    if st.session_state.agent_ai_insight:
        st.markdown(
            f"""<div style='background:#FFFFFF;border-radius:6px;padding:24px;
                border:1px solid #E2E8F0;border-left:3px solid #1D4ED8;
                color:#1E293B;font-size:14px;line-height:1.7;'>
            {st.session_state.agent_ai_insight.replace(chr(10),'<br>')}
            </div>""",
            unsafe_allow_html=True,
        )
