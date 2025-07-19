from selenium.webdriver.common.driver_finder import DriverFinder
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from collections import OrderedDict
from typing import Optional,List
from selenium import webdriver
from pathlib import Path
from time import sleep
from sys import exit

SEARCH_SELECTOR = '.ytSearchboxComponentSearchButton > yt-icon:nth-child(1) > span:nth-child(1) > div:nth-child(1)'
SEARCH_BOX_SELECTOR = '.ytSearchboxComponentInput'
VIDEO_SELECTOR = 'ytd-video-renderer.ytd-item-section-renderer:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > h3:nth-child(1) > a:nth-child(2)'

def get_elem(css_selector:str) -> WebElement:
    return WebDriverWait(driver,60).until(EC.element_to_be_clickable((By.CSS_SELECTOR,css_selector)))

def init():
    options:Options = Options()
    options.page_load_strategy = 'normal'
    global driver
    driver = webdriver.Firefox(options)
    driver.get('https://www.youtube.com/')
    get_elem('ytd-button-renderer.ytd-consent-bump-v2-lightbox:nth-child(2) > yt-button-shape:nth-child(1) > button:nth-child(1)').click()

def add_video_to_playlist(video_id: str, playlist_id: str) -> None:
    print(f"add_video_to_playlist({video_id},{playlist_id})")

def create_playlist(name: str) -> str:
    print(f"create_playlist({name})")
    playlist_id = name.upper()
    return playlist_id

def get_simmilar_video(name: str) -> Optional[tuple[str,str]]: # returns (video_id,title)
    get_elem(SEARCH_BOX_SELECTOR).send_keys(name)
    # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    get_elem(SEARCH_SELECTOR).click()
    video_elem: WebElement = get_elem(VIDEO_SELECTOR)
    if video_elem.get_attribute('href') != None:
        link:str = str(video_elem.get_attribute('href'))
        video_id:str = link[link.find('watch?v='):]
        title:str = str(video_elem.get_attribute('title'))
        print((video_id,title))
        return (video_id,title)
    else:
        return ('','')