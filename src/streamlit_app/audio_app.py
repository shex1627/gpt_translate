import os
import streamlit as st
from pydub import AudioSegment
import pandas as pd
from urllib.request import urlopen
from PIL import Image
import logging 
from streamlit_app.playlistManager import LocalFilePlaylistManager, LANG_ENGLISH, LANG_CHINESE 
from streamlit_app.utils import get_article_manager, play_audio, preview_articles

# Configure the logging system
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("streamlit_app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger()

page_icon = Image.open(urlopen("https://i.imgur.com/z7ZGWvZ.jpg"))
st.set_page_config(page_title="Audiobook", 
                page_icon=page_icon)
st.title("Audiobook Player")

# hide menu
if os.environ.get('HIDE_MENU', 'true') == 'true':
        st.markdown("""
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """, unsafe_allow_html=True)

# Initialize Playlist Manager
audio_files_dir = os.environ.get("AUDIO_DIRECTORY", "C:\\Users\\alistar\\Desktop\\ds\\blogger_translate\\tts\\tts_data")
playlist_dir = os.environ.get("PLAYLIST_DIRECTORY", "/opt/shichenh/tts_data/playlist_data")
MIN_PLAYLIST_SIZE = 5
MAX_PLAYLIST_SIZE = 10

playlist_manager = LocalFilePlaylistManager(
    audio_files_dir=audio_files_dir,
    playlist_dir=playlist_dir)

# initialize session states
if st.session_state.get('first_run', True):
    logger.info("first run")
    st.session_state['playlist_id'] = None
    st.session_state['current_playlist'] = None
    st.session_state['selected_article_ids'] = []
    st.session_state['random_articles'] = pd.DataFrame()
    st.session_state['embedding_articles'] = pd.DataFrame()
    st.session_state['input_articles'] = pd.DataFrame()
    st.session_state['first_run'] = False
else:
    logger.info("not first run")
    logger.info(f"playlist_id: {st.session_state['playlist_id']}")
    logger.info(f"current_playlist: {st.session_state['current_playlist']}")
    logger.info(f"selected_article_ids: {st.session_state['selected_article_ids']}")
    logger.info(f"random_articles: {st.session_state['random_articles'].shape}")
    logger.info(f"embedding_articles: {st.session_state['embedding_articles'].shape}")
    logger.info(f"input_articles: {st.session_state['input_articles'].shape}")


# Load Articles
article_manager = get_article_manager()
articles_df = article_manager.articles_df
playlist_manager.init_playlist()

# Language Selection
lang = st.radio("Select Language", [LANG_CHINESE, LANG_ENGLISH])
if lang == LANG_ENGLISH:
    st.write("You selected English.")
    show_cols = ['english_title', 'english_main_topic', 'english_tags', 'title']
else:
    st.write("你選擇了中文.")
    show_cols = ['title', 'chinese_main_topic', 'chinese_tags']

# Play Articles Playlist
playlist_id = st.experimental_get_query_params().get("playlist_id", None)
logger.info(f"query_params: playlist_id: {playlist_id}")
# parse playlist_id, throw error if not int
try:
    playlist_id = playlist_id[0] if playlist_id else None
    if playlist_id in playlist_manager.playlist_metadata['playlists']:
        st.session_state['playlist_id'] = playlist_id
        logger.debug(f"set session_state['playlist_id'] to {playlist_id}")
    else:
        if playlist_id == None:
            playlist_id = ''
        st.warning(f"Playlist {playlist_id} not found. Generate a playlist from below options or enter a valid playlist_id as query parameter.")
except:
    playlist_id = None
    st.error("Error parsing playlist_id. Please make sure it is an integer.")

if st.session_state['playlist_id']:
    # check if playlist exists in playlist_manager.playlist_metadata
    logger.info(f"play articles section: playlist_id: {playlist_id}")
    metadata, audio_path = playlist_manager.load_playlist(st.session_state['playlist_id'])
    st.write(f"### Playlist {playlist_id}")
    st.write("Articles in this playlist:")
    current_playlist_articles = articles_df[articles_df['id'].isin(metadata['article_ids'])].reset_index(drop=True)
    preview_articles(current_playlist_articles, show_cols=['id']+show_cols)
    play_audio(audio_path)

# Generate Playlist
st.write("### Generate Playlist")

# From random articles
st.write("#### From Random Articles")
num_articles = st.slider("Select number of articles", MIN_PLAYLIST_SIZE, MAX_PLAYLIST_SIZE, key='random_article')
if st.button("Preview Random Articles"):
    random_articles = articles_df.sample(num_articles)
    random_articles['audio_exist'] = random_articles['id'].apply(
        lambda x: playlist_manager.check_audio_files_exist([x], lang)[0])
    st.session_state['random_articles'] = random_articles
if st.session_state['random_articles'].shape[0] > 0:
    logger.info(f"random articles shape: {st.session_state['random_articles'].shape}")
    preview_articles(st.session_state['random_articles'], show_cols=['id', 'audio_exist']+show_cols)
    if st.button("Confirm Random Playlist"):
        logger.info(f"generating playlist with the following ids: {st.session_state['random_articles']['id'].tolist()}")
        random_articles = st.session_state['random_articles']
        valid_article_ids = random_articles[random_articles['audio_exist']]['id'].tolist()
        playlist_id = playlist_manager.generate_playlist_from_ids(valid_article_ids, lang)
        logger.info(f"generated playlist_id: {playlist_id}")
        st.experimental_set_query_params(playlist_id=[playlist_id])
        st.session_state['playlist_id'] = playlist_id
        logger.info(f"set session_state['playlist_id'] to {playlist_id}")
        #st.experimental_rerun() 

# From Search
st.write("#### From Search")
search_term = st.text_input("Search term", max_chars=30)
num_articles = st.slider("Select number of articles", MIN_PLAYLIST_SIZE, MAX_PLAYLIST_SIZE, key="search_terms")
if st.button("Preview Search"):
    if not search_term:
        st.warning("Please input search term")
    else:
        relevant_articles = article_manager.search_by_embedding(search_term, num_articles).copy()
        relevant_articles['audio_exist'] = relevant_articles['id'].apply(
            lambda x: playlist_manager.check_audio_files_exist([x], lang)[0])
        st.session_state['embedding_articles'] = relevant_articles
if st.session_state['embedding_articles'].shape[0] > 0:
    preview_articles(st.session_state['embedding_articles'], show_cols=['id', 'audio_exist']+show_cols)
    if st.button("Confirm Search Playlist", key='confirm_search'):
        valid_article_ids = st.session_state['embedding_articles'][st.session_state['embedding_articles']['audio_exist']]['id'].tolist()
        playlist_id = playlist_manager.generate_playlist_from_ids(valid_article_ids, lang)
        st.experimental_set_query_params(playlist_id=[playlist_id])
        st.session_state['playlist_id'] = playlist_id
        #st.experimental_rerun() 

# From article IDs
st.write("#### From Article IDs")
article_ids_str = st.text_input("Enter comma-separated article IDs")
if st.button("Preview from IDs"):
    if not article_ids_str:
        st.warning("Please input a list of article IDs")
    else:
        try:
            article_ids = [int(id_str) for id_str in article_ids_str.split(",")]
            exist, problematic_id = playlist_manager.check_audio_files_exist(article_ids, lang)
            if exist:
                selected_articles = articles_df[articles_df['id'].isin(article_ids)].copy()
                selected_articles['audio_exist'] = selected_articles['id'].apply(
                    lambda x: playlist_manager.check_audio_files_exist([x], lang)[0])
                st.session_state['input_articles'] = selected_articles
        except Exception as e:
            st.error(f"Error parsing list of article IDs")
            st.error(e)

if st.session_state['input_articles'].shape[0] > 0:
    preview_articles(st.session_state['input_articles'])
    if st.button("Confirm ID Playlist", key='confirm_ids'):
        valid_article_ids = st.session_state['input_articles'][st.session_state['input_articles']['audio_exist']]['id'].tolist()
        playlist_id = playlist_manager.generate_playlist_from_ids(valid_article_ids, lang)
        st.experimental_set_query_params(playlist_id=[playlist_id])
        st.session_state['playlist_id'] = playlist_id
        #st.experimental_rerun() 

        