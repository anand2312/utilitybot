"""Some constants used in the project."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING


from bot.backend.exceptions import BadContentTypeError

if TYPE_CHECKING:
    from bot.internal.context import UtilityContext


class EmbedColour(Enum):
    """
    Colors used throughout embeds returned by the bot.
    """

    Error = 0xFF0000
    Info = 0xF4C2C2
    Success = 0x39FF14
    Warning = 0xFF7900


class VoteEmoji(Enum):
    """
    Emojis used for voting and suggestions.
    """

    Check = "<:check:849985604993548308>"
    Neutral = "<:neutral:849985545333243944>"
    Cross = "<:cross:849985759750389780>"


class ContentType(Enum):
    """
    Types of content that can be tracked by UtilityBot.
    """

    Anime = "anime"
    Manga = "manga"
    Music = "music"

    async def convert(self, ctx: UtilityContext, arg: str) -> "ContentType":
        try:
            return self.__class__(arg.lower())
        except ValueError:
            raise BadContentTypeError(f"{arg} is not a valid ContentType")
