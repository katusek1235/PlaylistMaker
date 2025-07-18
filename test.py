from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pathlib import Path
from sys import exit
import pickle

# Scope for full access to YouTube account
SCOPES = ["https://www.googleapis.com/auth/youtube"]

def get_authenticated_service():
    credentials = None
    pickle_file_path = (Path.cwd() / "token.pickle")
    # Token file stores the user's access and refresh tokens
    if pickle_file_path.exists():
        with open(pickle_file_path, "rb") as token:
            credentials = pickle.load(token)
    # Authenticate if no valid credentials
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if len(list(Path.cwd().rglob("client_secret*"))) != 1:
                print("Cant find client_secret file or there is more than one!")
                exit(1)
            client_secrets_path = list(Path.cwd().rglob("client_secret*"))[0]
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
            credentials = flow.run_local_server(port=0)
        with open(pickle_file_path, "wb") as token:
            pickle.dump(credentials, token)

    return build("youtube", "v3", credentials=credentials)

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
    video_id = "yszl2oxi8IY"
    playlist_id = "PL2JW1S4IMwYubm06iDKfDsmWVB-J8funQ"
    add_video_to_playlist(youtube, video_id, playlist_id)