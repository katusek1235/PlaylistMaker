from pathlib import Path
from sys import exit
from os.path import sep as path_sep

playlist_base_name = "muzyka"
playlist_dir = Path("D:\\muzyka")
exclusions = {Path("ting"), Path("sfx"), Path("midi"), Path("FL"),
              Path("moja muzyka"), Path("hard") / "dwarfs"}
global_exclusions = {"converted"}
playlist_separator = " | "

def add_to_playlist(playlist_name,video_name):
    print("Playlist: " + playlist_name)
    print("Video: " + video_name)
    pass

for file in playlist_dir.rglob("*"):
    if any([file.is_relative_to(playlist_dir / ex) for ex in exclusions]):
        continue
    if any([(path_sep + ex + path_sep) in str(file) for ex in global_exclusions]):
        continue
    
    if str(file.parent.relative_to(playlist_dir)) == ".":
        add_to_playlist(playlist_base_name,file.stem)
    
    add_to_playlist(playlist_base_name + playlist_separator + str(file.parent.relative_to(playlist_dir)).replace(path_sep,playlist_separator),file.stem)
    # maybe add removing -(p) at end 
    # maybe replace _ and - with spaces