"""Some constants used in the project."""
from enum import Enum


class EmbedColour(Enum):
    """
    Colors used throughout embeds returned by the bot.
    """

    Error = 0xFF0000
    Info = 0xF4C2C2
    Success = 0x39FF14
    
class VoteEmoji(Enum):
    """
    Emojis used for voting and suggestions.
    """
    
    Check = "<:check:849985604993548308>"
    Neutral = "<:neutral:849985545333243944>"
    Cross = "<:cross:849985759750389780>"
