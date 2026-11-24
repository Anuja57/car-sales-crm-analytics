import json
import numpy as np
import pandas as pd


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, pd.Timestamp):
            return str(obj)
        return super().default(obj)


def df_to_records(df: pd.DataFrame) -> list:
    """Convert DataFrame to JSON-safe list of dicts."""
    return json.loads(json.dumps(df.to_dict("records"), cls=NumpyEncoder))


def safe_dict(d: dict) -> dict:
    """Recursively make a dict JSON-safe."""
    return json.loads(json.dumps(d, cls=NumpyEncoder))
