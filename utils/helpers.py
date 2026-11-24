"""Shared constants, mappings, and utility functions."""

#  Model ID → Name mapping (Jeep India lineup) 
MODEL_MAP = {
    "60": "Renegade", "64": "Compass (Sport)", "65": "Compass X",
    "69": "Wrangler", "70": "Meridian (D)", "72": "Meridian (P)",
    "73": "Compass", "74": "Meridian", "76": "Grand Cherokee",
    "77": "Grand Cherokee L", "81": "4xe",
}

#  Lead-source ID → Label 
LEAD_SOURCE_MAP = {
    "3":  "Walk-In",       "4":  "Phone Call",     "6":  "Website",
    "10": "Other",         "15": "Social Media",   "18": "Digital Campaign",
    "23": "Referral",      "29": "Event",          "30": "Email",
    "34": "WhatsApp",
}

#  Lead status 
LEAD_STATUS_MAP = {"1": "Active", "3": "Converted / Closed"}

#  Agent ID → short display name 
AGENT_NAMES = {
    "7200204": "Agent Arjun",  "7200205": "Agent Sneha",
    "7200207": "Agent Vikram", "7200209": "Agent Priya",
    "7200210": "Agent Rohan",  "7200212": "Agent Meera",
    "7200222": "Agent Kabir",  "7200223": "Agent Disha",
    "7200224": "Agent Ankit",  "7200225": "Agent Pooja",
    "7200226": "Agent Rahul",
}

#  Dashboard colour palette 
COLORS = {
    "primary":   "#2563EB",
    "success":   "#16A34A",
    "warning":   "#D97706",
    "danger":    "#DC2626",
    "info":      "#0891B2",
    "purple":    "#7C3AED",
    "high":      "#16A34A",
    "medium":    "#D97706",
    "low":       "#DC2626",
    "chart":     ["#2563EB", "#16A34A", "#D97706", "#DC2626",
                  "#7C3AED", "#0891B2", "#DB2777", "#65A30D",
                  "#EA580C", "#6366F1", "#14B8A6"],
}

TIER_COLORS = {"High": "#16A34A", "Medium": "#D97706", "Low": "#DC2626"}
SEGMENT_COLORS = {
    "Highly Engaged":     "#16A34A",
    "Moderately Engaged": "#D97706",
    "Low Engagement":     "#DC2626",
}


def label_model(mid: str) -> str:
    return MODEL_MAP.get(str(mid), f"Model-{mid}") if mid and mid not in ("NULL", "", "nan") else "Unknown"


def label_source(sid: str) -> str:
    return LEAD_SOURCE_MAP.get(str(sid), f"Source-{sid}") if sid and sid not in ("NULL", "", "nan") else "Unknown"


def label_agent(aid) -> str:
    if aid is None or str(aid) in ("NULL", "", "nan", "None", "nan"):
        return "Unknown"
    # convert float IDs like 7200223.0 → "7200223"
    try:
        key = str(int(float(aid)))
    except (ValueError, TypeError):
        key = str(aid)
    return AGENT_NAMES.get(key, f"Agt-{key[-3:]}")
