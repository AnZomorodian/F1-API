
import json
import numpy as np
import pandas as pd
from datetime import timedelta

def make_json_serializable(obj):
    """Convert object to JSON serializable format"""
    if isinstance(obj, dict):
        return {str(k): make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, timedelta):
        return str(obj)
    elif pd.isna(obj):
        return None
    else:
        return obj

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle numpy and pandas types"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, timedelta):
            return str(obj)
        elif pd.isna(obj):
            return None
        return super().default(obj)
