"""EDA + data cleaning for all three CSV files.

Steps
-----
1. Replace string 'NULL' with NaN
2. Parse date/datetime columns
3. Strip whitespace from string columns
4. Drop full-duplicate rows
5. Encode categorical IDs → human-readable labels
6. Derive helper columns (age_days, lead_type_label, …)
"""

import pandas as pd
import numpy as np
from utils.helpers import label_model, label_source, label_agent

NULL_VALUES = {"NULL", "null", "None", "none", "N/A", "n/a", ""}

DATE_COLS_LEADS = ["created_at", "updated_at", "last_followup_date",
                   "appointment_date", "date_of_purchase"]
DATE_COLS_CALLS = ["created_at", "updated_at", "call_back_date"]
DATE_COLS_TD    = ["created_at", "updated_at", "appointment_date",
                   "test_drive_date", "test_drive_from",
                   "test_drive_completetion_date"]


def _replace_nulls(df: pd.DataFrame) -> pd.DataFrame:
    df = df.replace(list(NULL_VALUES), np.nan)
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip().replace(list(NULL_VALUES), np.nan)
    return df


def _parse_dates(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _eda_summary(df: pd.DataFrame, name: str) -> dict:
    total = len(df)
    missing_pct = (df.isna().sum() / total * 100).round(1)
    duplicates = df.duplicated().sum()
    numeric_stats = df.select_dtypes(include=[np.number]).describe().to_dict()
    return {
        "name":          name,
        "total_rows":    total,
        "total_cols":    len(df.columns),
        "duplicates":    int(duplicates),
        "missing_pct":   missing_pct[missing_pct > 0].to_dict(),
        "numeric_stats": numeric_stats,
    }


def clean_leads(df: pd.DataFrame):
    df = df.copy()
    df = _replace_nulls(df)
    eda = _eda_summary(df, "leads")

    df = _parse_dates(df, DATE_COLS_LEADS)
    df = df.drop_duplicates()

    # human-readable labels
    df["model_name"]   = df["model_id"].astype(str).apply(label_model)
    df["source_name"]  = df["lead_source_id"].astype(str).apply(label_source)
    df["status_label"] = df["status"].apply(
        lambda x: {"1": "Active", "3": "Converted/Closed"}.get(str(x).split(".")[0], "Unknown")
    )
    df["lead_type_label"] = df["lead_type"].astype(str).map(
        {"1": "Inbound", "2": "Outbound"}
    ).fillna("Unknown")
    # test_drive_status stored as float (0.0 / 1.0) — normalise before map
    td_norm = df["test_drive_status"].apply(
        lambda x: str(int(float(x))) if x is not None and str(x) not in ("nan", "NULL", "") else None
    )
    df["td_status_label"] = td_norm.map({"0": "Not Taken", "1": "Taken"}).fillna("Pending")

    # derived metrics
    ref_date = df["created_at"].max()
    df["lead_age_days"] = (ref_date - df["created_at"]).dt.days.fillna(0).astype(int)
    # status is stored as float (1.0 / 3.0) in some rows — normalise
    df["converted"] = df["status"].apply(
        lambda x: 1 if str(x).split(".")[0] == "3" else 0
    )

    return df, eda


def clean_calls(df: pd.DataFrame):
    df = df.copy()
    df = _replace_nulls(df)
    eda = _eda_summary(df, "calls")

    df = _parse_dates(df, DATE_COLS_CALLS)
    df = df.drop_duplicates()

    df["agent_name"]   = df["created_by"].astype(str).apply(label_agent)
    df["model_name"]   = df["intrested_model_id"].astype(str).apply(label_model)
    df["lead_type"]    = df["lead_type"].fillna("Unknown")
    df["has_callback"] = df["is_callback"].astype(str).isin(["y", "1", "yes"]).astype(int)

    # date parts for time-series
    df["call_date"]  = df["created_at"].dt.date
    df["call_month"] = df["created_at"].dt.to_period("M").astype(str)

    # lead_type clean
    df["lead_type"] = df["lead_type"].str.strip().str.title()
    df.loc[~df["lead_type"].isin(["Hot", "Warm", "Cold"]), "lead_type"] = "Unknown"

    return df, eda


def clean_testdrives(df: pd.DataFrame):
    df = df.copy()
    df = _replace_nulls(df)
    eda = _eda_summary(df, "testdrives")

    df = _parse_dates(df, DATE_COLS_TD)
    df = df.drop_duplicates()

    df["model_name"]   = df["model_id"].astype(str).apply(label_model)
    df["agent_name"]   = df["first_agent"].astype(str).apply(label_agent)
    df["td_completed"] = (df["appointment_status"].astype(str) == "1").astype(int)

    return df, eda
