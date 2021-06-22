from spotify import Spotify
from youtube import YouTubeClient, Song, Playlist
from flask import Flask, redirect, request
app = Flask(__name__)
spotify = Spotify()
songs = []
chosen_playlist = Playlist()

@app.route("/")
def index():
    auth_url_end = spotify.app_authorization()
    return redirect(auth_url_end)


@app.route("/callback/")
def callback():

    auth_header = spotify.user_authorization()
    user_data = spotify.get_user_info(auth_header)
    check_playlist = spotify.check_playlist_exists(auth_header, chosen_playlist.title)
    if check_playlist:
        playlist_id = check_playlist
    else:
        playlist_id = spotify.create_playlist(user_data["id"], auth_header, chosen_playlist.title)

    for song in songs:
        song_search_info = spotify.add_song_to_playlist(song.artist, song.track, playlist_id, auth_header)
    #song_search_info = spotify.search_song(songs[0].artist, songs[0].track, auth_header)
    close = "You can close the tab!"
    return close


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    youtube_client = YouTubeClient("client_secret.json")
    playlists = youtube_client.get_playlists()

    for index, playlist in enumerate(playlists):
        print(f"{index}: {playlist.title}")

    choice = int(input("Enter your choice: "))
    chosen_playlist = playlists[choice]
    print(f"You selected: {chosen_playlist.title}")
    songs = youtube_client.get_videos_from_playlist(chosen_playlist.id)

    print(f"Attempting to add {len(songs)}")
    app.run(port=8080)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
