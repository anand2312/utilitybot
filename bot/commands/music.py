"""music commands for recommending music"""

from discord.ext import commands

from bot.backend.apis import music
from bot.internal.bot import UtilityBot
from bot.internal.context import UtilityContext

# For debugging. Remove later
import pprint


class Music(commands.Cog):
    "Standard music commands"

    def __init__(self, bot: UtilityBot) -> None:
        self.bot = bot

        # Using a wrapper for Spotify API
        self.api = self.bot.music_client

    @commands.command(name="song")
    async def song(self, ctx: UtilityContext, *, name: str) -> None:
        """Search the Spotify API (using spotipy) for a specific song."""

        response = await self.api.fetch_song_data(name)
        await ctx.send(response)


def setup(bot: UtilityBot) -> None:
    bot.add_cog(Music(bot))
