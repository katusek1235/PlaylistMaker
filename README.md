
# Playlist maker

A python script that makes a youtube playlist with original videos of all files in a directory

# Dependencies

to use this you have to:
- Create or open an existing Google Cloud project and enable youtube v3 api in it
- download the client_secret.json
- set the:
- - playlist_base_name to the name of the playlist
- - playlist_dir to the path of the directory with videos or music
- - exclusions to a list of excluded subdirectories or files
- - global_exclusions to to a list of excluded strings
- - playlist_separator to a string separating playlist name and the subdirectory name

# Quick Start

```console
$ python playlist.py
```
