"""Search and recommend anime and manga."""

from __future__ import annotations

from loguru import logger

from bot.backend.exceptions import ContentNotFoundError
from bot.internal.bot import UtilityBot
from bot.utils.constants import ContentType


API_URL = "https://graphql.anilist.co"
_QUERY = """
query ($search: String) {{
  Media (search: $search, type: {_type}) {{
    title {{
      romaji
      english
      native
    }}
    siteUrl
  }}
}}
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


async def get_anime_manga(bot: UtilityBot, *, query: str, _type: ContentType) -> dict:
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
    query_string = _QUERY(_type=_type.value.upper())
    async with bot.http_session.post(
        API_URL, json={"query": query_string, "variables": {"search": query}}
    ) as resp:
        logger.info(f"Searching Anilist for {query} {_type.value}")
        try:
            d = await resp.json()
            return {
                "siteUrl": d["data"]["Media"]["siteUrl"],
                "title": d["data"]["Media"]["title"]["romaji"],
            }
        except KeyError as e:
            logger.warning(
                f"Could not find content {_type.value}: {query}\nAPI status: {resp.status}"
            )
            logger.debug(str(d))  # type: ignore ; not unbound
            raise ContentNotFoundError(
                f"Could not find {_type.value} with name {query}"
            ) from e


async def get_character(bot: UtilityBot, *, name: str) -> dict:
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
        logger.info(f"Searching anilist for character: {name}")
        try:
            d = await resp.json()
            out = {
                "name": " ".join(d["data"]["Character"]["name"].values()),
                "siteUrl": d["data"]["Character"]["siteUrl"],
            }
            return out
        except KeyError as e:
            logger.warning(
                f"Could not find character: {name}\nAPI status code {resp.status}"
            )
            logger.debug(str(d))  # type: ignore; nope, not unbound
            raise ContentNotFoundError(
                f"Could not find character with name {name}"
            ) from e
