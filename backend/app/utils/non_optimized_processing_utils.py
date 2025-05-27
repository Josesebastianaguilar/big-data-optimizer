import pandas as pd
import operator
from typing import List, Any, Dict, Tuple
from collections import defaultdict
from app.utils.general_utils import OPERATORS, AGGREGATION_FUNCTIONS

def filter_data(df: pd.DataFrame, filters: List[Dict[str, Any]], num_processes = None) -> pd.DataFrame:
    """
    Filter a DataFrame using multiple conditions.
    Parameters:
    - df: pd.DataFrame - The input data.
    - filters: List[Dict[str, Any]] - Filter conditions.
    Returns:
    - pd.DataFrame: Filtered DataFrame.
    """
    
    for condition in filters:
        op_func = OPERATORS[condition["operator"]]["action"]
        value = condition["value"]

        if condition["operator"] == "contains":
            df = df[op_func(df[condition["name"]].astype(str), str(value))]
        else:
            try:
                value = float(value)
            except ValueError:
                pass
            df = df[op_func(df[condition["name"]], value)]

    return df

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
    """
    Group data by specified parameters.
    Parameters:
    - data: List[dict] - Input data as a list of dictionaries.
    - group_by_parameters: List[str] - Parameters to group by.
    Returns:
    - Dict[Tuple[Any, ...], List[dict]]: A dictionary where keys are tuples of group values and values are lists of rows in that group.
    """
    grouped_data = defaultdict(list)
    
    for row in data:
        group_key = tuple(row.get(parameter, None) for parameter in group_by_parameters)
        
        if any(v is None for v in group_key):
            continue
        grouped_data[group_key].append(row)
    
    return grouped_data

def aggregate_data(df: pd.DataFrame, aggregation_parameters: List[dict]) -> Dict[str, Any]:
    """
    Perform aggregation on the DataFrame based on specified parameters and functions.
    Parameters:
    - df: pd.DataFrame - The input data.
    - aggregation_parameters: List[dict] - Parameters to aggregate and their respective functions.
    Returns:
    - Dict[str, Any]: A dictionary with aggregation results.
    """
    results = []
    for aggregation_parameter in aggregation_parameters:
        aggregation_result = {"property": aggregation_parameter["name"]}
        series_as_list = df[aggregation_parameter["name"]].tolist()
         
        for aggregation in aggregation_parameter["operations"]:
            aggregation_result[aggregation] = AGGREGATION_FUNCTIONS[aggregation](series_as_list)
        results.append(aggregation_result)

    return results
