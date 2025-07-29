
import json
import numpy as np
import pandas as pd
from datetime import timedelta

def make_json_serializable(obj):
    """Convert object to JSON serializable format with enhanced NaN/infinity handling"""
    if isinstance(obj, dict):
        return {str(k): make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        # Handle NaN values in numpy arrays
        clean_list = []
        for item in obj.flatten():
            if isinstance(item, (np.floating, float)) and (np.isnan(item) or np.isinf(item)):
                clean_list.append(None)
            else:
                clean_list.append(make_json_serializable(item))
        return clean_list
    elif isinstance(obj, timedelta):
        return str(obj)
    elif pd.isna(obj):
        return None
    elif obj is None:
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
