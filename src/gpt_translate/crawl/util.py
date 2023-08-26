from typing import List, Dict, Optional
import time
import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import Tag


def extract_info(elements: List[Tag]) -> List[Dict[str, Optional[str]]]:
    """
    Extract information from a list of elements containing news items.
    
    :param elements: A list of BeautifulSoup Tag objects containing the news items.
    :return: A list of dictionaries containing extracted information.
    """
    extracted_info = []

    for element in elements:
        try:
            title = element.find("p", class_="news-title").text
        except AttributeError:
            title = None

        try:
            link = element.find("a")["href"]
        except (AttributeError, KeyError):
            link = None

        try:
            img_url = element.find("img")["data-echo"]
        except (AttributeError, KeyError):
            img_url = None

        try:
            date = element.find("div", class_="public-time font").text
        except AttributeError:
            date = None

        extracted_info.append({
            "title": title,
            "link": link,
            "image_url": img_url,
            "date": date
        })

    return extracted_info


def scroll_one_step(driver, sleep_time: int=5) -> int:
    """
    Scroll the page down by one step.
    
    :param driver: The Selenium WebDriver object.
    :return: True if the page is scrolled down successfully, False otherwise.
    """
    try:
        height = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_time)
        return height
    except Exception as e:
        print(f"Error scrolling page: {e}")
        return -1
    
def normalize_date(date_value):
    """
    normalize date value
    """
    if date_value is None or not date_value:
        # return default start date
        return "2100-01-01"
    elif len(str(date_value)) == len("2022-07-25"):
        return date_value
    elif len(str(date_value)) == len(str(1547683200000)):
        return pd.to_datetime(date_value, unit='ms').strftime('%Y-%m-%d')
    else:
        return "2100-01-01"