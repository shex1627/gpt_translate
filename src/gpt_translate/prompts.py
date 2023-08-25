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

def key_context_prompt(question: str):
    """
    generate messages
    """
    messages = [
      {"role": "system", "content": "You are a QA bot that finds relevant information to answer the given question."},
      {"role": "user", "content": f'extract key entities from below question "{question}", return only the list of key entities as plain text"'}
    ]
    #num_tokens = num_tokens_from_messages(messages)
    #print(f"num_tokens {num_tokens}")
    return messages

def single_article_prompt(question: str, article: str, word_limit: int= 2000, language: str = "Chinese"):
    """
    generate messages
    """
    messages = [
      {"role": "system", "content": "You are a QA bot that finds relevant information to answer the given question, based on the following article, if you can not give a definite answer, still provide relevant information}"},
      {"role": "user", "content": f'In less than {word_limit} words, answering in {language} language, return important context to answer the following question: {question}, based on the following article, if you can not give a definite answer, still provide relevant information, aritcle: {article}"'}
    ]
    #num_tokens = num_tokens_from_messages(messages)
    #print(f"num_tokens {num_tokens}")
    return messages


def aggregate_article_prompt(question: str, article: str, word_limit: int= 2000, language: str = "Chinese"):
    """
    generate messages
    """
    messages = [
      {"role": "system", "content": "You are a QA bot that tries to answer the given question based on analyzing the given text, if you can not give a definite answer, express that and summarize the information from given context."},
      {"role": "user", "content": f'Below are answers to question {question} based on different articles, oragnize all the answers into a coherent essay in less than {word_limit} words, answering in {language} language". Context: {article}"'}
    ]
    #num_tokens = num_tokens_from_messages(messages)
    #print(f"num_tokens {num_tokens}")
    return messages