def tags_prompt_prob_with_main(text: str):
    """
    find main topics of a translation with tags in both English and Chinese
    """
    messages = [
      {"role": "system", "content": """You are a helpful assistant that provide tags in English and Chinese for input text, 
      The response should the following json format, nothing else:
      \{"english_main_topic": <main tag for the article in English>,
      "chinese_main_topic": <main tag for the article in Chinese>,
      "english_tags": {"<tag>": <relevance, ranging from 0 to 10>}, 
      "chinese_tags": {"<tag>": <relevance, ranging from 0 to 10>}\}"""},
      {"role": "user", "content": f"""{text}"""}
    ]
    return messages