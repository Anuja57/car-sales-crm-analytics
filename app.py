"""
CRM Analytics AI - Main Streamlit Application
AI-Based Data Analytics for CRM Optimization: Driving Car Sales Success
"""

import sys, os
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="CRM Analytics AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

from pipeline.data_loader   import load_data
from pipeline.data_cleaner  import clean_leads, clean_calls, clean_testdrives
from pipeline.ml_engine     import (analyze_agent_performance,
                                    analyze_customer_connectivity,
                                    analyze_lead_conversion)
from dashboards.agent_performance     import render_agent_dashboard
from dashboards.customer_connectivity import render_connectivity_dashboard
from dashboards.lead_conversion       import render_lead_dashboard

# ── HTML ✕ removal handler ────────────────────────────────────────────────────
if "remove" in st.query_params:
    _slot = st.query_params.get("remove", "")
    if _slot in ("slot_leads", "slot_calls", "slot_td"):
        st.session_state[_slot] = None
    st.query_params.clear()
    st.rerun()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons+Round');

/* ── Base typography ── */
html, body, [class*="css"], .stMarkdown,
.stTextInput, .stButton, .stSelectbox, .stMetric, [data-baseweb="tab"],
h1, h2, h3, h4, h5, h6, p, span, div, label, button, table, th, td {
    font-family: "Poppins", sans-serif !important;
    letter-spacing: -0.01em;
}

/* ── Box model (prevents content from spilling outside containers) ── */
*, *::before, *::after { box-sizing: border-box; }

