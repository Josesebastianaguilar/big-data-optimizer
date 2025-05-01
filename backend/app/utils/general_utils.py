from fastapi import Request
from typing import List, Any
from app.models.process import Process, ProcessName
import operator

OPERATORS = {
    "==": {"action": operator.eq, "types": ["int", "float", "str", "number"]},
    "!=": {"action": operator.ne, "types": ["int", "float", "str", "number"]},
    ">": {"action": operator.gt, "types": ["int", "float", "number"]},
    "<": {"action": operator.lt, "types": ["int", "float", "number"]},
    ">=": {"action": operator.ge, "types": ["int", "float", "number"]},
    "<=": {"action": operator.le, "types": ["int", "float", "number"]},
    "contains": {"action": lambda col, val: col.str.contains(val, case=False, na=False), "types": ["str"]}
}

AGGREGATION_FUNCTIONS = {
    "sum": sum,
    "min": min,
    "max": max,
    "mean": lambda x: sum(x) / len(x) if len(x) > 0 else None,
    "count": len,
    "median": lambda x: sorted(x)[len(x) // 2] if len(x) % 2 != 0 else (sorted(x)[len(x) // 2 - 1] + sorted(x)[len(x) // 2]) / 2,
    "std": lambda x: (sum((xi - sum(x) / len(x)) ** 2 for xi in x) / len(x)) ** 0.5 if len(x) > 1 else 0,
    "var": lambda x: sum((xi - sum(x) / len(x)) ** 2 for xi in x) / len(x) if len(x) > 1 else 0,
    "first": lambda x: x[0] if len(x) > 0 else None,
    "last": lambda x: x[-1] if len(x) > 0 else None,
    "unique": lambda x: list(set(x)),
    "mode": lambda x: max(set(x), key=x.count) if len(x) > 0 else None,
    "range": lambda x: max(x) - min(x) if len(x) > 0 else None
}

def get_query_params(request: Request) -> dict:
    """
    Extracts query parameters from the request and returns them as a dictionary for a list of items.
    """
    query_params = request.query_params._dict
    limit = int(query_params.get("limit", 10))
    offset = int(query_params.get("offset", 0))
    
    if limit > 100:
        limit = 100
    
    if "limit" in query_params:
        query_params.pop("limit")
    if "offset" in query_params:
        query_params.pop("offset")
    
    return {"query_params": query_params, "limit": limit, "offset": offset}

def validate_columns(collection_columns: List[str], process_columns: List[str]):
    """
    Validates if the columns to be processed are present in the collection columns.
    Raises an exception if any column is not valid.
    """
    invalid_columns = [col for col in process_columns if col not in collection_columns]
    
    if invalid_columns:
        raise ValueError(f"Missing columns: {', '.join(invalid_columns)}")

def validate_operator(operator: str, type: str):
    """
    Validates if the operator is supported.
    Raises an exception if the operator is not valid.
    """
    if operator not in OPERATORS.keys():
        raise ValueError(f"Unsupported operator '{operator}'. Supported operators are: {', '.join(OPERATORS.keys())}")
    
    if type not in OPERATORS[operator]["types"]:
        raise ValueError(f"Operator '{operator}' is not valid for type '{type}'. Supported types are: {', '.join(OPERATORS[operator]['types'])}")

def validate_aggregation(aggregation: List[str]):
    """
    Validates if the aggregation functions are supported.
    Raises an exception if any function is not valid.
    """
    invalid_aggregation = [agg for agg in aggregation if agg not in AGGREGATION_FUNCTIONS.keys()]
    
    if invalid_aggregation:
        raise ValueError(f"Unsupported aggregation functions: {', '.join(invalid_aggregation)}")

def validate_processes(processes: List[str]) -> None:
    """
    Validate the processes from ProcessName enum.
    """
    if not processes or len(processes) == 0:
        raise HTTPException(status_code=400, detail="No processes provided")
    
    for process in processes:
        if process not in ProcessName.__members__:
            raise HTTPException(status_code=400, detail=f"Invalid process: {process}")

def validate_columns_types(collection_columns: List[dict], process_columns: List[str], col_type: str):
    """
    Validates if the columns to be processed are of the correct type.
    Raises an exception if any column is not valid.
    """
    for process_column in process_columns:
        for col in collection_columns:
            if col.name == process_column and col.type != col_type:
                raise ValueError(f"Column '{process_column}' is not of type '{type}'. Expected type: {col_type}.")
    