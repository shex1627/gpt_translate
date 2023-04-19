import json

from typing import List, Union, Dict, Any

def learn_data_types(data: Dict[str, Any], print_output: bool=False, max_items: int=None) -> Dict[str, Any]:
    """
    Recursively go through all items in a dictionary and learn their data types.
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = learn_data_types(value, max_items=max_items)
        else:
            result[key] = type(value).__name__
    if max_items is not None and len(result) > max_items:
        keys = list(result.keys())[:max_items]
        keys.append("...")
        result = {key: result[key] for key in keys}
    if print_output:
        print_dict_hierarchy(result)
    return result


def learn_data_types_complex(data: Union[Dict[str, Any], List[Any]], print_output: bool=False, max_items: int=None) -> Union[Dict[str, Any], List[Any]]:
    """
    Recursively go through all items in a dictionary or list and learn their data types.
    If a key is a list, check if items in the list can be converted to a dictionary,
    if convertable, learn the schema of that as well.
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = learn_data_types(value, max_items=max_items)
            elif isinstance(value, list):
                sub_items = []
                for item in value:
                    if isinstance(item, dict):
                        sub_items.append(learn_data_types(item, max_items=max_items))
                if sub_items:
                    result[key] = sub_items
                else:
                    result[key] = [type(value[0]).__name__] if value else []
            else:
                result[key] = type(value).__name__
        if max_items is not None and len(result) > max_items:
            keys = list(result.keys())[:max_items]
            keys.append("...")
            result = {key: result[key] for key in keys}
    elif isinstance(data, list):
        result = []
        for item in data:
            if isinstance(item, dict):
                result.append(learn_data_types(item, max_items=max_items))
            else:
                result.append(type(item).__name__)
        if max_items is not None and len(result) > max_items:
            result = result[:max_items] + ["..."]
    else:
        result = type(data).__name__
    if print_output:
        print_dict_hierarchy(result)
    return result

def print_dict_hierarchy(data: dict, indent: int = 0):
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{' '*indent}{key}:")
            print_dict_hierarchy(value, indent+2)
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            print(f"{' '*indent}{key}: [LIST]")
            print_dict_hierarchy(value[0], indent+2)
        else:
            print(f"{' '*indent}{key}: {value}")