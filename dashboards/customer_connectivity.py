"""Customer Connectivity Dashboard — Streamlit + Plotly."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.helpers import COLORS, SEGMENT_COLORS


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


def render_connectivity_dashboard(conn_results: dict, api_key: str = ""):
    cust  = conn_results["customer_metrics"]
    ts    = conn_results["time_series"]
    loc   = conn_results["location_stats"]
    ltd   = conn_results["lead_type_dist"]

    st.markdown("## Customer Connectivity Analysis")

    #  KPIs 
    total_cust     = len(cust)
    avg_calls      = cust["total_calls"].mean()
    avg_cb_rate    = cust["callback_rate"].mean()
    highly_engaged = int((cust["segment"] == "Highly Engaged").sum())
    hot_count      = int(ltd[ltd["lead_type"] == "Hot"]["count"].sum()) if "Hot" in ltd["lead_type"].values else 0
    total_calls_all= int(ltd["count"].sum())
    hot_pct        = round(hot_count / total_calls_all * 100, 1) if total_calls_all else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    _kpi(c1, "Unique Customers",       f"{total_cust:,}",        color=COLORS["primary"])
    _kpi(c2, "Avg Calls / Customer",   f"{avg_calls:.1f}",       color=COLORS["info"])
    _kpi(c3, "Avg Callback Rate",      f"{avg_cb_rate:.1f}%",    color=COLORS["warning"])
    _kpi(c4, "Highly Engaged",         f"{highly_engaged}",      color=COLORS["success"])
    _kpi(c5, "Hot Lead Share",         f"{hot_pct}%",            color=COLORS["danger"])

    st.markdown("<br>", unsafe_allow_html=True)

    #  Row 1: segment pie + lead-type donut 
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Customer Engagement Segments")
        seg = cust["segment"].value_counts().reset_index()
        seg.columns = ["segment", "count"]
        fig1 = px.pie(
            seg, names="segment", values="count",
            color="segment", color_discrete_map=SEGMENT_COLORS,
            hole=0.45,
        )
        fig1.update_traces(textinfo="percent+label", pull=[0.05, 0, 0])
        fig1.update_layout(
            height=360, paper_bgcolor="white",
            showlegend=True, margin=dict(l=10, r=10, t=20, b=20),
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.markdown("### Lead Type Distribution (Calls)")
        fig2 = px.pie(
            ltd, names="lead_type", values="count",
            color="lead_type",
            color_discrete_map={"Hot": "#DC2626", "Warm": "#D97706",
                                 "Cold": "#2563EB", "Unknown": "#9CA3AF"},
            hole=0.45,
        )
        fig2.update_traces(textinfo="percent+label", pull=[0.05, 0, 0])
        fig2.update_layout(
            height=360, paper_bgcolor="white",
            showlegend=True, margin=dict(l=10, r=10, t=20, b=20),
        )
        st.plotly_chart(fig2, use_container_width=True)

    #  Daily call volume time-series 
    st.markdown("### Daily Call Volume & Lead Type Trend")
    fig3 = go.Figure()
    if len(ts) > 0:
        fig3.add_trace(go.Bar(
            x=ts["call_date"], y=ts["cold_calls"], name="Cold",
            marker_color="#93C5FD", opacity=0.8,
        ))
        fig3.add_trace(go.Bar(
            x=ts["call_date"], y=ts["warm_calls"], name="Warm",
            marker_color="#FCD34D", opacity=0.8,
        ))
        fig3.add_trace(go.Bar(
            x=ts["call_date"], y=ts["hot_calls"], name="Hot",
            marker_color="#F87171", opacity=0.8,
        ))
        fig3.add_trace(go.Scatter(
            x=ts["call_date"], y=ts["call_count"], name="Total Calls",
            mode="lines+markers", line=dict(color="#1E40AF", width=2.5),
            marker=dict(size=7),
        ))
    fig3.update_layout(
        barmode="stack", height=320,
        paper_bgcolor="white", plot_bgcolor="#f9fafb",
        xaxis_title="Date", yaxis_title="Calls",
        legend=dict(orientation="h", yanchor="bottom", y=1, x=0),
        margin=dict(l=10, r=10, t=40, b=20),
    )
    st.plotly_chart(fig3, use_container_width=True)

    #  Row 2: location bar + callbacks per location 
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("### Call Volume by Showroom Location")
        fig4 = px.bar(
            loc.head(10), x="location_label", y="calls",
            color="hot_rate",
            color_continuous_scale=["#BFDBFE", "#1D4ED8"],
            text="calls",
            labels={"calls": "Calls", "location_label": "", "hot_rate": "Hot %"},
        )
        fig4.update_traces(textposition="outside")
        fig4.update_layout(
            height=320, paper_bgcolor="white", plot_bgcolor="#f9fafb",
            xaxis_tickangle=-30, margin=dict(l=10, r=10, t=20, b=60),
            coloraxis_showscale=True,
        )
        st.plotly_chart(fig4, use_container_width=True)

    with col_d:
        st.markdown("### Hot-Lead Rate by Location (%)")
        fig5 = px.bar(
            loc.head(10).sort_values("hot_rate", ascending=False),
            x="location_label", y="hot_rate",
            color="hot_rate",
            color_continuous_scale=["#FEF3C7", "#DC2626"],
            text=loc.head(10).sort_values("hot_rate", ascending=False)["hot_rate"].apply(
                lambda x: f"{x:.1f}%"),
            labels={"hot_rate": "Hot Lead %", "location_label": ""},
        )
        fig5.update_traces(textposition="outside")
        fig5.update_layout(
            height=320, paper_bgcolor="white", plot_bgcolor="#f9fafb",
            xaxis_tickangle=-30, margin=dict(l=10, r=10, t=20, b=60),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig5, use_container_width=True)

    #  Connectivity score histogram 
    col_e, col_f = st.columns(2)

    with col_e:
        st.markdown("### Customer Connectivity Score Distribution")
        fig6 = px.histogram(
            cust, x="connectivity_score", nbins=20,
            color="segment", color_discrete_map=SEGMENT_COLORS,
            labels={"connectivity_score": "Connectivity Score (0–100)"},
            barmode="overlay", opacity=0.75,
        )
        fig6.update_layout(
            height=300, paper_bgcolor="white", plot_bgcolor="#f9fafb",
            margin=dict(l=10, r=10, t=20, b=20),
        )
        st.plotly_chart(fig6, use_container_width=True)

    with col_f:
        st.markdown("### Calls per Customer Distribution")
        fig7 = px.histogram(
            cust, x="total_calls", nbins=10,
            color_discrete_sequence=[COLORS["primary"]],
            labels={"total_calls": "Number of Calls"},
        )
        fig7.update_layout(
            height=300, paper_bgcolor="white", plot_bgcolor="#f9fafb",
            margin=dict(l=10, r=10, t=20, b=20),
        )
        st.plotly_chart(fig7, use_container_width=True)

    #  Model interest breakdown 
    st.markdown("### Customer Interest by Car Model")
    model_interest = cust["models_interest"].value_counts().reset_index()
    model_interest.columns = ["model", "customers"]
    fig8 = px.bar(
        model_interest.head(10), x="model", y="customers",
        color="customers",
        color_continuous_scale=["#BFDBFE", "#1D4ED8"],
        text="customers",
        labels={"model": "Model", "customers": "Customers Interested"},
    )
    fig8.update_traces(textposition="outside")
    fig8.update_layout(
        height=300, paper_bgcolor="white", plot_bgcolor="#f9fafb",
        coloraxis_showscale=False, margin=dict(l=10, r=10, t=20, b=20),
    )
    st.plotly_chart(fig8, use_container_width=True)

    #  Customer details table 
    with st.expander("View Customer Engagement Detail Table"):
        show = cust[[
            "sales_customer_master_id", "total_calls", "callbacks_sched",
            "callback_rate", "dominant_lead_type", "contact_span_days",
            "connectivity_score", "segment",
        ]].rename(columns={
            "sales_customer_master_id": "Customer ID",
            "total_calls": "Total Calls",
            "callbacks_sched": "Callbacks Scheduled",
            "callback_rate": "Callback Rate %",
            "dominant_lead_type": "Lead Type",
            "contact_span_days": "Contact Span (Days)",
            "connectivity_score": "Connectivity Score",
            "segment": "Segment",
        })

        def _style(row):
            c = {"Highly Engaged": "#dcfce7",
                 "Moderately Engaged": "#fef9c3",
                 "Low Engagement": "#fee2e2"}.get(row["Segment"], "white")
            return [f"background-color: {c}"] * len(row)

        st.dataframe(
            show.style.apply(_style, axis=1).format(
                {"Callback Rate %": "{:.1f}", "Connectivity Score": "{:.1f}"}
            ),
            use_container_width=True, height=400,
        )

    #  AI Insights 
    st.markdown("---")
    st.markdown("### AI-Generated Executive Insights")

    if "conn_ai_insight" not in st.session_state:
        st.session_state.conn_ai_insight = None

    if api_key:
        if st.button("Generate AI Insights for Customer Connectivity", key="btn_conn_ai"):
            with st.spinner("Analysing connectivity data with Claude AI…"):
                try:
                    import os
                    os.environ["ANTHROPIC_API_KEY"] = api_key
                    from pipeline.ai_insights import get_connectivity_insights
                    st.session_state.conn_ai_insight = get_connectivity_insights(cust, ts, ltd)
                except Exception as e:
                    st.error(f"Claude API error: {e}")
    else:
        st.info("Enter your Anthropic API key in the sidebar to unlock AI insights.")

    if st.session_state.conn_ai_insight:
        st.markdown(
            f"""<div style='background:#FFFFFF;border-radius:6px;padding:24px;
                border:1px solid #E2E8F0;border-left:3px solid #1D4ED8;
                color:#1E293B;font-size:14px;line-height:1.7;'>
            {st.session_state.conn_ai_insight.replace(chr(10),'<br>')}
            </div>""",
            unsafe_allow_html=True,
        )
