import pandas as pd
import modin.pandas as modin_pd
import operator
import multiprocessing as mp
from app.general_utils import validate_columns, validate_column_types, validate_operator, validate_aggregation, OPERATORS, AGGREGATION_FUNCTIONS


def filter_chunk(chunk: pd.DataFrame, filters: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Filter a chunk of DataFrame based on multiple conditions.
    Parameters:
    - chunk: A DataFrame chunk.
    - filters: List of filter conditions (each with column, operator, and value).
    Returns:
    - Filtered DataFrame chunk.
    """
    for condition in filters:
        op_func = OPERATORS[condition["operator"]]["action"]

        if operator == "contains":
            chunk = chunk[op_func(chunk[condition["name"]].astype(str), value)]
        else:
            try:
                value = float(value)
            except ValueError:
                pass
            chunk = chunk[op_func(chunk[condition["name"]], value)]
    return chunk


def filter_data(df: pd.DataFrame, filters: List[Dict[str, Any]], num_processes=1) -> pd.DataFrame:
    """
    Filter a DataFrame using multiple conditions in parallel.
    Parameters:
    - df: pd.DataFrame - The input data.
    - filters: List[Dict[str, Any]] - Filter conditions.
    - num_processes: int - Number of processes to use for parallel processing.
    Returns:
    - pd.DataFrame: Filtered DataFrame.
    """
    chunks = [df.iloc[i::num_processes] for i in range(num_processes)]
    args = [(chunk, filters) for chunk in chunks]

    with mp.Pool(processes=num_processes) as pool:
        results = pool.starmap(filter_chunk, args)

    filtered_df = pd.concat(results)

    return filtered_df.reset_index(drop=True)

def group_data(df: pd.DataFrame, group_by_columns: List[str]) -> pd.core.groupby.generic.DataFrameGroupBy:
    """
    Group data by specified columns.
    Parameters:
    - df: pd.DataFrame - The input data.
    - group_by_columns: List[str] - Columns to group by.
    Returns:
    - pd.core.groupby.generic.DataFrameGroupBy: A DataFrameGroupBy object.
    """
    return df.groupby(group_by_columns)

def aggregate_data(df: pd.DataFrame, aggregation_columns: List[dict]) -> List[dict]:
    """
    Perform aggregation on the DataFrame based on specified columns and functions.
    Parameters:
    - df: pd.DataFrame - The input data.
    - aggregate_columns: List[dict] - Columns to aggregate and their respective functions.
    Returns:
    - List[dict]: A list of dictionaries with aggregation results.
    """
    result = []
    for column in aggregation_columns:
        try:
            agg_values = df[column["name"]].agg(column["aggregations"])
            result.append({
                "property": column,
                **{agg_func: agg_values[agg_func] for agg_func in column["aggregations"]}
            })
        except Exception as e:
            print(f"Skipping column '{column}' due to error: {e}")
    return result
