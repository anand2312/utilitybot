"""Search and recommend anime and manga."""
from typing import TYPE_CHECKING, Optional

from bot.utils.constants import ContentType

if TYPE_CHECKING:
    from bot.internal.bot import UtilityBot

# TODO: help finish nino async

API_URL = "https://graphql.anilist.co"
_QUERY = """
query ($search: String) {
  Media (search: $search, type: {type}) {
    title {
      romaji
      english
      native
    }
    siteUrl
  }
}
""".format
CHARACTER_QUERY = """
query ($search: String) {
  Character(search: $search) {
    name {
      first
      last
    }
    siteUrl
  }
}
"""


class ContentNotFoundError(ValueError):
    """Error raised when a specific query could not be found."""


async def get_anime_manga(
    bot: UtilityBot, *, query: str, _type: ContentType
) -> Optional[dict]:
    """
    Gets the URL for a specific anime or manga from the Anilist API.

    Args:
        bot: The running bot instance
        query: The anime or manga name to search for
        _type: Whether to search for anime or manga.

    Returns:
        The requested anime/manga URL and name

    Raises:
        ContentNotFoundError
    """
    query_string = _QUERY(type=_type.value.upper())
    async with bot.http_session.post(
        API_URL, json={"query": query_string, "variables": {"search": query}}
    ) as resp:
        try:
            d = await resp.json()
            d = d["data"]["Media"]
            return {"siteUrl": d["siteUrl"], "title": d["title"]["romaji"]}
        except KeyError as e:
            raise ContentNotFoundError(
                f"Could not find {_type.value} with name {query}"
            ) from e


async def get_character(bot: UtilityBot, *, name: str) -> Optional[dict]:
    """
    Gets the URL for a specific character from the Anilist API.

    Args:
        bot: The running bot instance
        name: The character to search for

    Returns:
        The requested character URL and name

    Raises:
        ContentNotFoundError
    """
    async with bot.http_session.post(
        API_URL, json={"query": CHARACTER_QUERY, "variables": {"search": name}}
    ) as resp:
        try:
            d = await resp.json()
            d = d["data"]["Media"]
            out = {"name": " ".join(d["name"].values()), "siteUrl": d["siteUrl"]}
            return out
        except KeyError as e:
            raise ContentNotFoundError(
                f"Could not find character with name {name}"
            ) from e
