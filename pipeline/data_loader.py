"""Load and lightly validate the three CRM CSV files."""

import pandas as pd
import io
from typing import Tuple, Optional

REQUIRED_COLS = {
    "leads": {"id", "mobile_no", "model_id", "lead_source_id",
              "lead_type", "status", "test_drive_status", "created_at"},
    "calls": {"id", "sales_customer_master_id", "connected_phone",
              "intrested_model_id", "lead_type", "disposition_id",
              "is_callback", "showroom_location_id", "created_by",
              "created_at", "call_back_date"},
    "testdrives": {"id", "sales_customer_master_id", "sales_completed_calls_id",
                   "appointment_status", "appointment_date", "first_agent",
                   "test_drive_date", "created_at"},
}


def _load(source) -> pd.DataFrame:
    """Accept a file path (str/Path) or a Streamlit UploadedFile."""
    if hasattr(source, "read"):
        content = source.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="replace")
        return pd.read_csv(io.StringIO(content), low_memory=False)
    return pd.read_csv(source, low_memory=False)


def _check_cols(df: pd.DataFrame, name: str) -> Tuple[bool, list]:
    missing = REQUIRED_COLS[name] - set(df.columns)
    return len(missing) == 0, list(missing)


def load_data(
    leads_src, calls_src, testdrives_src
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    """Return (leads_df, calls_df, testdrives_df, info_dict)."""
    leads = _load(leads_src)
    calls = _load(calls_src)
    td    = _load(testdrives_src)

    info = {
        "leads_rows":    len(leads),
        "calls_rows":    len(calls),
        "testdrive_rows": len(td),
        "leads_cols":    len(leads.columns),
        "calls_cols":    len(calls.columns),
        "testdrive_cols": len(td.columns),
    }

    for df, name in [(leads, "leads"), (calls, "calls"), (td, "testdrives")]:
        ok, missing = _check_cols(df, name)
        if not ok:
            info[f"{name}_missing_cols"] = missing

    return leads, calls, td, info
