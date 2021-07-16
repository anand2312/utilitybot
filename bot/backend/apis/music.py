"""interacting with the music api"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# for debugging
import pprint


# Only for testing.
# Will access it from the music command's python file.
client_id = "bro"
client_secret = "bro"

# Only for testing.
# Make from music command's file and pass it to the class in this file
auth_manager = SpotifyClientCredentials(client_id, client_secret)

# TODO: Make everything async


class MusicClient:
    """Manage music searches and recommendations"""

    def __init__(self, auth_manager: SpotifyClientCredentials):
        self.spotify = spotipy.Spotify(auth_manager=auth_manager)

    def fetch_data(self, query_type: str, query: str, number_of_results: int = 1):
        """Fetch track/album/artist data in unusable form"""

        data = self.spotify.search(query, number_of_results, type=query_type)
        pprint.pprint(data["tracks"]["items"][0])

    # def parse_data(self, data):


# a = MusicClient(auth_manager)
# a.fetch_data("track", "bro", 1)
