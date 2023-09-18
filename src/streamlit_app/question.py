import openai
import os
import json
import streamlit as st
import pandas as pd
import os 
from urllib.request import urlopen
from PIL import Image
import random
import logging 
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid import GridUpdateMode, DataReturnMode
from gpt_translate.utils import add_newlines
from gpt_translate.articles.JsonArticleManager import JsonArticleManager
from gpt_translate.article_to_answer import parallel_send_chatcomplete_api
from gpt_translate.prompts import key_context_prompt, single_article_prompt, aggregate_article_prompt
from gpt_translate.article_to_translation import text_split, send_chatcomplete_api, combine_openapi_response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

openai.api_key = os.environ["OPENAI_API_KEY"]

TOP_K_ARTICLES = 10
SINGLE_ARTICLE_SUMMARY_LENGTH = 1024
SUNMMARY_LENGTH = 4000  
TOP_N_ARTICLES = 40
OUTPUT_FILE_PATH = os.environ.get("OUTPUT_FILE_PATH", "./output.json")

completion_config = {
    'model': "gpt-3.5-turbo-16k",
    'temperature': 0
}

gpt4_config = {
    'model': "gpt-4",
    'temperature': 0,
}

@st.cache_data
def get_article_manager():
   article_file_path = os.environ.get('ARTICLE_DB_PATH', "C:\\Users\\alistar\\Desktop\\ds\\blogger_translate\\articles_embedding.json")
   print(f"article_file_path {article_file_path}")
   article_manager = JsonArticleManager(article_file_path)
   return article_manager

@st.cache_data
def get_article_summary(all_context_text: str, question: str, language: str = "Chinese"):
    text_trunks = text_split(all_context_text, max_length=SINGLE_ARTICLE_SUMMARY_LENGTH)
    trunk_messages = [single_article_prompt(question, text_trunk, word_limit=SINGLE_ARTICLE_SUMMARY_LENGTH, 
                                            language=language) for text_trunk in text_trunks]
    responses = parallel_send_chatcomplete_api(trunk_messages, completion_config)
    trunk_processed = [combine_openapi_response(response)[0] for response in responses]
    return trunk_processed

@st.cache_data
def agggregate_article_summary(article_summaries: str, question: str, language: str = "Chinese"):
    aggregate_answers_msg = aggregate_article_prompt(question, article_summaries, 
                                                     word_limit = SINGLE_ARTICLE_SUMMARY_LENGTH, 
                                                     language=language)
    response = openai.ChatCompletion.create(**completion_config, messages=aggregate_answers_msg)
    return response

# set up page icon
page_icon = Image.open(urlopen("https://i.imgur.com/z7ZGWvZ.jpg"))

# Streamlit App
st.set_page_config(page_title="Article Search", 
                   page_icon=page_icon, 
                   layout="wide")

# hide menu
if os.environ.get('HIDE_MENU', 'true') == 'true':
        st.markdown("""
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """, unsafe_allow_html=True)
        
st.title("Answer Questions from Articles")
st.write("This website uses GPT to answer questions based on the top 5 relevant articles from a wechat blog. The blog covers a wide range of common topics in life.")

article_manager = get_article_manager()
query_params = st.experimental_get_query_params()
initial_question = query_params.get("question", [""])[0]  # Extract the first value if there's any.
initial_language = query_params.get("language", ["English"])[0]
auto_run = bool(initial_question)

languages = ["English", "Chinese"]
language = st.radio("Language:", languages, index=languages.index(initial_language) if initial_language in languages else 0)
is_random = st.radio("Article Randomness", ["Default", "Random"], index=0)
st.write(f"Note: Random means randomly choose {TOP_K_ARTICLES} out of top {TOP_N_ARTICLES} relevant articles")

# save random to session state
st.session_state.is_random = is_random

# save language to session state
st.session_state.language = language
if st.session_state.language == "English":
    st.session_state.period = "."
    show_cols = ['english_title', 'title']
elif st.session_state.language == 'Chinese':
    st.session_state.period = "。"
    show_cols = ['title', 'english_title']

if 'selected_article' not in st.session_state:
    st.session_state.selected_article = None

st.header("Ask A Question")
question = st.text_input("question prompt",value=initial_question, max_chars=60)
st.experimental_set_query_params(question=question, language=st.session_state.language)

if (st.button("Ask") and question) or auto_run:
    key_context_resp = openai.ChatCompletion.create(**completion_config, messages=key_context_prompt(question))
    key_context = key_context_resp.choices[0]['message']['content'].replace("作者,", "")
    relevant_articles = article_manager.search_by_embedding(key_context, top_n=TOP_N_ARTICLES) 
    if st.session_state.is_random == "Default":
        seed = "None"
        st.session_state.seed = seed
        results = relevant_articles[:TOP_K_ARTICLES]
    else:
        seed = random.randint(0, 10000)
        st.session_state.seed = seed
        results = relevant_articles.sample(n=TOP_K_ARTICLES, random_state=seed)
    results['article_url'] = results['id'].apply(lambda x: f"https://memory.ftdalpha.com?article_id={x}")
    results = results.reset_index(drop=True)
    st.session_state.results = results
st.write("Note: typical run takes 2-4 min to finish")

if st.session_state.get("results", pd.DataFrame()).shape[0] > 0:
    # Generate column definitions dynamically
    # make streamtlit show each row in dataframe st.session_state.results
    st.header("Relevant Articles")
    st.write(st.session_state.results[['article_url']+show_cols])

    # load output file 
    try:
        with open(OUTPUT_FILE_PATH, "r") as f:
            output = json.load(f)
    except:
        output = {}
    question_key = "-".join([question, st.session_state.language, str(st.session_state.seed)])
    if question_key in output:
        trunk_processed = output[question_key]["article_summary_sentences"]
        overall_summary_sentences = output[question_key]["overall_summary_sentences"]
        # write to UI the summary of individual articles
        for trunk in trunk_processed:
            st.write(trunk)
            st.write("#####################################\n")    
    else:
        all_context_text = " ".join(st.session_state.results['text'])
        trunk_processed = get_article_summary(all_context_text, question, language=st.session_state.language)

        # write to UI the summary of individual articles 
        st.header("Article Summaries")
        for trunk in trunk_processed:
            st.write(trunk)
            st.write("#####################################\n")    

        article_summaries = "\n".join(trunk_processed)
        article_summary_sentences = []
        for trunk in trunk_processed:
            for sentence in trunk.split(st.session_state.period):
                if sentence:
                    article_summary_sentences.append(sentence)
                    article_summary_sentences.append("\n")
            article_summary_sentences.append("#####################################\n")

        overall_summary_resp = agggregate_article_summary(article_summaries, question, language=st.session_state.language)
        print(overall_summary_resp)
        overall_summary_sentences = []
        for sentence in overall_summary_resp.choices[0]['message']['content'].split(st.session_state.period):
            if sentence:
                overall_summary_sentences.append(sentence)
                overall_summary_sentences.append("\n")

    st.header("Overall Summary")
    st.write("".join(overall_summary_sentences))
    
    # save current output to another file 
    with open(OUTPUT_FILE_PATH, "w") as f:
        output[question_key] = {"article_summary_sentences": trunk_processed, 
                            "overall_summary_sentences": overall_summary_sentences}
        json.dump(output, f, indent=4)
    
