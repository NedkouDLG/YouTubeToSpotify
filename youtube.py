import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl


class Playlist(object):
    def __init__(self, id=None, title=None):
        self.id = id
        self.title = title


class Song(object):
    def __init__(self, artist=None, track=None):
        self.artist = artist
        self.track = track


class YouTubeClient(object):

    def __init__(self, credentials_location):

        # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        api_service_name = "youtube"
        api_version = "v3"

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            credentials_location, scopes)
        flow.run_local_server(port=8080, prompt="consent")
        credentials = flow.credentials
        print(credentials.to_json())
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        request = youtube.playlists().list(
            part="snippet,contentDetails",
            maxResults=25,
            mine=True
        )
        response = request.execute()

        print(response)
        self.youtube_client = youtube

    def get_playlists(self):
        request = self.youtube_client.playlists().list(
            part="snippet,contentDetails",
            maxResults=50,
            mine=True
        )
        response = request.execute()
        print(response)
        playlists = [Playlist(item['id'], item['snippet']['title']) for item in response['items']]

        return playlists

    def get_videos_from_playlist(self, playlist_id):
        songs = []
        request = self.youtube_client.playlistItems().list(
            playlistId=playlist_id,
            part="id, snippet",
            maxResults=50
        )
        response = request.execute()
        print(response)
        for item in response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            artist, track = self.get_artist_and_track_from_video(video_id)
            if artist and track:
                songs.append(Song(artist, track))

        return songs

    def get_artist_and_track_from_video(self, video_id):
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        video = youtube_dl.YoutubeDL({}).extract_info(
            youtube_url, download=False
        )

        artist = video['artist']
        track = video['track']

        return artist, track
