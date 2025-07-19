<p align="center">
<img src="logo.png" alt="drawing" width="200"/>
</p>

> [!WARNING]
> This is absolutely not production ready this is only hobbyist project

# Playlist maker

A python script that iterates over a directory and all of its subdirectories and searches youtube for every file it finds then it creates a playlist with the specified name (and subdirectory if its in)

because google has a daily quota of 10.000 "cost" and calls to their api have their cost:
- search 100
- add to playlist 50
- create playlist 50

this script calculates the cost needed to upload the playlist and automatially stop when the quota is reached then saves the progress and allows you to resume it the next day 

# Dependencies

[Python > v3.5 (not tested)](https://www.python.org/)

[google-api-python-client](https://pypi.org/project/google-api-python-client/)

[google-auth-oauthlib](https://pypi.org/project/google-auth-oauthlib/)

[google-auth-httplib2](https://pypi.org/project/google-auth-httplib2/)

# Quick Start

to use this you have to:
- Create or open an existing Google Cloud project and enable youtube v3 api in it
- download the client_secret.json
  
### playlist.json

this file contains the configuration for the script:

```
{
    "playlist_base_name": "<name of the youtube playlist>",
    "playlist_dir": "<path to the playlist folder on the disk>",
    "exclusions": [
        <list of excluded subdirectories and files>
    ],
    "global_exclusions": [<list of excluded strings>],
    "prefixes_to_remove": [<list of prefixes that will be removed when searching (regex)>],
    "suffixes_to_remove": [<list of suffixes that will be removed when searching (regex)>],
    "playlist_separator": "<separator between the playlist name and the subdirectory name>"
}
```
  
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