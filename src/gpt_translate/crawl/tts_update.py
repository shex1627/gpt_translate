import argparse
import pandas as pd
import os
import yaml
import logging
import torch
from TTS.api import TTS
from gpt_translate.articles.JsonArticleManager import JsonArticleManager

def setup_logging(logging_level, logging_file):
    logging.basicConfig(filename=logging_file, level=logging_level.upper(),
                        format='%(asctime)s %(levelname)s: %(message)s')
    
    # Adding StreamHandler to log to console as well
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging_level.upper())
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logging.getLogger().addHandler(console_handler)
    
    logging.info("Logging setup complete.")

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    logging.info(f"Configuration loaded from {config_file}.")
    return config

def find_missing_audio_files(articles_df, config):
    missing_en = []
    missing_cn = []
    for idx, row in articles_df.iterrows():
        article_id = row['id']
        en_audio_path = os.path.join(config['AUDIO_DIRECTORY'], f'en_{article_id}.wav')
        cn_audio_path = os.path.join(config['AUDIO_DIRECTORY'], f'cn_{article_id}.wav')
        
        if not os.path.exists(en_audio_path):
            missing_en.append(article_id)
        if not os.path.exists(cn_audio_path):
            missing_cn.append(article_id)
            
    return missing_en, missing_cn

def main():
    parser = argparse.ArgumentParser(description='Generate TTS audio for articles.')
    parser.add_argument('--config', type=str, required=True, help='Path to the config.yaml file')
    parser.add_argument('--logging_file', type=str, default='tts_audio.log', help='Logging file path')
    parser.add_argument('--logging_level', type=str, default='info', help='Logging level')

    args = parser.parse_args()

    setup_logging(args.logging_level, args.logging_file)
    config = load_config(args.config)
    
    article_manager = JsonArticleManager(config['ARTICLE_DB_PATH'])
    articles_df = article_manager.articles_df.query("id > 1200")
    logging.info(f"Loaded {len(articles_df)} articles from {config['ARTICLE_DB_PATH']}.")

    missing_en, missing_cn = find_missing_audio_files(articles_df, config)
    logging.info(f"Found {len(missing_en)} articles missing English audio and {len(missing_cn)} articles missing Chinese audio.")

    # device = "cuda" if torch.cuda.is_available() else "cpu"
    # logging.info(f"Using device: {device}")

    # Initialize English TTS
    eng_tts = TTS(config['tts_english']['model_name'], progress_bar=True)

    # Initialize Chinese TTS
    cn_tts = TTS(config['tts_chinese']['model_name'], progress_bar=True)

    # only run 1 article for testing
    for article_id in missing_en:
        break
        article_text = articles_df[articles_df['id'] == article_id]['translation'].iloc[0]
        en_audio_path = os.path.join(config['AUDIO_DIRECTORY'], f'en_{article_id}.wav')
        logging.info(f"Generating English audio for article ID {article_id}, to {en_audio_path}")
        eng_tts.tts_to_file(text=article_text, file_path=en_audio_path)

    for article_id in missing_cn:
        try:
            article_text = articles_df[articles_df['id'] == article_id]['text'].iloc[0]
            cn_audio_path = os.path.join(config['AUDIO_DIRECTORY'], f'cn_{article_id}.wav')
            logging.info(f"Generating Chinese audio for article ID {article_id}, to {cn_audio_path}")
            cn_tts.tts_to_file(text=article_text, file_path=cn_audio_path)
        except Exception as e:
            logging.error(f"error processing article_id {article_id}")


    logging.info("Audio generation complete.")

if __name__ == '__main__':
    main()
