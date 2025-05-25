from fastapi import Request, HTTPException
from typing import List, Any
from app.models.process import Process, ProcessName
from bson.objectid import ObjectId
from dotenv import load_dotenv
import operator
import os
import logging

load_dotenv()
logging.basicConfig(filename=os.getenv("ERROR_LOG_PATH", "error.log"), level=logging.ERROR)
logging.basicConfig(filename=os.getenv("INFO_LOG_PATH", "info.log"), level=logging.INFO)
logging.basicConfig(filename=os.getenv("WARNING_LOG_PATH", "warning.log"), level=logging.WARNING)

OPERATORS = {
    "==": {"action": operator.eq, "types": ["int", "float", "string", "number"]},
    "!=": {"action": operator.ne, "types": ["int", "float", "string", "number"]},
    ">": {"action": operator.gt, "types": ["int", "float", "number"]},
    "<": {"action": operator.lt, "types": ["int", "float", "number"]},
    ">=": {"action": operator.ge, "types": ["int", "float", "number"]},
    "<=": {"action": operator.le, "types": ["int", "float", "number"]},
    "contains": {"action": lambda col, val: col.str.contains(val, case=False, na=False), "types": ["string"]}
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
    page = int(query_params.get("page", 1))
    offset = limit * (page - 1)
    select_parameters = [col for col in query_params.get("select", "").strip().split(" ") if col]
    select = {}
    for col in select_parameters:
        select[col] = 1
    
    if offset < 0:
        offset = 0
        
    if limit < 1:
        limit = 1
    elif limit > 100:
        limit = 100
    
    if "limit" in query_params:
        query_params.pop("limit")
    if "page" in query_params:
        query_params.pop("page")
    if "select" in query_params:
        query_params.pop("select")
        
    if "_id" in query_params:
        try:
            query_params["_id"] = ObjectId(query_params["_id"])
        except Exception:
            pass 
        
    
    return {"query_params": query_params, "limit": limit, "offset": offset, "page": page, "select": select}

def validate_parameters(collection_parameters: List[str], task_parameters: List[str]):
    """
    Validates if the parameters to be processed are present in the collection parameters.
    Raises an exception if any paramter is not valid.
    """
    invalid_parameters = [parameter for parameter in task_parameters if parameter not in collection_parameters]
    
    if len(invalid_parameters) > 0:
        logging.error(f"Missing parameters: {', '.join(invalid_parameters)}")
        raise ValueError(f"Missing parmaters: {', '.join(invalid_parameters)}. Please check the parameters provided.")

def validate_operator(repository_parameter: dict, operator: str, value: Any):
    """
    Validates if the operator is supported and the value matches the expected type.
    Raises an exception if the operator or value is not valid.
    """
    if operator not in OPERATORS:
        logging.error(f"Unsupported operator: {operator}")
        raise HTTPException(status_code=400, detail=f"Unsupported operator: {operator}")

    expected_types = OPERATORS[operator]["types"]
    param_type = repository_parameter["type"]

    if param_type not in expected_types:
        logging.error(f"Operator '{operator}' is not valid for type '{param_type}'. " f"Expected types are: {', '.join(expected_types)}")
        raise HTTPException(status_code=400, detail=f"Operator '{operator}' is not valid for type '{param_type}'. "f"Expected types are: {', '.join(expected_types)}")

    # Map "number" to (int, float), "string" to str
    if param_type in ("int", "float", "number"):
        if not isinstance(value, (int, float)):
            logging.error(f"Value '{value}' is not valid for operator '{operator}'. Expected a number.")
            raise HTTPException(status_code=400, detail=f"Value '{value}' is not valid for operator '{operator}'. Expected a number.")
    elif param_type == "string":
        if not isinstance(value, str):
            logging.error(f"Value '{value}' is not valid for operator '{operator}'. Expected a string.")
            raise HTTPException(status_code=400, detail=f"Value '{value}' is not valid for operator '{operator}'. Expected a string.")

def validate_aggregations(aggregation: List[str]):
    """
    Validates if the aggregation functions are supported.
    Raises an exception if any function is not valid.
    """
    invalid_aggregation = [agg for agg in aggregation if agg not in AGGREGATION_FUNCTIONS.keys()]
    
    if invalid_aggregation:
        logging.error(f"Unsupported aggregation functions: {', '.join(invalid_aggregation)}")
        raise ValueError(f"Unsupported aggregation functions: {', '.join(invalid_aggregation)}")

def validate_processes(processes: List[str]) -> None:
    """
    Validate the processes from ProcessName enum.
    """
    if not processes or len(processes) == 0:
        logging.error("No processes provided for validation.")
        raise HTTPException(status_code=400, detail="No processes provided")
    
    for process in processes:
        if process not in ProcessName.__members__:
            logging.error(f"Invalid process: {process}. Supported processes are: {', '.join(ProcessName.__members__.keys())}")
            raise HTTPException(status_code=400, detail=f"Invalid process: {process}")

def validate_aggregation_parameter_types(collection_parameters: List[dict], process_parameters: List[str], parameter_type: str):
    """
    Validates if the parameters to be processed are of the correct type.
    Raises an exception if any parameter is not valid.
    """
    for process_parameter in process_parameters:
        for collection_parameter in collection_parameters:
            if process_parameter["name"] == collection_parameter["name"] and collection_parameter["type"] != parameter_type:
                logging.error(f"Parameter {collection_parameter['name']} is not of type {parameter_type}. Expected type: {collection_parameter['type']}.")
                raise HttpException(status_code=400, detail=f"Parameter {collection_parameter['name']} is not of type {parameter_type}. Expected type: {collection_parameter['type']}.")
    