from app.utils.general_utils import OPERATORS, AGGREGATION_FUNCTIONS
import pandas as pd
import multiprocessing as mp
import asyncio
from typing import List, Any, Dict

def filter_data(df: pd.DataFrame, filters: List[Any]) -> pd.DataFrame:
    mask = pd.Series([True] * len(df))
    for condition in filters:
        op_func = OPERATORS[condition["operator"]]["action"]
        value = condition["value"]
        if condition["operator"] == "contains":
            mask &= op_func(df[condition["name"]].astype(str), str(value))
        else:
            try:
                value_cast = float(value)
            except (ValueError, TypeError):
                value_cast = value
            mask &= op_func(df[condition["name"]], value_cast)
    return df[mask].reset_index(drop=True)

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
    return df.groupby(group_by_parameters)

def aggregate_data(df: pd.DataFrame, aggregation_parameters: List[dict]) -> List[dict]:
    aggregation_ops = {"sum", "min", "max", "mean", "count", "median", "std", "var", "first", "last"}
    transform_ops = {"unique", "mode", "range"}

    result = []
    for parameter in aggregation_parameters:
        param_name = parameter["name"]
        ops = parameter["operations"]

        agg_ops = [op for op in ops if op in aggregation_ops]
        trans_ops = [op for op in ops if op in transform_ops]

        agg_result = {}
        if agg_ops:
            agg_values = df[param_name].agg(agg_ops)
            for agg_func in agg_ops:
                agg_result[agg_func] = agg_values[agg_func] if agg_func in agg_values else None

        # Apply transforms manually
        series = df[param_name]
        for trans_func in trans_ops:
            if trans_func == "unique":
                agg_result["unique"] = list(series.unique())
            elif trans_func == "mode":
                mode_val = series.mode()
                agg_result["mode"] = mode_val.iloc[0] if not mode_val.empty else None
            elif trans_func == "range":
                agg_result["range"] = series.max() - series.min() if not series.empty else None

        # Combine into result
        result.append({"property": param_name,**agg_result})

    return result
