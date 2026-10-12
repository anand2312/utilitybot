"""Standard anime and manga commands."""

from discord.ext import commands

from bot.backend import anime
from bot.internal.bot import UtilityBot
from bot.internal.context import UtilityContext
from bot.utils.constants import ContentType


class Weeb(commands.Cog):
    """Standard anime and manga commands."""

    def __init__(self, bot: UtilityBot) -> None:
        self.bot = bot

    @commands.command(name="anime")
    async def anime(self, ctx: UtilityContext, *, name: str) -> None:
        """Search Anilist for a specific anime."""
        async with ctx.typing():
            resp = await anime.get_anime_manga(
                self.bot, query=name, _type=ContentType.Anime
            )
            await ctx.send(resp["siteUrl"])

    @commands.command(name="manga")
    async def manga(self, ctx: UtilityContext, *, name: str) -> None:
        """Search Anilist for a specific manga."""
        async with ctx.typing():
            resp = await anime.get_anime_manga(
                self.bot, query=name, _type=ContentType.Manga
            )
            await ctx.send(resp["siteUrl"])

    @commands.command(name="character")
    async def character(self, ctx: UtilityContext, *, name: str) -> None:
        async with ctx.typing():
            resp = await anime.get_character(self.bot, name=name)
            await ctx.send(resp["siteUrl"])


def setup(bot: UtilityBot) -> None:
    bot.add_cog(Weeb(bot))
