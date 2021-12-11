import pandas as pd


def infer_dtype(series):
    if pd.api.types.infer_dtype(series) == "string":
        return "category"
    else:
        return "value"
