from typing import Tuple, Union, List, Optional
import os
import json
import random
from pydub import AudioSegment
import logging 
import streamlit as st  # Required for @st.cache_data

logger = logging.getLogger("playlistManager")

LANG_ENGLISH = "en"
LANG_CHINESE = "cn"

class PlaylistManager:
    def __init__(self):
        pass

    def init_playlist(self) -> None:
        """Initialize the playlist environment."""
        pass

    def check_audio_files_exist(self, article_ids: List[int], lang: str) -> Tuple[bool, Optional[int]]:
        """Check if audio files for the given article IDs exist."""
        pass

    def generate_playlist_from_ids(self, article_ids: List[int], lang: str) -> int:
        """Generate a playlist from given article IDs and language."""
        pass

    def load_playlist(self, playlist_id: int) -> Tuple[Optional[dict], Optional[str]]:
        """Load and return playlist audio and metadata."""
        pass


class LocalFilePlaylistManager(PlaylistManager):
    def __init__(self, audio_files_dir: str = "audio_files/", playlist_dir: str = "playlists/"):
        self.audio_files_dir = audio_files_dir
        self.playlist_dir = playlist_dir
        self.playlist_metadata_file = os.path.join(self.playlist_dir, "playlist_metadata.json")
        self._init_playlist()
        self._load_playlist_metadata()

    def _init_playlist(self) -> None:
        """Initialize the playlist directory and metadata file if they don't exist."""
        if not os.path.exists(self.playlist_dir):
            os.makedirs(self.playlist_dir)
        if not os.path.exists(self.playlist_metadata_file):
            with open(self.playlist_metadata_file, 'w') as f:
                json.dump({"last_playlist_id": 0, "playlists": {}}, f)

    def check_audio_files_exist(self, article_ids: List[int], lang: str) -> Tuple[bool, Optional[int]]:
        """Check if audio files for the given article IDs exist."""
        prefix = "en_" if lang == LANG_ENGLISH else "cn_"
        for article_id in article_ids:
            if not os.path.exists(os.path.join(self.audio_files_dir, f"{prefix}{article_id}.wav")):
                return False, article_id
        return True, None

    def generate_playlist_from_ids(self, article_ids: List[int], lang: str) -> int:
        """Generate a playlist from given article IDs and language and return the playlist ID.
        if there is a file not found, return error instead
        """
        prefix = "en_" if lang == LANG_ENGLISH else "cn_"
        playlist = AudioSegment.empty()
        valid_article_ids = []

        # for article_id in article_ids:
        #     audio_path = os.path.join(self.audio_files_dir, f"{prefix}{article_id}.wav")
        #     audio = AudioSegment.from_wav(audio_path)
        #     playlist += audio
        for article_id in article_ids:
            audio_path = os.path.join(self.audio_files_dir, f"{prefix}{article_id}.wav")
            print(f"checking if {audio_path} exists")
            if os.path.exists(audio_path):
                #audio = AudioSegment.from_wav(audio_path)
                audio = AudioSegment.from_mp3(audio_path)
                playlist += audio
                valid_article_ids.append(article_id)
            else:
                print(f"Warning: Audio file for article ID {article_id} not found.")

        # Read the metadata from the metadata file
        with open(self.playlist_metadata_file, 'r') as f:
            metadata = json.load(f)

        # Increment to get a new unique playlist_id
        playlist_id = metadata["last_playlist_id"] + 1

        # Update metadata with new playlist_id
        metadata["last_playlist_id"] = playlist_id
        metadata["playlists"][str(playlist_id)] = {"article_ids": valid_article_ids}

        # Write the updated metadata back to the metadata file
        with open(self.playlist_metadata_file, 'w') as f:
            json.dump(metadata, f)

        # Save the playlist audio file
        playlist.export(os.path.join(self.playlist_dir, f"{playlist_id}.wav"), format="wav")

        return str(playlist_id)
    
    def _load_playlist_metadata(self):
        with open(self.playlist_metadata_file, 'r') as f:
            all_metadata = json.load(f)
        self.playlist_metadata = all_metadata

    def load_playlist(self, playlist_id: int) -> Tuple[Optional[dict], Optional[str]]:
        """Load and return playlist metadata and the path to the audio file."""
        # Extract the metadata for the given playlist_id
        playlist_str_id = str(playlist_id)  # Ensure the key is in string format
        if playlist_str_id not in self.playlist_metadata['playlists']:
            return None, None

        metadata = self.playlist_metadata['playlists'][playlist_str_id]
        audio_path = os.path.join(self.playlist_dir, f"{playlist_id}.wav")

        return metadata, audio_path