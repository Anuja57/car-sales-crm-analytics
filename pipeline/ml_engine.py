"""
ML Engine — three independent analyses:

1. agent_performance   → K-Means clustering + composite score
2. customer_connectivity → Engagement scoring + segmentation
3. lead_conversion      → Random Forest scoring + funnel analysis
"""

import warnings
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.impute import SimpleImputer

warnings.filterwarnings("ignore")


# 
# 1. AGENT PERFORMANCE
# 

def analyze_agent_performance(calls_df: pd.DataFrame,
                               td_df: pd.DataFrame) -> dict:
    """
    Returns:
        agent_metrics  – DataFrame with per-agent KPIs, tier, score, rank
        feature_cols   – list of metric column names used for ML
    """
    calls = calls_df.copy()
    td    = td_df.copy()

    #  per-agent call metrics 
    agg = calls.groupby("agent_name").agg(
        total_calls     = ("id", "count"),
        hot_leads       = ("lead_type", lambda x: (x == "Hot").sum()),
        warm_leads      = ("lead_type", lambda x: (x == "Warm").sum()),
        cold_leads      = ("lead_type", lambda x: (x == "Cold").sum()),
        callbacks_sched = ("has_callback", "sum"),
        unique_customers= ("sales_customer_master_id", "nunique"),
        models_handled  = ("model_name", "nunique"),
    ).reset_index()

    #  test-drive stats per agent 
    td_agg = td.groupby("agent_name").agg(
        test_drives_assigned = ("id", "count"),
        test_drives_completed= ("td_completed", "sum"),
    ).reset_index()

    agent_metrics = agg.merge(td_agg, on="agent_name", how="left")
    agent_metrics["test_drives_assigned"]  = agent_metrics["test_drives_assigned"].fillna(0)
    agent_metrics["test_drives_completed"] = agent_metrics["test_drives_completed"].fillna(0)

    #  derived KPIs 
    tc = agent_metrics["total_calls"].replace(0, np.nan)
    agent_metrics["hot_lead_ratio"]       = (agent_metrics["hot_leads"] / tc * 100).round(1)
    agent_metrics["callback_rate"]        = (agent_metrics["callbacks_sched"] / tc * 100).round(1)
    agent_metrics["td_conversion_rate"]   = (
        agent_metrics["test_drives_completed"] /
        agent_metrics["test_drives_assigned"].replace(0, np.nan) * 100
    ).round(1)
    agent_metrics = agent_metrics.fillna(0)

    #  ML: K-Means clustering (High / Medium / Low) 
    feature_cols = ["total_calls", "hot_lead_ratio", "callback_rate",
                    "test_drives_assigned", "td_conversion_rate",
                    "unique_customers"]

    X = agent_metrics[feature_cols].values
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    n_clusters = min(3, len(agent_metrics))
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    agent_metrics["cluster"] = km.fit_predict(X_scaled)

    #  composite score (weighted) 
    weights = np.array([0.25, 0.20, 0.15, 0.20, 0.15, 0.05])
    agent_metrics["composite_score"] = (X_scaled * weights).sum(axis=1)
    agent_metrics["composite_score"] = (
        agent_metrics["composite_score"] / agent_metrics["composite_score"].max() * 100
    ).round(1)

    #  assign tier labels based on composite score percentile 
    q67 = agent_metrics["composite_score"].quantile(0.67)
    q33 = agent_metrics["composite_score"].quantile(0.33)

    def tier(score):
        if score >= q67:
            return "High"
        elif score >= q33:
            return "Medium"
        return "Low"

    agent_metrics["tier"] = agent_metrics["composite_score"].apply(tier)
    agent_metrics["rank"] = agent_metrics["composite_score"].rank(
        ascending=False, method="min"
    ).astype(int)
    agent_metrics = agent_metrics.sort_values("rank")

    return {"agent_metrics": agent_metrics, "feature_cols": feature_cols}


# 
# 2. CUSTOMER CONNECTIVITY
# 

