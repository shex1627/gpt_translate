from enum import Enum
from typing import List
import openai
import os
import json

from gpt_translate.articles.dto import LanguageEnum
from pydantic import BaseModel

openai.api_key = os.environ["OPENAI_API_KEY"]

class ArticleManager:
    def __init__(self):
        pass

    def search_by_tags(self, input_tag: str, language: LanguageEnum):
        raise NotImplementedError()

    def search_by_text(self, input_str: str, language: LanguageEnum):
        raise NotImplementedError()

    def search_by_embedding(self, input_str: str, language: LanguageEnum):
        raise NotImplementedError()

    def get_embedding(text: str, model="text-embedding-ada-002"):
        try:
            text = text.replace("\n", " ")
            return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']
        except Exception as e:
            print(e)
            return []
    