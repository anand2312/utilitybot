"""Standard commands for recommending content to other users."""
from discord import Embed, Member
from discord.ext import commands

from bot.backend import anime
from bot.backend import models
from bot.internal.bot import UtilityBot
from bot.internal.context import UtilityContext
from bot.utils.constants import ContentType, EmbedColour


class Recommendations(commands.Cog):
    """Standard commands for recommending content to other users."""

    def __init__(self, bot: UtilityBot) -> None:
        self.bot = bot

    def recommend_output(self, record: models.ContentRecord) -> Embed:
        """
        Prepares the embed output for a `recommend x` command.

        Args:
            record: The ContentRecord object prepared to insert data into the db.

        Returns:
            The embed to be sent as the output.
        """

        return Embed(
            title="Recommended!",
            description=f"Added [{record.name}]({record.url}) to <@{record.user_id}>'s {record.type.value} list.",
            color=EmbedColour.Success,
        )

    @commands.group(name="recommend")
    async def recommend(self, ctx: UtilityContext) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @recommend.command(name="anime")
    async def recommend_anime(
        self, ctx: UtilityContext, member: Member, *, name: str
    ) -> None:
        """Recommend an anime to another user."""
        data = await anime.get_anime_manga(
            self.bot, query=name, _type=ContentType.Anime
        )
        db_anime = models.ContentRecord(
            user_id=member.id,
            name=data["title"],
            recommended_by=ctx.author.id,
            url=data["siteUrl"],
        )

        async with self.bot.db_pool.acquire() as conn:
            await db_anime.save(conn)

        await ctx.reply(embed=self.recommend_output(db_anime))

    @recommend.command(name="manga")
    async def recommend_manga(
        self, ctx: UtilityContext, member: Member, *, name: str
    ) -> None:
        """Recommend a manga to another user."""
        data = await anime.get_anime_manga(
            self.bot, query=name, _type=ContentType.Manga
        )
        db_manga = models.ContentRecord(
            user_id=member.id,
            name=data["title"],
            type=ContentType.Manga,
            recommended_by=ctx.author.id,
            url=data["siteUrl"],
        )

        async with self.bot.db_pool.acquire() as conn:
            await db_manga.save(conn)

        await ctx.reply(embed=self.recommend_output(db_manga))


def setup(bot: UtilityBot) -> None:
    bot.add_cog(Recommendations(bot))