def analyze_customer_connectivity(calls_df: pd.DataFrame) -> dict:
    """
    Returns:
        customer_metrics  – per-customer engagement stats + segment
        time_series       – daily call volume
        location_stats    – calls by showroom location
        lead_type_dist    – overall Hot/Warm/Cold distribution
    """
    calls = calls_df.copy()

    #  per-customer aggregation 
    cust = calls.groupby("sales_customer_master_id").agg(
        total_calls     = ("id", "count"),
        callbacks_sched = ("has_callback", "sum"),
        lead_types      = ("lead_type", lambda x: list(x)),
        models_interest = ("model_name", lambda x: x.mode().iloc[0] if len(x) > 0 else "Unknown"),
        first_contact   = ("created_at", "min"),
        last_contact    = ("created_at", "max"),
    ).reset_index()

    cust["callback_rate"]   = (cust["callbacks_sched"] / cust["total_calls"] * 100).round(1)
    cust["contact_span_days"] = (
        cust["last_contact"] - cust["first_contact"]
    ).dt.days.fillna(0).astype(int)

    # dominant lead type
    def _dominant(lt_list):
        from collections import Counter
        c = Counter([x for x in lt_list if x not in ("Unknown",)])
        return c.most_common(1)[0][0] if c else "Unknown"

    cust["dominant_lead_type"] = cust["lead_types"].apply(_dominant)

    # connectivity score: multi-call customers + callbacks + lead_type weight
    lt_weight = {"Hot": 3, "Warm": 2, "Cold": 1, "Unknown": 1}
    cust["lt_score"] = cust["dominant_lead_type"].map(lt_weight).fillna(1)
    cust["conn_score_raw"] = (
        cust["total_calls"] * 0.4 +
        cust["callback_rate"] * 0.3 +
        cust["lt_score"] * 10 * 0.3
    )
    mx = cust["conn_score_raw"].max()
    cust["connectivity_score"] = (cust["conn_score_raw"] / mx * 100).round(1) if mx > 0 else 0

    # segment
    q67 = cust["connectivity_score"].quantile(0.67)
    q33 = cust["connectivity_score"].quantile(0.33)

    def segment(s):
        if s >= q67:
            return "Highly Engaged"
        elif s >= q33:
            return "Moderately Engaged"
        return "Low Engagement"

    cust["segment"] = cust["connectivity_score"].apply(segment)

    #  time series 
    ts = calls.groupby("call_date").agg(
        call_count      = ("id", "count"),
        hot_calls       = ("lead_type", lambda x: (x == "Hot").sum()),
        warm_calls      = ("lead_type", lambda x: (x == "Warm").sum()),
        cold_calls      = ("lead_type", lambda x: (x == "Cold").sum()),
        callbacks_sched = ("has_callback", "sum"),
    ).reset_index()
    ts["call_date"] = pd.to_datetime(ts["call_date"])
    ts = ts.sort_values("call_date")

    #  location stats 
    loc = calls.groupby("showroom_location_id").agg(
        calls       = ("id", "count"),
        hot_calls   = ("lead_type", lambda x: (x == "Hot").sum()),
        callbacks   = ("has_callback", "sum"),
    ).reset_index()
    loc["location_label"] = "Location-" + loc["showroom_location_id"].astype(str)
    loc["hot_rate"]        = (loc["hot_calls"] / loc["calls"] * 100).round(1)
    loc = loc.sort_values("calls", ascending=False)

    #  overall lead-type distribution 
    ltd = calls["lead_type"].value_counts().reset_index()
    ltd.columns = ["lead_type", "count"]

    return {
        "customer_metrics": cust,
        "time_series":       ts,
        "location_stats":    loc,
        "lead_type_dist":    ltd,
    }


# 
# 3. LEAD CONVERSION
# 

