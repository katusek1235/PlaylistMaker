from typing import List,OrderedDict
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from pathlib import Path
from sys import exit, platform, argv
import yt_api
import stat
import os
import re

playlist_base_name = "muzyka"
playlist_dir = Path("D:\\muzyka")
exclusions: List[Path] = [Path("ting"), Path("sfx"), Path("midi"), Path("FL"),
                          Path("moja muzyka"), Path("hard") / "dwarfs", Path("GD"),
                          Path("tuba"), Path("undertale"), Path("subnautica"),
                          Path("niklas gustavsson"), Path("nu11"), Path("factorio"),
                          Path("creeper-world-3")]
global_exclusions: List[str]  = [os.path.sep + "converted" + os.path.sep]
prefixes_to_remove: List[str] = [r"yt1s.com - "]   # can be a regex expression
suffixes_to_remove: List[str] = [r"-\(.*\)"]       # can be a regex expression
playlist_separator = " | "

total_videos_count:int = 0
playlists:OrderedDict[str,List] = OrderedDict() # list has List[str],int

cost_limit:int = 9000
save_file: Path = Path("save.txt")


def has_hidden_attribute(filepath):
    return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)

def upload_new_playlist(youtube:Resource, playlist_name:str) -> str:
    print("------------------------------------------")
    print("Uploading Playlist: " + playlist_name)
    playlist_id = yt_api.create_playlist(youtube,playlist_name)
    # playlist_id = playlist_name
    print("Uploaded Playlist with id: " + playlist_id)
    return playlist_id

def upload_video(youtube:Resource, video_name:str,playlist_id:str) -> str:
    print("Searching for Video: " + video_name)
    video_id,_ = yt_api.get_simmilar_video(youtube,video_name)
    # video_id = video_name
    print("Found Video id: " + video_id)
    print("Uploading Video to playlist with id: " + playlist_id)
    yt_api.add_video_to_playlist(youtube,video_id,playlist_id)
    return video_id

def add_to_playlist(playlist_name:str,video_name:str) -> None:
    global total_videos_count
    global playlists
    total_videos_count += 1
    if not playlist_name in playlists:
        playlists[playlist_name] = [[],0]
    playlists[playlist_name][0].append(video_name)
    playlists[playlist_name][1] += 1

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
    
def read_save() -> tuple[int,int,str]: # returns playlist_idx ,video_idx and playlist_id
    if save_file.exists():
        print("Reading save!")
        with open(save_file,"rb") as save:
            save_data:str = save.read().decode()
        save_lines = save_data.split("\n")
        return (int(save_lines[0]),int(save_lines[1]),save_lines[2])
    else:
        return (0,0,"")
    
def save_and_exit(playlist_idx:int,video_idx:int,playlist_id:str) -> None:
    save_data:str = str(playlist_idx) + "\n" + str(video_idx) + "\n" + str(playlist_id)
    with open(save_file,"wb") as save:
        save.write(save_data.encode())
    print("Exiting!")
    exit(0)
    
def check_cost(used_cost:int,playlist_idx:int,video_idx:int,playlist_id:str) -> None:
    if used_cost > cost_limit - 50:
        print("Used: " + str(used_cost) + " cost! Saving...")
        save_and_exit(playlist_idx,video_idx,playlist_id)
    
def upload_everything() -> None:
    youtube: Resource = yt_api.get_authenticated_service()
    used_cost: int = 0
    
    (start_playlist,start_video,playlist_id) = read_save()
    
    for playlist_idx in range(start_playlist, len(playlists)):
        check_cost(used_cost,playlist_idx,0,"")
        
        playlist_name:str = list(playlists.keys())[playlist_idx]
        videos_list:List[str] = list(playlists.values())[playlist_idx][0]
        if playlist_idx != start_playlist:
            playlist_id = upload_new_playlist(youtube,playlist_name)
        used_cost += 50
        
        if playlist_idx != start_playlist:
            start_video = 0
        
        for video_idx in range(start_video, len(videos_list)):
            check_cost(used_cost,playlist_idx,video_idx,playlist_id)
            upload_video(youtube,videos_list[video_idx],playlist_id)
            used_cost += 50

def get_video_idx(name: str) -> List[tuple[str,int,int]]: # returns list of matching video_name, playlist_idx and video_idx
    iterate_playlist_folder(playlist_dir)
    
    matching_videos: List[tuple[str,int,int]] = []
    for (playlist_idx,(playlist_name,videos_data)) in enumerate(playlists.items()):
        for (video_idx,video_name) in enumerate(videos_data[0]):
            if re.match(name,video_name,re.I) != None:
                matching_videos.append((video_name,playlist_idx,video_idx))

    return matching_videos

if __name__ == "__main__":
    if len(argv) > 1:
        matching_videos: List[tuple[str,int,int]] = get_video_idx(argv[1])
        print("Matching videos: ")
        for (video_name,playlist_idx,video_idx) in matching_videos:
            print("Name: " + video_name)
            print("Playlist index: " + str(playlist_idx))
            print("Video index: " + str(video_idx))
        exit(0)
    iterate_playlist_folder(playlist_dir)
    print("Videos:" + str(total_videos_count))
    print("Playlists: " + str(len(playlists.keys())))
    print("Total Cost: " + str((total_videos_count * 50) + (len(playlists.keys()) * 50)))
    sure:str = input("Are you sure you want to upload? (y or n)")
    if "y" in sure:
        upload_everything()
        if save_file.exists():
            os.remove(save_file)