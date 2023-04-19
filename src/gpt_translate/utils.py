import os
from typing import List, Dict
import json

def load_json_files(file_path: str) -> List[Dict]:
    """
    Loads all JSON files in the specified file path and returns a list of dictionaries containing the data from each file.

    Args:
        file_path (str): The file path to load the JSON files from.

    Returns:
        A list of dictionaries containing the data from each JSON file.
    """
    # Initialize an empty list to store the data from each JSON file
    data_list = []

    # Load each JSON file in the directory and append the data to the list
    for file_name in os.listdir(file_path):
        if file_name.endswith('.json'):
            file_pathname = os.path.join(file_path, file_name)
            with open(file_pathname, encoding="utf-8") as file:
                data = json.load(file)
                data_list.append(data)

    return data_list