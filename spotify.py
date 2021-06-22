from secrets import client_id, client_secret, redirect_uri
import requests
import base64
import json
from urllib.parse import quote
from exceptions import TrackNotExistsException
from flask import request


class Spotify(object):
    def __init__(self):
        self.api_uri = "https://api.spotify.com/v1/"
        pass

    def app_authorization(self):
        auth_url = "https://accounts.spotify.com/authorize"
        scope = "user-library-read playlist-modify-public"
        auth_headers = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri + "/callback/",
            "scope": scope
        }
        url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_headers.items()])
        auth_url_end = "{}/?{}".format(auth_url, url_args)
        return auth_url_end

    def user_authorization(self):
        auth_token = request.args["code"]
        code_data = {
            "grant_type": "authorization_code",
            "code": str(auth_token),
            "redirect_uri": redirect_uri + "/callback/"
        }
        client_creds = f"{client_id}:{client_secret}"
        client_creds64 = base64.b64encode(client_creds.encode())

        headers = {
            "Authorization": f"Basic {client_creds64.decode()}"
        }
        token_url = "https://accounts.spotify.com/api/token"
        post_request = requests.post(token_url, data=code_data, headers=headers)
        response = post_request.json()

        access_token = response["access_token"]

        auth_header = {"Authorization": f"Bearer {access_token}"}
        print(auth_header)
        return auth_header

    def get_user_info(self, auth_header):
        response = requests.get(self.api_uri+"me", headers=auth_header)
        data = response.json()
        return data

    def create_playlist(self, user_id, auth_header, playlist_name):
        playlist_uri = self.api_uri + f"users/{user_id}/playlists"
        data = json.dumps({
            "name": str(playlist_name),
            "description": "Automate adding of YouTube Music to Spotify",
            "public": True
        })
        response = requests.post(playlist_uri, data=data, headers=auth_header)
        data = response.json()
        return data["id"]

    def check_playlist_exists(self, auth_header, playlist_name):
        playlist_uri = self.api_uri + "me/playlists"
        response = requests.get(playlist_uri, headers=auth_header)
        data = response.json()
        for item in data["items"]:
            if item["name"] == str(playlist_name):
                return item["id"]
        return False

    def check_song_exists_in_playlist(self, song_uri, playlist_id, auth_header):
        tracks_uri = self.api_uri + f"playlists/{playlist_id}/tracks"
        response = requests.get(tracks_uri, headers=auth_header)
        data = response.json()
        items = data["items"]
        for item in items:
            if song_uri == item["track"]["uri"]:
                return False
        return True

    def search_song(self, artist, track, auth_header):
        song_url_friendly = quote(f"{artist} {track}")
        search_url = self.api_uri + f"search?q={song_url_friendly}&type=track"
        response = requests.get(search_url, headers=auth_header)
        data = response.json()
        results = data["tracks"]["items"]
        if results:
            return results[0]["uri"]
        else:
            raise TrackNotExistsException(response.status_code, f"There is not track : {artist} {track}")

    def add_song_to_playlist(self, artist, track, playlist_id, auth_header):
        song_uri = self.search_song(artist, track, auth_header)
        result = f"Track {track} exists!"
        if self.check_song_exists_in_playlist(song_uri, playlist_id, auth_header):
            playlist_url = self.api_uri + f"playlists/{playlist_id}/tracks"
            js = {"uris": [song_uri]}
            data = json.dumps(js)
            response = requests.post(playlist_url, data=data, headers=auth_header)
            result = f"Track {track} added!"
        return result


