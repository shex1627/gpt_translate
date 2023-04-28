import streamlit as st
import pandas as pd
import os 
from urllib.request import urlopen
from PIL import Image


from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid import GridUpdateMode, DataReturnMode
from gpt_translate.articles.JsonArticleManager import JsonArticleManager

@st.cache_data
def get_article_manager():
   article_manager = JsonArticleManager("C:\\Users\\alistar\\Desktop\\ds\\blogger_translate\\articles_embedding.json")
   return article_manager


page_icon = Image.open(urlopen("https://i.imgur.com/z7ZGWvZ.jpg"))

# Streamlit App
st.set_page_config(page_title="Article Search", 
                   page_icon=page_icon, layout="wide")

if os.environ.get('HIDE_MENU', 'true') == 'true':
        st.markdown("""
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """, unsafe_allow_html=True)


st.title("Article Search")

article_manager = get_article_manager()

language = st.radio("Language:", ["English", "Chinese"], index=0)
st.session_state.language = language
if st.session_state.language == 'English':
    show_cols = ['english_title', 'english_main_topic', 'english_tags', 'title']
else:
    show_cols = ['title', 'chinese_main_topic', 'chinese_tags']

# Sidebar
st.sidebar.title("Available Tags")
tags_count_df = article_manager.get_tags_count()
tags_count_df_filtered = tags_count_df[tags_count_df['language'] == st.session_state.language]
st.sidebar.write(tags_count_df_filtered.reset_index(drop=True))

if 'selected_article' not in st.session_state:
    st.session_state.selected_article = None

st.header("Search Articles")
query_params = st.experimental_get_query_params()
print(query_params)

# Input & options
search_input = st.text_input("Search Articles", max_chars=30)
search_option = st.radio("Search by:", ["Embedding", "Tag", "Text"])

if st.button("Search"):
    if search_option == "Embedding":
        results = article_manager.search_by_embedding(search_input)
    elif search_option == "Tag":
        results = article_manager.search_by_tags(search_input)
    else:
        results = article_manager.search_by_text(search_input)

    results = results.reset_index(drop=True)
    st.session_state.results = results


selected_rows = []

if st.session_state.get("results", pd.DataFrame()).shape[0] > 0:
    # Generate column definitions dynamically
    gb = GridOptionsBuilder.from_dataframe(st.session_state.results[show_cols])
    gb.configure_selection(use_checkbox=True)
    gridOptions = gb.build()
    grid_response = AgGrid(
        dataframe=st.session_state.results[show_cols],
        gridOptions = gridOptions,
        update_mode=GridUpdateMode.FILTERING_CHANGED | GridUpdateMode.SELECTION_CHANGED,
        data_return_mode = DataReturnMode.FILTERED
    )

    print(grid_response['selected_rows'])
    selected_rows = grid_response['selected_rows']

query_selected_rows = []
if query_params.get('article_id', []):
    query_param_article = article_manager.articles_df.query(f"id == {int(query_params.get('article_id')[0])}")
    if query_param_article.shape[0] > 0:
        #st.session_state.results = query_param_article
        query_selected_rows = query_param_article[show_cols].to_dict('records')
        
    
if len(selected_rows) > 0:
    st.header("Read Article")
    st.write(pd.DataFrame(selected_rows))
    st.session_state.selected_article = st.session_state.results.query(f"title == '{selected_rows[0]['title']}'").to_dict('records')[0]
    if st.session_state.language == "English":
        st.write(st.session_state.selected_article['translation'])
    else:
        st.write(st.session_state.selected_article['text'])
    st.experimental_set_query_params(article_id=st.session_state.selected_article['id'])
    
elif len(query_selected_rows) > 0:
    st.header("Read Article")
    query_params_article_df = article_manager.articles_df.query(f"id == {int(query_params.get('article_id')[0])}")
    st.write(pd.DataFrame(query_params_article_df[show_cols]))
    st.session_state.selected_article = article_manager.articles_df.query(f"id == {int(query_params.get('article_id')[0])}").to_dict('records')[0]
    if st.session_state.language == "English":
        st.write(st.session_state.selected_article['translation'])
    else:
        st.write(st.session_state.selected_article['text'])

