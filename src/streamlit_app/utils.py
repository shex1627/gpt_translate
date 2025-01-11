# utils.py (continuation)
import os
import json
import random
from pydub import AudioSegment
import streamlit as st

from gpt_translate.articles.JsonArticleManager import JsonArticleManager

LANG_ENGLISH = "English"
LANG_CHINESE = "Chinese"

# Constants for directories
# ideally I should structure my code so that everything doesn't have to operate on files
audio_files_dir = "audio_files/"
playlist_dir = "playlists/"
playlist_metadata_file = os.path.join(playlist_dir, "playlist_metadata.json")

# Initialize playlist directory if it doesn't exist
def init_playlist_dir():
    if not os.path.exists(playlist_dir):
        os.makedirs(playlist_dir)
    if not os.path.exists(playlist_metadata_file):
        with open(playlist_metadata_file, 'w') as f:
            json.dump({"last_playlist_id": 0, "playlists": {}}, f)

def check_audio_files_exist(article_ids, lang):
    prefix = "en_" if lang == LANG_ENGLISH else "cn_"
    for article_id in article_ids:
        if not os.path.exists(os.path.join(audio_files_dir, f"{prefix}{article_id}.wav")):
            return False, article_id
    return True, None

def generate_playlist_from_ids(article_ids, lang):
    prefix = "en_" if lang == LANG_ENGLISH else "cn_"
    playlist = AudioSegment.empty()

    for article_id in article_ids:
        audio_path = os.path.join(audio_files_dir, f"{prefix}{article_id}.wav")
        audio = AudioSegment.from_wav(audio_path)
        playlist += audio

    # Read the metadata from the metadata file
    with open(playlist_metadata_file, 'r') as f:
        metadata = json.load(f)

    # Increment to get a new unique playlist_id
    playlist_id = metadata["last_playlist_id"] + 1

    # Update metadata with new playlist_id
    metadata["last_playlist_id"] = playlist_id
    metadata["playlists"][str(playlist_id)] = {"article_ids": article_ids}

    # Write the updated metadata back to the metadata file
    with open(playlist_metadata_file, 'w') as f:
        json.dump(metadata, f)

    # Save the playlist audio file
    playlist.export(os.path.join(playlist_dir, f"{playlist_id}.wav"), format="wav")

    return playlist_id

# Load and return playlist audio and metadata
def load_playlist(playlist_id):
    # Read the centralized metadata file
    with open(playlist_metadata_file, 'r') as f:
        all_metadata = json.load(f)

    # Extract the metadata for the given playlist_id
    playlist_str_id = str(playlist_id)  # Ensure the key is in string format
    if playlist_str_id not in all_metadata['playlists']:
        return None, None

    metadata = all_metadata['playlists'][playlist_str_id]
    audio_path = os.path.join(playlist_dir, f"{playlist_id}.wav")

    return metadata, audio_path

@st.cache_data
def get_article_manager():
   article_manager = JsonArticleManager(os.environ.get('ARTICLE_DB_PATH', '"C:\\Users\\alistar\\Desktop\\ds\\blogger_translate\\articles_embedding.json"'))
   return article_manager

def play_audio(file):
    audio_bytes = open(file, "rb").read()
    #st.audio(audio_bytes, format="audio/wav")
    st.audio(audio_bytes, format="audio/mp3")

def preview_articles(articles_df):
    st.write("Preview:")
    for title in articles_df['title']:
        st.write(f"- {title}")

def preview_articles(articles_df, show_cols=['title', 'id', 'audio_exist', 'chinese_main_topic', 'chinese_tags']):
    st.write("Preview:")
    st.write(articles_df[show_cols].reset_index(drop=True))