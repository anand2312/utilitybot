"""interacting with the music api"""

import tekore

from decouple import config


class MusicClient:
    """Manage music searches and recommendations"""

    def __init__(self):
        client_id = config("SPOTIFY_CLIENT_ID")
        client_secret = config("SPOTIFY_CLIENT_SECRET")
        app_token = tekore.request_client_token(client_id, client_secret)
        self.spotify = tekore.Spotify(app_token, asynchronous=True)

    async def fetch_music_data(self, query: str):
        """Fetch track/album/artist data in unusable form"""

        (tracks,) = await self.spotify.search(
            query, ("track",), limit=1, include_external="audio"
        )

        return tracks.items[0]
