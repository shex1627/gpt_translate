import streamlit as st
import pandas as pd
from typing import Optional
from gpt_translate.articles.JsonArticleManager import JsonArticleManager

article_manager = JsonArticleManager("C:\\Users\\alistar\\Desktop\\ds\\blogger_translate\\articles_embedding.json")

# Streamlit App
st.set_page_config(page_title="Article Search", layout="wide")
st.title("Article Search")

# Sidebar
st.sidebar.title("Available Tags")
tags_count_df = article_manager.get_tags_count()
st.sidebar.write(tags_count_df)

# Tabs
tab = st.selectbox("Choose Tab", ["Search Articles", "Read Article"])

if tab == "Search Articles":
    st.header("Search Articles")

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

        results = results.head(15)
        selected_article = st.selectbox("Select an article", results.index)
        st.session_state.selected_article = results.loc[selected_article]

        # Show article details
        st.write(results[['title', 'english_main_topic', 'english_tags', 'chinese_tags', 'chinese_main_topic']])

elif tab == "Read Article":
    st.header("Read Article")

    if st.session_state.selected_article is not None:
        selected_article = st.session_state.selected_article
        language = st.radio("Language:", ["English", "Chinese"])

        st.write(selected_article[['title', 'english_main_topic', 'english_tags', 'chinese_tags', 'chinese_main_topic']])

        if language == "English":
            st.write(selected_article['translation'])
        else:
            st.write(selected_article['text'])
    else:
        st.write("Please select an article from the 'Search Articles' tab first.")
