from app.utils.general_utils import OPERATORS, AGGREGATION_FUNCTIONS
import pandas as pd
import multiprocessing as mp
import asyncio
from typing import List, Any, Dict

# def filter_data(df: pd.DataFrame, filters: List[Any]) -> pd.DataFrame:
#     # Try to use .query() if possible
#     try:
#         query_parts = []
#         for condition in filters:
#             col = condition["name"]
#             op = condition["operator"]
#             val = condition["value"]
#             if op == "contains":
#                 # fallback to mask for contains
#                 mask = pd.Series([True] * len(df))
#                 for condition in filters:
#                     op_func = OPERATORS[condition["operator"]]["action"]
#                     value = condition["value"]
#                     if condition["operator"] == "contains":
#                         mask &= op_func(df[condition["name"]].astype(str), str(value))
#                     else:
#                         try:
#                             value_cast = float(value)
#                         except (ValueError, TypeError):
#                             value_cast = value
#                         mask &= op_func(df[condition["name"]], value_cast)
#                 return df[mask]
#             else:
#                 # For numbers and equality
#                 if isinstance(val, str):
#                     val = f'"{val}"'
#                 query_parts.append(f"`{col}` {op} {val}")
#         query_str = " and ".join(query_parts)
#         return df.query(query_str)
#     except Exception:
#         # fallback to mask
#         mask = pd.Series([True] * len(df))
#         for condition in filters:
#             op_func = OPERATORS[condition["operator"]]["action"]
#             value = condition["value"]
#             if condition["operator"] == "contains":
#                 mask &= op_func(df[condition["name"]].astype(str), str(value))
#             else:
#                 try:
#                     value_cast = float(value)
#                 except (ValueError, TypeError):
#                     value_cast = value
#                 mask &= op_func(df[condition["name"]], value_cast)
#         return df[mask]
def filter_data(df: pd.DataFrame, filters: List[Any]) -> pd.DataFrame:
    numeric_ops = {"==", "!=", ">", "<", ">=", "<="}
    try:
        query_parts = []
        for condition in filters:
            col = condition["name"]
            op = condition["operator"]
            val = condition["value"]
            if op == "contains":
                # fallback to mask for contains
                mask = pd.Series([True] * len(df))
                for condition in filters:
                    op_func = OPERATORS[condition["operator"]]["action"]
                    value = condition["value"]
                    if condition["operator"] == "contains":
                        mask &= op_func(df[condition["name"]].astype(str), str(value))
                    elif condition["operator"] in numeric_ops:
                        col_numeric = pd.to_numeric(df[condition["name"]], errors='coerce')
                        try:
                            value_cast = float(value)
                        except (ValueError, TypeError):
                            value_cast = float('nan')
                        mask &= op_func(col_numeric, value_cast)
                    else:
                        mask &= op_func(df[condition["name"]], value)
                return df[mask]
            else:
                # For numbers and equality
                if isinstance(val, str):
                    val = f'"{val}"'
                query_parts.append(f"`{col}` {op} {val}")
        query_str = " and ".join(query_parts)
        return df.query(query_str)
    except Exception:
        # fallback to mask
        mask = pd.Series([True] * len(df))
        for condition in filters:
            op_func = OPERATORS[condition["operator"]]["action"]
            value = condition["value"]
            if condition["operator"] == "contains":
                mask &= op_func(df[condition["name"]].astype(str), str(value))
            elif condition["operator"] in numeric_ops:
                col_numeric = pd.to_numeric(df[condition["name"]], errors='coerce')
                try:
                    value_cast = float(value)
                except (ValueError, TypeError):
                    value_cast = float('nan')
                mask &= op_func(col_numeric, value_cast)
            else:
                mask &= op_func(df[condition["name"]], value)
        return df[mask]


def map_groupped_records(grouped_data: pd.core.groupby.generic.DataFrameGroupBy, map_property):
    """
    Map grouped records to a dictionary with group keys and their corresponding values.
    Parameters:
    - grouped_data: pd.core.groupby.generic.DataFrameGroupBy - The grouped DataFrame.
    - map_property: str - The property to map.
    Returns:
    - dict: A dictionary where keys are group keys and values are lists of mapped property values.
    """
    group_mapping = {}

    for group_key, group_df in grouped_data:
        # Extract the values of the property parameter for each group
        group_mapping[group_key] = group_df[map_property].tolist()

    return group_mapping


def group_data(df: pd.DataFrame, group_by_parameters: List[str]) -> pd.core.groupby.generic.DataFrameGroupBy:
    """
    Group data by specified parameter.
    Parameters:
    - df: pd.DataFrame - The input data.
    - group_by_parameters: List[str] - Parameters to group by.
    Returns:
    - pd.core.groupby.generic.DataFrameGroupBy: A DataFrameGroupBy object.
    """
    return df.groupby(group_by_parameters, dropna=True)

def aggregate_data(df: pd.DataFrame, aggregation_parameters: List[dict]) -> List[dict]:
    # Build aggregation dict for pandas
    agg_dict = {}
    transform_ops = {"unique", "mode", "range"}
    post_process = {}

    for param in aggregation_parameters:
        name = param["name"]
        ops = param["operations"]
        agg_ops = [op for op in ops if op not in transform_ops]
        if agg_ops:
            agg_dict[name] = agg_ops
        # Store transforms for post-processing
        post_process[name] = [op for op in ops if op in transform_ops]

    # Perform all standard aggregations in one go
    agg_result = df.agg(agg_dict)

    # Post-process transforms
    results = []
    for param in aggregation_parameters:
        name = param["name"]
        df[name] = pd.to_numeric(df[name], errors='coerce')
        res = {"property": name}
        if name in agg_result:
            for op in agg_dict.get(name, []):
                res[op] = agg_result[name][op] if op in agg_result[name] else None
        # Manual transforms
        series = df[name].dropna()
        for op in post_process[name]:
            if op == "unique":
                res["unique"] = list(series.unique())
            elif op == "mode":
                mode_val = series.mode()
                res["mode"] = mode_val.iloc[0] if not mode_val.empty else None
            elif op == "range":
                res["range"] = series.max() - series.min() if not series.empty else None
        results.append(res)
    return results
