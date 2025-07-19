from sys import exit, platform, argv
from collections import OrderedDict
from typing import List,Optional
from pathlib import Path
import yt_api
import json
import stat
import os
import re

playlist_base_name: str = ''
playlist_dir: Path = Path()
exclusions: List[Path] = []
global_exclusions: List[str]  = []
prefixes_to_remove: List[str] = []
suffixes_to_remove: List[str] = []
playlist_separator: str = ''

total_videos_count:int = 0
playlists:OrderedDict[str,List[str]] = OrderedDict()
lost_media:List[str] = []

config_file: Path = Path.cwd() / "playlist.json"

def has_hidden_attribute(filepath):
    return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)

def upload_new_playlist(playlist_name:str) -> str:
    print("------------------------------------------")
    print("Uploading Playlist: " + playlist_name)
    playlist_id = yt_api.create_playlist(playlist_name)
    print("Uploaded Playlist with id: " + playlist_id)
    return playlist_id

def find_video(video_name:str):
    print("Searching for Video: " + video_name)
    api_result: Optional[tuple[str,str]] = yt_api.get_simmilar_video(video_name)
    if api_result != None:
        video_id,_ = api_result
        return video_id
    else:
        global lost_media
        lost_media.append(video_name)
        return ""

def upload_video(video_id:str,playlist_id:str) -> None:
    if video_id != "":
        print("Uploading Video to playlist with id: " + playlist_id)
        yt_api.add_video_to_playlist(video_id,playlist_id)

def add_to_playlist(playlist_name:str,video_name:str) -> None:
    global total_videos_count
    global playlists
    total_videos_count += 1
    if not playlist_name in playlists:
        playlists[playlist_name] = []
    playlists[playlist_name].append(video_name)

def remove_suffix(file: str) -> str:
    temp_str: str = file
    for suffix in suffixes_to_remove:
        regex = re.compile(suffix + r'$')
        temp_str = regex.sub('', temp_str)
            
    return temp_str

def remove_prefix(file: str) -> str:
    temp_str: str = file
    for prefix in prefixes_to_remove:
        regex = re.compile(r'^' + prefix)
        temp_str = regex.sub('', temp_str)
            
    return temp_str
    
def format_video_name(file: str) -> str:
    return remove_suffix(remove_prefix(file))

def is_hidden(file: Path) -> bool:
    if platform == 'win32':
        # On Windows: check for hidden attribute
        try:
            attrs = os.stat(file).st_file_attributes
            return bool(attrs & stat.FILE_ATTRIBUTE_HIDDEN)
        except (OSError, AttributeError):
            return False
    else:
        # On Unix (Linux/macOS): hidden if basename starts with '.'
        return file.name.startswith('.')

def iterate_playlist_folder(folder: Path) -> None:
    for file in folder.rglob("*"):
        if any([file.is_relative_to(folder / ex) for ex in exclusions]):
            continue
        if any([ex in str(file) for ex in global_exclusions]):
            continue
        
        if not file.is_file() or is_hidden(file):
            continue
        
        video_name = format_video_name(file.stem)
        if str(file.parent.relative_to(folder)) == ".":
            add_to_playlist(playlist_base_name,video_name)
            continue
        
        add_to_playlist(playlist_base_name + playlist_separator + str(file.parent.relative_to(folder)).replace(os.path.sep,playlist_separator),video_name)
    
def upload_everything() -> None:
    yt_api.init()
    
    for playlist,videos in playlists.items():
        playlist_id = upload_new_playlist(playlist)
        
        for video in videos:
            video_id = find_video(video)
            upload_video(video_id,playlist_id)

def read_config() -> None:
    global playlist_base_name
    global playlist_dir      
    global exclusions        
    global global_exclusions 
    global prefixes_to_remove
    global suffixes_to_remove
    global playlist_separator

    json_config: dict = {}
    with open(config_file,"rb") as config:
        json_config = json.load(config)
    
    playlist_base_name = str(           json_config["playlist_base_name"])
    playlist_dir       = Path(          json_config["playlist_dir"      ])
    exclusions         = list(map(Path, json_config["exclusions"        ]))
    global_exclusions  = list(map(str,  json_config["global_exclusions" ]))
    prefixes_to_remove = list(map(str,  json_config["prefixes_to_remove"]))
    suffixes_to_remove = list(map(str,  json_config["suffixes_to_remove"]))
    playlist_separator = str(           json_config["playlist_separator"])

if __name__ == "__main__":
    read_config()
    iterate_playlist_folder(playlist_dir)
    print("Videos:" + str(total_videos_count))
    print("Playlists: " + str(len(playlists.keys())))
    upload_everything()