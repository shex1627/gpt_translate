from enum import Enum
from typing import List
from pydantic import BaseModel


class LanguageEnum(str, Enum):
    Chinese = 'Chinese'
    English = 'English'

    @property
    def search_column(self):
        if self == LanguageEnum.Chinese:
            return 'text'
        elif self == LanguageEnum.English:
            return 'translation'
        else:
            raise ValueError("Invalid language: must be 'Chinese' or 'English'.")
    
    def __eq__(self, other):
        # Override the __eq__ method to compare enum values to string values
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)

"""
Thinking about converting article into a 
structure json, but rather keep it in current form


{'title': 'str',
 'date': 'str',
 'url': 'str',
 'is_original': 'bool',
 'text': 'str',
 'text_len': 'int',
 'translation': 'str',
 'english_tags': {<tag>: <relevance, from 0 to 10>},
 'chinese_tags': {<tag>: <relevance, from 0 to 10>},
 'english_main_topic': 'str',
 'chinese_main_topic': 'str'}
"""