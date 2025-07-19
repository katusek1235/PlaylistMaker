<p align="center">
<img src="logo.png" alt="drawing" width="200"/>
</p>

> [!WARNING]
> This is absolutely not production ready this is only hobbyist project

# Playlist maker

A python script that makes a youtube playlist with original videos of all files in a directory

# Dependencies

[Python > v3.5 (not tested)](https://www.python.org/)

[google-api-python-client](https://pypi.org/project/google-api-python-client/)

[google-auth-oauthlib](https://pypi.org/project/google-auth-oauthlib/)

[google-auth-httplib2](https://pypi.org/project/google-auth-httplib2/)

# Quick Start

to use this you have to:
- Create or open an existing Google Cloud project and enable youtube v3 api in it
- download the client_secret.json
- set the:
- - playlist_base_name to the name of the playlist
- - playlist_dir to the path of the directory with videos or music
- - exclusions to a list of excluded subdirectories or files
- - global_exclusions to to a list of excluded strings
- - playlist_separator to a string separating playlist name and the subdirectory name
  
##### Running

to run the uploader
```console
$ python playlist.py
```
##### Debugging

to check video index
```console
$ python playlist.py <video_name>
```