def tags_prompt(text: str, token_limit: int= 1500):
    """
    generate messages
    """
    messages = [
      {"role": "system", "content": """You are a helpful assistant that provide tags in English and Chinese for input text, The response should the following json format, nothoing else:\{"english_tags": <tags in english>, "chinese_tags": <tags in Chinese>\}"""},
      {"role": "user", "content": f"""{text}"""}
    ]
    #num_tokens = num_tokens_from_messages(messages)
    #print(f"num_tokens {num_tokens}")
    return messages

def tags_prompt_prob(text: str, token_limit: int= 1500):
    """
    generate messages
    """
    messages = [
      {"role": "system", "content": """You are a helpful assistant that provide tags in English and Chinese for input text, The response should the following json format, nothoing else:\{"english_tags": {"<tag>": <relevance, ranging from 0 to 10>}, "chinese_tags": {"<tag>": <relevance, ranging from 0 to 10>}\}"""},
      {"role": "user", "content": f"""{text}"""}
    ]
    #num_tokens = num_tokens_from_messages(messages)
    #print(f"num_tokens {num_tokens}")
    return messages