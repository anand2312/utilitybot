"""interacting with the music api"""

import tekore
from decouple import config
from loguru import logger

from bot.backend.exceptions import ContentNotFoundError


class MusicClient:
    """Manage music searches and recommendations"""

    def __init__(self):
        client_id = config("SPOTIFY_CLIENT_ID")
        client_secret = config("SPOTIFY_CLIENT_SECRET")
        app_token = tekore.request_client_token(client_id, client_secret)
        sender = tekore.CachingSender(max_size=30, sender=tekore.AsyncSender())
        self.spotify = tekore.Spotify(app_token, sender=sender, asynchronous=True)

    async def fetch_track_data(self, query: str) -> tekore.model.FullTrack:
        """Fetch track data"""

        logger.info(f"Searching Spotify for {query} MUSIC")

        try:
            (tracks,) = await self.spotify.search(
                query, ("track",), limit=1, include_external="audio"
            )

            return tracks.items[0]

        except tekore.HTTPError as error:
            logger.warning(
                f"Could not find MUSIC with name {query} \nAPI error: {error.response}"
            )
            raise ContentNotFoundError(
                f"Could not find MUSIC with name {query}\n{error.response}"
            )
        except IndexError:
            logger.warning(
                f"Could not find MUSIC with name {query} \nAPI error: nil; API is working fine"
            )
            raise ContentNotFoundError(f"Could not find MUSIC with name {query}")
        except Exception as error:
            logger.warning(
                f"Could not find MUSIC with name {query} \nAPI error: {error}"
            )
            raise ContentNotFoundError(
                f"Could not find MUSIC with name {query} \nPlease wait for a while before trying again"
            ) from error