def analyze_lead_conversion(leads_df: pd.DataFrame,
                             calls_df: pd.DataFrame) -> dict:
    """
    Returns:
        leads_scored      – leads with ML conversion probability + score tier
        feature_importance– dict of feature → importance
        model_report      – classification_report as str
        funnel            – conversion funnel counts
        source_stats      – conversion by lead source
        model_stats       – interest by car model
        rf_model          – trained model (for live scoring)
    """
    leads = leads_df.copy()

    #  feature engineering 
    leads["model_id_enc"]  = pd.factorize(leads["model_id"].astype(str))[0]
    leads["source_id_enc"] = pd.factorize(leads["lead_source_id"].astype(str))[0]
    leads["lead_type_enc"] = pd.factorize(leads["lead_type_label"].astype(str))[0]
    leads["td_taken"]      = (leads["td_status_label"] == "Taken").astype(int)
    leads["state_enc"]     = pd.factorize(leads["state_id"].astype(str))[0]

    # rule-based features
    leads["is_hot_inbound"] = (
        (leads["lead_type_label"] == "Inbound") &
        (leads["td_status_label"] == "Taken")
    ).astype(int)

    feature_cols = ["model_id_enc", "source_id_enc", "lead_type_enc",
                    "td_taken", "state_enc", "lead_age_days", "is_hot_inbound"]

    X = leads[feature_cols].fillna(0)
    y = leads["converted"]   # 0=Active, 1=Converted

    #  Random Forest 
    imp = SimpleImputer(strategy="median")
    X_imp = imp.fit_transform(X)

    rf_report = ""
    if y.nunique() >= 2 and len(X_imp) >= 20:
        X_tr, X_te, y_tr, y_te = train_test_split(
            X_imp, y, test_size=0.2, random_state=42, stratify=y
        )
        rf = RandomForestClassifier(n_estimators=150, random_state=42,
                                     class_weight="balanced", max_depth=6)
        rf.fit(X_tr, y_tr)
        y_pred = rf.predict(X_te)
        rf_report = classification_report(y_te, y_pred, zero_division=0)
        proba = rf.predict_proba(X_imp)
        conv_class_idx = list(rf.classes_).index(1) if 1 in rf.classes_ else 0
        leads["conversion_prob"] = proba[:, conv_class_idx]
        feature_importance = dict(zip(feature_cols, rf.feature_importances_))
        rf_model = rf
    else:
        # fallback: rule-based scoring
        leads["conversion_prob"] = (
            leads["td_taken"] * 0.5 +
            leads["is_hot_inbound"] * 0.3 +
            (leads["lead_age_days"] < 30).astype(int) * 0.2
        ).clip(0, 1)
        feature_importance = {c: 1.0 / len(feature_cols) for c in feature_cols}
        rf_model = None

    leads["conversion_prob"] = leads["conversion_prob"].round(3)

    #  score tiers 
    def score_tier(p):
        if p >= 0.65:
            return "High Potential"
        elif p >= 0.35:
            return "Medium Potential"
        return "Low Potential"

    leads["score_tier"] = leads["conversion_prob"].apply(score_tier)

    #  funnel 
    funnel = {
        "Total Leads":           len(leads),
        "Test Drive Taken":      int((leads["td_taken"] == 1).sum()),
        "Converted / Closed":    int(leads["converted"].sum()),
        "High Potential (Remaining)": int(
            ((leads["score_tier"] == "High Potential") & (leads["converted"] == 0)).sum()
        ),
    }

    #  source stats 
    src = leads.groupby("source_name").agg(
        total       = ("id", "count"),
        converted   = ("converted", "sum"),
        td_taken    = ("td_taken", "sum"),
        avg_prob    = ("conversion_prob", "mean"),
    ).reset_index()
    src["conversion_rate"] = (src["converted"] / src["total"] * 100).round(1)
    src = src.sort_values("total", ascending=False)

    #  model stats 
    mst = leads.groupby("model_name").agg(
        total       = ("id", "count"),
        converted   = ("converted", "sum"),
        td_taken    = ("td_taken", "sum"),
        avg_prob    = ("conversion_prob", "mean"),
    ).reset_index()
    mst["conversion_rate"] = (mst["converted"] / mst["total"] * 100).round(1)
    mst = mst.sort_values("total", ascending=False)

    return {
        "leads_scored":       leads,
        "feature_importance": feature_importance,
        "model_report":       rf_report,
        "funnel":             funnel,
        "source_stats":       src,
        "model_stats":        mst,
        "rf_model":           rf_model,
    }
