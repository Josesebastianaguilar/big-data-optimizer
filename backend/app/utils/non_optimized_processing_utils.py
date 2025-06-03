import pandas as pd
import operator
import statistics
from typing import List, Any, Dict, Tuple
from collections import defaultdict
from app.utils.general_utils import OPERATORS, AGGREGATION_FUNCTIONS

def filter_data(df: pd.DataFrame, filters: List[Dict[str, Any]]) -> pd.DataFrame:
    if not filters:
        return df
    mask = pd.Series([True] * len(df))
    for condition in filters:
        op_func = OPERATORS[condition["operator"]]["action"]
        value = condition["value"]
        col = df[condition["name"]]
        if condition["operator"] == "contains":
            mask &= op_func(col.astype(str), str(value))
        else:
            try:
                value_cast = float(value)
            except ValueError:
                value_cast = value
            mask &= op_func(col, value_cast)
    return df[mask].reset_index(drop=True)

def map_groupped_records(groupped_data: dict, map_property: str) -> dict:
    """
    Map grouped records to a dictionary with group keys and their corresponding values.
    Parameters:
    - groupped_data: dict - The grouped data.
    - map_property: str - The property to map.
    Returns:
    - dict: A dictionary where keys are group keys and values are lists of mapped property values.
    """
    group_mapping = {}
    for group_key in groupped_data.keys():
        group_mapping[group_key] = [record[map_property] for record in groupped_data[group_key]]
    
    return group_mapping

def group_data(data: List[dict], group_by_parameters: List[str]) -> Dict[Tuple[Any, ...], List[dict]]:
    grouped_data = defaultdict(list)
    for row in data:
        try:
            group_key = tuple(row[param] for param in group_by_parameters)
        except KeyError:
            continue  # skip rows missing a key
        if any(v is None for v in group_key):
            continue
        grouped_data[group_key].append(row)
    return grouped_data

def aggregate_data(df: pd.DataFrame, aggregation_parameters: List[dict]) -> Dict[str, Any]:
    results = []
    for aggregation_parameter in aggregation_parameters:
        aggregation_result = {"property": aggregation_parameter["name"]}
        series_as_list = df[aggregation_parameter["name"]].tolist()
        sorted_list = None  # Only sort if needed

        for aggregation in aggregation_parameter["operations"]:
            if aggregation == "mean":
                aggregation_result["mean"] = statistics.mean(series_as_list) if series_as_list else None
            elif aggregation == "median":
                aggregation_result["median"] = statistics.median(series_as_list) if series_as_list else None
            elif aggregation == "mode":
                try:
                    aggregation_result["mode"] = statistics.mode(series_as_list)
                except statistics.StatisticsError:
                    aggregation_result["mode"] = None
            elif aggregation == "std":
                aggregation_result["std"] = statistics.stdev(series_as_list) if len(series_as_list) > 1 else 0
            elif aggregation == "var":
                aggregation_result["var"] = statistics.variance(series_as_list) if len(series_as_list) > 1 else 0
            elif aggregation == "sum":
                aggregation_result["sum"] = sum(series_as_list)
            elif aggregation == "min":
                aggregation_result["min"] = min(series_as_list) if series_as_list else None
            elif aggregation == "max":
                aggregation_result["max"] = max(series_as_list) if series_as_list else None
            elif aggregation == "count":
                aggregation_result["count"] = len(series_as_list)
            elif aggregation == "first":
                aggregation_result["first"] = series_as_list[0] if series_as_list else None
            elif aggregation == "last":
                aggregation_result["last"] = series_as_list[-1] if series_as_list else None
            elif aggregation == "unique":
                aggregation_result["unique"] = list(set(series_as_list))
            elif aggregation == "range":
                aggregation_result["range"] = (max(series_as_list) - min(series_as_list)) if series_as_list else None
            else:
                # fallback to AGGREGATION_FUNCTIONS if custom
                aggregation_result[aggregation] = AGGREGATION_FUNCTIONS[aggregation](series_as_list)
        results.append(aggregation_result)
    return results
