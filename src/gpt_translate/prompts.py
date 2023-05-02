def translator_prompt(text: str, token_limit: int= 1500):
    """
    generate messages
    """
    messages = [
      {"role": "system", "content": "You are a helpful assistant that translates Chinese to English."},
      {"role": "user", "content": f'Translate the following Chinese to English,add new paragraphs for better readability: {text}"'}
    ]
    #num_tokens = num_tokens_from_messages(messages)
    #print(f"num_tokens {num_tokens}")
    return messages


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


def tags_prompt_prob_with_main_eng_title(text: str):
    """
    find main topics of a translation with tags in both English and Chinese
    """
    messages = [
      {"role": "system", "content": """You are a helpful assistant that provide tags in English and Chinese for input text, 
      The response should the following json format, nothing else:
      \{"english_tag_title": <suitable title for the article in English>,
      "english_main_topic": <main tag for the article in English>,
      "chinese_main_topic": <main tag for the article in Chinese>,
      "english_tags": {"<tag>": <relevance, ranging from 0 to 10>}, 
      "chinese_tags": {"<tag>": <relevance, ranging from 0 to 10>}\}"""},
      {"role": "user", "content": f"""{text}"""}
    ]
    return messages


def translate_title_prompt(text: str, token_limit: int= 1500):
    """
    generate messages
    """
    messages = [
      {"role": "system", "content": "You are a helpful assistant that translates article titles from Chinese to English."},
      {"role": "user", "content": f'{text}"'}
    ]
    #num_tokens = num_tokens_from_messages(messages)
    #print(f"num_tokens {num_tokens}")
    return messages