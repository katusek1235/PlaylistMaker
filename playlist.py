from typing import List,OrderedDict,Optional
from googleapiclient.discovery import Resource
from pathlib import Path
from sys import exit, platform, argv
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
lost_media:OrderedDict[str,List[str]] = OrderedDict()

cost_limit: int = 9000 # 1000 headroom
video_cost: int = 150 # search + add to playlist
playlist_cost: int = 50 # creating playlist

save_file: Path = Path.cwd() / "save.txt"
config_file: Path = Path.cwd() / "playlist.json"

run_data: List = [0,0,""] # playlist_idx:int,video_idx:int,playlist_id:str

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
    api_result: Optional[tuple[str,str]] = yt_api.get_simmilar_video(youtube,video_name)
    if api_result != None:
        video_id,_ = api_result
        # video_id = video_name
        print("Uploading Video to playlist with id: " + playlist_id)
        yt_api.add_video_to_playlist(youtube,video_id,playlist_id)
        return video_id
    else:
        global lost_media
        if not playlist_id in lost_media:
            lost_media[playlist_id] = []
        lost_media[playlist_id].append(video_name)
        return ""

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
    
def read_save() -> None:
    global run_data
    if save_file.exists():
        print("Reading save!")
        with open(save_file,"rb") as save:
            save_data:str = save.read().decode()
        save_lines = save_data.split("\n")
        run_data = [int(save_lines[0]),int(save_lines[1]),save_lines[2]]
    else:
        run_data = [0,0,""]
    
def save_and_exit() -> None:
    global run_data
    save_data:str = str(run_data[0]) + "\n" + str(run_data[1]) + "\n" + run_data[2]
    with open(save_file,"wb") as save:
        save.write(save_data.encode())
    print("Exiting!")
    exit(0)
    
def check_cost(used_cost:int,next_cost:int) -> None:
    if used_cost > cost_limit - next_cost:
        print("Used: " + str(used_cost) + " cost! Saving...")
        save_and_exit()
    
def upload_everything() -> None:
    global run_data
    youtube: Resource = yt_api.get_authenticated_service()
    used_cost: int = 0
    
    # run_data = (playlist,video,playlist_id)
    read_save()
    
    start_playlist: int = run_data[0]
    start_video: int    = run_data[1]
    playlist_id: str    = run_data[2]
    for playlist_idx in range(start_playlist, len(playlists)):
        is_saved_playlist: bool = playlist_idx == start_playlist
        check_cost(used_cost,video_cost if is_saved_playlist else playlist_cost)
        run_data[0] = playlist_idx
        
        playlist_name:str = list(playlists.keys())[playlist_idx]
        videos_list:List[str] = list(playlists.values())[playlist_idx]
        if not is_saved_playlist:
            playlist_id = upload_new_playlist(youtube,playlist_name)
            run_data[2] = playlist_id
            used_cost += playlist_cost
            start_video = 0
        
        for video_idx in range(start_video, len(videos_list)):
            check_cost(used_cost,video_cost)
            run_data[1] = video_idx
            upload_video(youtube,videos_list[video_idx],playlist_id)
            used_cost += video_cost

def get_video_idx(name: str) -> List[tuple[str,int,int]]: # returns list of matching video_name, playlist_idx and video_idx
    iterate_playlist_folder(playlist_dir)
    
    matching_videos: List[tuple[str,int,int]] = []
    for (playlist_idx,(playlist_name,video_names)) in enumerate(playlists.items()):
        for (video_idx,video_name) in enumerate(video_names):
            if re.fullmatch(".*" + name + ".*",video_name,re.I) != None:
                matching_videos.append((video_name,playlist_idx,video_idx))

    return matching_videos

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
    print("Total Cost: " + str((total_videos_count * video_cost) + (len(playlists.keys()) * playlist_cost)))
    sure:str = input("Are you sure you want to upload? (y or n)")
    if "y" in sure:
        yt_api.FAIL_FUNCTION = save_and_exit
        upload_everything()
        if save_file.exists():
            os.remove(save_file)
        print("Found " + str(len(list(lost_media))) + " Lost Media: ")
        for playlist_id, videos in list(lost_media.items()):
            print("  Playlist id: " + playlist_id)
            for video_name in videos:
                print("    Video name: " + video_name)