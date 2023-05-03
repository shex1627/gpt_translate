import json
import pandas as pd
import numpy as np
from typing import Dict
from sklearn.metrics.pairwise import cosine_similarity

from gpt_translate.articles.dto import * 
from gpt_translate.articles.ArticleManager import  ArticleManager
from gpt_translate.article_to_translation import process_article, translate_article
from gpt_translate.utils import load_json_files
from gpt_translate.prompts import translator_prompt, translate_title_prompt, tags_prompt_prob_with_main_eng_title

import logging
logger = logging.getLogger("JsonArticleManager")

class JsonArticleManager(ArticleManager):
    def __init__(self, articles_json_path: str):
        #articles_json = load_json_files(json_data_path)
        self.articles_df = pd.read_json(articles_json_path, orient="records")
        self.tags_count = self.__count_tags__()
        self.article_json_path = articles_json_path

    def search_by_tags(self, input_tag: str, top_n= 15):
        # Filter the DataFrame to include only rows with the specified tag
        matching_rows = self.articles_df[
            (self.articles_df['english_tags'].apply(lambda x: input_tag in x.keys())) | \
            (self.articles_df['chinese_tags'].apply(lambda x: input_tag in x.keys()))].copy()

        # Sort the matching rows by relevance (if available) and then by date
        if matching_rows.empty:
            return pd.DataFrame(columns=self.articles_df.columns)

        matching_rows['relevance'] = matching_rows.apply(lambda row: row['english_tags'].get(input_tag, 0) + row['chinese_tags'].get(input_tag, 0), axis=1)
        sorted_rows = matching_rows.sort_values(by=['relevance', 'date'], ascending=[False, False]).drop(columns=['relevance'])

        return sorted_rows.head(top_n)
    
    def search_by_embedding(self, input_str: str, top_n= 15):
        input_embedding = self.get_embedding(input_str)

        # Calculate cosine similarity between the input embedding and all embeddings in the dataframe
        embeddings = np.stack(self.articles_df['embedding'].to_numpy())
        similarity = cosine_similarity(embeddings, [input_embedding])

        # Sort the similarities in descending order and get the top n indices
        top_indices = similarity.argsort(axis=0)[::-1][:top_n].flatten()

        # Get the top n most similar articles as a new dataframe
        top_articles_df = self.articles_df.loc[top_indices]

        return top_articles_df

    def search_by_text(self, input_str: str, top_n= 15):
        # Search the appropriate column for the input string
        query_results = self.articles_df[self.articles_df['text'].str.contains(input_str) | \
                                         self.articles_df['translation'].str.contains(input_str)]

        # If there are no results, return an empty dataframe
        if query_results.empty:
            return pd.DataFrame(columns=['title', 'embedding', 'text', 'translation', 'date'])

        # Sort the query results by date in descending order
        query_results = query_results.sort_values(by='date', ascending=False)

        #     # Calculate cosine similarity between the query embeddings and all embeddings in the dataframe
        #     query_embeddings = np.stack(query_results['embedding'].to_numpy())
        #     all_embeddings = np.stack(dataframe['embedding'].to_numpy())
        #     similarity = cosine_similarity(all_embeddings, query_embeddings)

        #     # Sort the similarities in descending order and get the top n indices
        #     top_indices = similarity.argsort(axis=0)[::-1][:top_n].flatten()

        #     # Get the top n most similar articles as a new dataframe
        #     top_articles_df = dataframe.loc[top_indices]
        return query_results.head(top_n)

    def __count_tags__(self) -> pd.DataFrame:
        # Create an empty list to store the tag counts
        tag_counts = []

        # Iterate over the rows of the DataFrame and count the tags
        for lang in [LanguageEnum.Chinese, LanguageEnum.English]:
            lang_col = f"{lang.lower()}_tags"
            for row in self.articles_df.itertuples(index=False):
                if row._asdict()[lang_col]:
                    for tag, relevance in row._asdict()[lang_col].items():
                        # Check if the tag is already in the tag_counts list
                        existing_tag = next((x for x in tag_counts if x['tag'] == tag and x['language'] == lang), None)
                        if existing_tag:
                            existing_tag['count'] += 1
                        else:
                            tag_counts.append({'tag': tag, 'count': 1, 'language': lang})

        # Convert the tag counts list to a DataFrame and return it
        df_counts = pd.DataFrame(tag_counts)
        return df_counts.sort_values("count", ascending=False).reset_index(drop=True)
    
    def get_tags_count(self):
        return self.tags_count

    def add_complete_article(self, article_record :Dict):
        """
        add article to current existing articles, persist

        article should be a dictionary or pydantic model with following fields minimum:
        title
        english_title
        english_tags
        chinese_tags
        text
        translation
        embedding (15XX dim dimensions)

        article should have column ID which should be unique
        """
        #
        article_record = article_record.copy()
        expected_columns = ['title', 'english_title', 'english_tags', 'chinese_tags', 'text', 'translation', 'embedding']
            # Make sure the dictionary has all the expected columns
        if not set(expected_columns).issubset(article_record.keys()):
            raise ValueError(f"Dictionary is missing expected columns. Missing： {set(expected_columns).difference(set(article_record.keys()))}")
        
        # Remove any extra attributes from the dictionary
        article_record['id'] = int(self.articles_df['id'].max() + 1)
        article_record = {k: v for k, v in article_record.items() if k in self.articles_df.columns}
        
        # Create a Series from the dictionary with missing columns filled with np.nan
        series = pd.Series(article_record, index=list(article_record.keys()))
        
        # Append the series to the DataFrame
        self.articles_df = self.articles_df.append(series, ignore_index=True)

        # persist dictionary to db
        self.articles_df.to_json(self.article_json_path, orient='records')
        return self.articles_df
    

    def complete_article(self, record :Dict, completion_config: Dict):
        """
        [not modify DB]
        given an article with only
        title
        text,

        return a dictionary s.t
        english_title
        translation
        english_title
        english_tags
        chinese_tags
        """
        record = record.copy()
        expected_columns = ['title', 'text']
            # Make sure the dictionary has all the expected columns
        if not set(expected_columns).issubset(record.keys()):
            raise ValueError(f"Dictionary is missing expected columns. Missing： {set(expected_columns).difference(set(record.keys()))}")
        
        # find enligsh title 
        english_title = process_article(record['title'],100000,
                                completion_config, translate_title_prompt)
        record['english_title'] = english_title.replace("\"", "")

        # find english translation
        article_translation = translate_article(record['text'], completion_config, translator_prompt)
        record['translation'] = article_translation
        
        # find english tags 
        article_tags = process_article(record['translation'],100000,
                                completion_config, tags_prompt_prob_with_main_eng_title)
        article_tags_dict = json.loads(article_tags)
        record.update(article_tags_dict)
        
        # create tags 
        record['pre_embed_tokens'] = self.preprocess_tags(
        [record['english_main_topic']] + list(record['english_tags'].keys()) 
        )
        
        embedding = self.get_embedding(record['pre_embed_tokens'])
        record['embedding'] = embedding
        return record
    

    def add_tag(self, article_id: int):
        """
        [modify DB]
        add english or chinese tags to an article
        """
        raise NotImplementedError()
    


    def remove_article_by_id(self, id: str):
        # Filter the DataFrame to exclude rows with the specified ID value
        self.articles_df = self.articles_df[self.articles_df['id'] != id]

        # persist dictionary to db
        self.articles_df.to_json(self.article_json_path, orient='records')
        return self.articles_df