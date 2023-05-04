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


def add_newline_after_period(chinese_article: str) -> str:
    """
    Takes a Chinese article as input and returns the same article with a newline added
    after each period, but only if there is no newline character already present.

    Args:
        chinese_article: A string containing a Chinese article.

    Returns:
        A string containing the input article with a newline added after each period,
        but only if there is no newline character already present.

    Example:
        >>> article = "这是一篇关于Python的文章。Python是一种高级编程语言。"
        >>> add_newline_after_period(article)
        '这是一篇关于Python的文章。\nPython是一种高级编程语言。'
    """
    new_article = ""
    for i in range(len(chinese_article)):
        if chinese_article[i] == "。" and i < len(chinese_article) - 1 and chinese_article[i+1] != "\n":
            new_article += "。\n"
        else:
            new_article += chinese_article[i]
    return new_article

def add_newlines(article: str) -> str:
    """
    Adds a newline character after each period (`。`) in a Chinese article, but only if there are no existing newline characters.

    Args:
        article (str): The Chinese article to process.

    Returns:
        str: The processed Chinese article with a newline character after each period (`。`).
    """
    if '\n' in article:
        return article
    
    new_article = ''
    for char in article:
        new_article += char
        if char == '。':
            new_article += '\n'
    
    return new_article
