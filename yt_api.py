from typing import Optional, Dict
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from pathlib import Path
from sys import exit

# best docs: https://developers.google.com/resources/api-libraries/documentation/youtube/v3/python/latest/?hl=en

# Scope for full access to YouTube account
SCOPES: list[str] = ['https://www.googleapis.com/auth/youtube']
TOKEN_FILE: Path = Path.cwd() / 'user_token.json'

def get_authenticated_service() -> Resource:
    creds: Optional[Credentials] = None
    
    # Load existing token if available
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # Refresh or get new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if len(list(Path.cwd().rglob("client_secret*"))) != 1:
                print("Cant find client_secret file or there is more than one!")
                exit(1)
            client_secrets_path: Path = list(Path.cwd().rglob("client_secret*"))[0]
            flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
            creds = flow.run_local_server(port=0) # type: ignore
        
        # Save token for future use
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json()) # type: ignore
    
    return build('youtube', 'v3', credentials=creds)

def add_video_to_playlist(youtube, video_id, playlist_id) -> None:
    request = youtube.playlistItems().insert( # type: ignore
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    response = request.execute()
    print(f"Added video {video_id} to playlist {playlist_id}")

def create_playlist(youtube: Resource, name: str) -> str:
    request = youtube.playlists().insert( # type: ignore
        part="snippet",
        body={
            "snippet": {
                "title": name,
            }
        }
    )
    response = request.execute()
    playlist_id = response['id']
    print(f"Created playlist {name} with id {playlist_id}")
    return playlist_id

def get_simmilar_video(youtube: Resource, name: str) -> tuple[str,str]: # returns (video_id,title)
    request = youtube.search().list( # type: ignore
        part='snippet',
        q=name,
        type='video',
        maxResults=1,
        fields='items(id(videoId),snippet(title))'
    )
    response = request.execute()
    item = response.get('items', [])[0]
    video_id: str = item['id']['videoId']
    title: str = item['snippet']['title']
    print(f"Found video {video_id} with title {title} to search query {name}")
    return (video_id,title)

# EXAMPLE:
# if __name__ == "__main__":
#     youtube = get_authenticated_service()
#     
#     (video_id,title) = get_simmilar_video(youtube,"Me at the zoo")
#     playlist_id = create_playlist(youtube,"Python playlist")
#     add_video_to_playlist(youtube,video_id,playlist_id)