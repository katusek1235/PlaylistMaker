from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from pathlib import Path
from sys import exit
import json

# Scope for full access to YouTube account
SCOPES = ['https://www.googleapis.com/auth/youtube']
TOKEN_FILE = Path.cwd() / 'user_token.json'

def get_authenticated_service():
    creds = None
    
    if len(list(Path.cwd().rglob("client_secret*"))) != 1:
        print("Cant find client_secret file or there is more than one!")
        exit(1)
    client_secrets_path = list(Path.cwd().rglob("client_secret*"))[0]
    
    # Load existing token if available
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # Refresh or get new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save token for future use
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('youtube', 'v3', credentials=creds)

def add_video_to_playlist(youtube, video_id, playlist_id):
    request = youtube.playlistItems().insert(
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
    return response

if __name__ == "__main__":
    youtube = get_authenticated_service()
    # Replace with your video and playlist IDs
    # video_id = "yszl2oxi8IY"
    # playlist_id = "PL2JW1S4IMwYubm06iDKfDsmWVB-J8funQ"
    # add_video_to_playlist(youtube, video_id, playlist_id)