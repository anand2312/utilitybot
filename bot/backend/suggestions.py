"""Backend for suggestions command."""
import datetime

import discord

from bot.utils.constants import EmbedColour, VoteEmoji


async def send_to_suggestions(channel: discord.TextChannel, *, embed: discord.Embed) -> None:
    """Send the suggestion embed to the guild's suggestions channel and add vote reactions."""
    m = await channel.send(embed=embed)
    for e in VoteEmoji:
        await m.add_reaction(e.value)
        
def build_embed(suggestion: str, author: discord.Member) -> discord.Embed:
    e = discord.Embed(description=suggestion, color=EmbedColour.Info.value)
    e.set_author(name=author.display_name, icon_url=author.avatar_url)
    e.timestamp = datetime.datetime.utcnow()
    return e