/* ── Page background ── */
.stApp, [data-testid="stAppViewContainer"] {
    background: #F1F5F9;
}
[data-testid="block-container"] {
    padding-top: 1.5rem;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgb(240, 253, 244);
    border-right: 1px solid #E2E8F0;
    min-width: 280px !important;
    max-width: 280px !important;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #14532D !important; }
[data-testid="stSidebar"] .stFileUploader label { color: #14532D !important; }
[data-testid="stSidebar"] hr { border-color: #BBF7D0; }

/* ── Header ── */
.crm-header {
    background: rgb(240, 253, 244);
    border-radius: 6px;
    padding: 22px 28px;
    margin-bottom: 20px;
}
.crm-header h1 {
    color: #14532D !important;
    font-size: 1.6rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.03em;
}
.crm-header p {
    color: #166534 !important;
    margin: 5px 0 0;
    font-size: 0.85rem;
    font-weight: 400;
    letter-spacing: 0.01em;
}

/* ── Tabs ── */
[data-baseweb="tab"] {
    font-size: 14px;
    font-weight: 500;
    color: #64748B;
}
[aria-selected="true"] { color: #1D4ED8 !important; font-weight: 600 !important; }

/* ── Section headings ── */
h2 { color: #0F172A !important; font-weight: 700; font-size: 1.25rem !important; }
h3 { color: #1E293B !important; font-weight: 600; font-size: 1rem !important;
     text-transform: uppercase; letter-spacing: 0.05em; margin-top: 1.5rem !important; }

/* ── Welcome card ── */
.welcome-card {
    background: #FFFFFF;
    border-radius: 6px;
    padding: 40px;
    border: 1px solid #E2E8F0;
    text-align: center;
    margin-top: 20px;
}

/* ── Metric widget ── */
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 14px 18px;
}
[data-testid="stMetricLabel"] { color: #64748B !important; font-size: 12px !important;
    font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.06em;
    white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }
[data-testid="stMetricValue"] { color: #0F172A !important; font-size: 1.6rem !important;
    font-weight: 700 !important; white-space: nowrap !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid #E2E8F0; border-radius: 6px; }

/* ── Expander ── */
[data-testid="stExpander"] { border: 1px solid #E2E8F0 !important;
    border-radius: 6px !important; background: white; }

/* ── Success / info banners ── */
[data-testid="stAlert"] { border-radius: 6px !important; }

/* ── Fix: keyboard_double… raw text — hide collapse control and icon spans ── */
button[kind="header"] {
    display: none !important;
}
span.material-icons,
span.material-icons-rounded,
span.material-icons-outlined,
span.material-icons-sharp {
    display: none !important;
}
[data-testid="collapsedControl"] {
    display: none !important;
}

/* ── File slot: the green row is pure HTML — no Streamlit button involved ── */
</style>
""", unsafe_allow_html=True)


# ── File slot helper ─────────────────────────────────────────────────────────
def _file_slot(label, slot_key, uploader_key):
    """Show uploader or a filename badge with a remove button."""
    if st.session_state.get(slot_key) is None:
        f = st.file_uploader(label, type=["csv"], key=uploader_key)
        if f:
            st.session_state[slot_key] = f
            st.rerun()
        return None
    else:
        fname = st.session_state[slot_key].name
        st.markdown(f"""
<p style='color:#14532D;font-size:12px;font-weight:600;margin:0 0 3px;'>{label}</p>
<div style='background:#DCFCE7;border-radius:6px;padding:7px 10px;
            display:flex;align-items:center;justify-content:space-between;
            gap:8px;margin-bottom:4px;'>
  <span style='font-size:13px;color:#14532D;font-weight:500;
               white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
               flex:1;min-width:0;' title='{fname}'>{fname}</span>
  <span onclick="window.location.href='?remove={slot_key}'"
        onmouseover="this.style.color='#DC2626'"
        onmouseout="this.style.color='#14532D'"
        style='font-size:14px;color:#14532D;cursor:pointer;
               font-weight:500;flex-shrink:0;line-height:1;'>✕</span>
</div>""", unsafe_allow_html=True)
        return st.session_state[slot_key]


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## CRM Analytics AI")
    st.markdown("---")
    st.markdown("### Upload Data Files")

    leads_file = _file_slot("Leads CSV",               "slot_leads", "up_leads")
    calls_file = _file_slot("Sales Completed Calls CSV","slot_calls", "up_calls")
    td_file    = _file_slot("Test Drive Details CSV",   "slot_td",    "up_td")

    st.markdown("---")
    st.markdown("### AI Insights (Optional)")
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Required to generate Claude AI narrative insights on each dashboard.",
    )

    st.markdown("---")
    analyse_btn = st.button("Run Analysis", type="primary", use_container_width=True)

    st.markdown("---")
    if st.button("Reset / Clear", use_container_width=True):
        for k in ["slot_leads", "slot_calls", "slot_td",
                  "analysis_done", "agent_results", "conn_results",
                  "conv_results", "load_info", "leads_eda", "calls_eda", "td_eda",
                  "agent_ai_insight", "conn_ai_insight", "lead_ai_insight"]:
            st.session_state.pop(k, None)
        st.rerun()



# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='crm-header'>
  <h1>AI-Based CRM Analytics Dashboard</h1>
</div>
""", unsafe_allow_html=True)


# ── Main logic ────────────────────────────────────────────────────────────────
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if not (leads_file and calls_file and td_file):
    st.markdown("""
<div class='welcome-card'>
  <h2 style='color:#1e40af;'>Welcome to CRM Analytics AI</h2>
  <p style='color:#4b5563;font-size:1.05rem;max-width:640px;margin:12px auto 0;'>
    Upload your three CRM CSV files in the sidebar to start the <b>AI-driven analysis pipeline</b>.
  </p>
  <br>
  <div style='display:flex;justify-content:center;gap:30px;flex-wrap:wrap;margin-top:10px;'>
    <div style='background:#eff6ff;border-radius:10px;padding:16px 24px;width:180px;'>
      <b style='color:#1e40af;'>Agent Performance</b>
      <p style='color:#6b7280;font-size:13px;margin:4px 0 0;'>
        Ranks agents by calls, lead quality &amp; test-drive results
      </p>
    </div>
    <div style='background:#f0fdf4;border-radius:10px;padding:16px 24px;width:180px;'>
      <b style='color:#166534;'>Customer Connectivity</b>
      <p style='color:#6b7280;font-size:13px;margin:4px 0 0;'>
        Evaluates engagement, reach &amp; call patterns
      </p>
    </div>
    <div style='background:#fff7ed;border-radius:10px;padding:16px 24px;width:180px;'>
      <b style='color:#92400e;'>Lead Conversion</b>
      <p style='color:#6b7280;font-size:13px;margin:4px 0 0;'>
        ML-scores leads &amp; spots highest-potential opportunities
      </p>
    </div>
  </div>
  <br>
  <p style='color:#9ca3af;font-size:13px;'>
    Upload <b>leads.csv</b>, <b>sales_completed_calls.csv</b>
    and <b>sales_test_drive_details.csv</b> in the sidebar to begin.
  </p>
</div>
""", unsafe_allow_html=True)
    st.stop()

if analyse_btn or st.session_state.analysis_done:

    if not st.session_state.analysis_done:
        with st.spinner("Loading and validating CSV files..."):
            leads_raw, calls_raw, td_raw, load_info = load_data(
                leads_file, calls_file, td_file
            )

        with st.spinner("Running EDA and cleaning data..."):
            leads_clean, leads_eda = clean_leads(leads_raw)
            calls_clean, calls_eda = clean_calls(calls_raw)
            td_clean,    td_eda    = clean_testdrives(td_raw)

        with st.spinner("Applying ML models (K-Means + Random Forest)..."):
            agent_results = analyze_agent_performance(calls_clean, td_clean)
            conn_results  = analyze_customer_connectivity(calls_clean)
            conv_results  = analyze_lead_conversion(leads_clean, calls_clean)

        st.session_state.update({
            "analysis_done": True,
            "agent_results": agent_results,
            "conn_results":  conn_results,
            "conv_results":  conv_results,
            "load_info":     load_info,
            "leads_eda":     leads_eda,
            "calls_eda":     calls_eda,
            "td_eda":        td_eda,
        })

        st.success("Analysis complete! Explore the dashboards below.")

    agent_results = st.session_state.agent_results
    conn_results  = st.session_state.conn_results
    conv_results  = st.session_state.conv_results
    load_info     = st.session_state.load_info

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Leads Loaded",       f"{load_info['leads_rows']:,}")
    with c2:
        st.metric("Calls Loaded",       f"{load_info['calls_rows']:,}")
    with c3:
        st.metric("Test Drive Records", f"{load_info['testdrive_rows']:,}")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Agent Performance",
        "Customer Connectivity",
        "Lead Conversion",
        "EDA Summary",
    ])

    with tab1:
        render_agent_dashboard(agent_results, api_key=api_key)

    with tab2:
        render_connectivity_dashboard(conn_results, api_key=api_key)

    with tab3:
        render_lead_dashboard(conv_results, api_key=api_key)

    with tab4:
        st.markdown("## EDA & Data Quality Summary")
        st.markdown("Auto-generated exploratory data analysis performed before ML pipeline.")

        for eda in [st.session_state.leads_eda,
                    st.session_state.calls_eda,
                    st.session_state.td_eda]:
            name = eda["name"].replace("_", " ").title()
            with st.expander(f"{name} — {eda['total_rows']:,} rows x {eda['total_cols']} columns"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Rows",            f"{eda['total_rows']:,}")
                col2.metric("Total Columns",          eda['total_cols'])
                col3.metric("Duplicate Rows Removed", eda['duplicates'])

                if eda["missing_pct"]:
                    import pandas as pd
                    mp = pd.DataFrame.from_dict(
                        eda["missing_pct"], orient="index", columns=["Missing %"]
                    ).sort_values("Missing %", ascending=False).head(15)
                    st.markdown("**Top Columns with Missing Data:**")
                    import plotly.express as px
                    fig = px.bar(
                        mp.reset_index(), x="index", y="Missing %",
                        color="Missing %",
                        color_continuous_scale=["#FEF9C3", "#DC2626"],
                        labels={"index": "Column"},
                    )
                    fig.update_layout(
                        height=280, paper_bgcolor="white", plot_bgcolor="#f9fafb",
                        margin=dict(l=10, r=10, t=10, b=80),
                        xaxis_tickangle=-40, coloraxis_showscale=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.success("No missing data detected in this file.")
