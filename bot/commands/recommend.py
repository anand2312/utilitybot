"""Standard commands for recommending content to other users."""
from discord import Embed, Member
from discord.ext import commands
from loguru import logger

from bot.backend import anime
from bot.backend.apis import music
from bot.backend import models
from bot.internal.bot import UtilityBot
from bot.internal.context import UtilityContext
from bot.utils.constants import ContentType, EmbedColour
from bot.utils import pagination


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

        em = Embed(
            title="Recommended!",
            description=f"Added [{record.name}]({record.url}) to <@{record.user_id}>'s {record.type.value} list.",
            color=EmbedColour.Success.value,
        )
        return em  # TODO: add header/footer images with users pfp

    @commands.group(name="recommend")
    async def recommend(self, ctx: UtilityContext) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @recommend.command(name="anime")
    async def recommend_anime(
        self, ctx: UtilityContext, member: Member, *, name: str
    ) -> None:
        """Recommend an anime to another user."""
        async with ctx.typing():
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
            await ctx.db_user.add_to_list(conn, record=db_anime)

        await ctx.reply(embed=self.recommend_output(db_anime))

    @recommend.command(name="manga")
    async def recommend_manga(
        self, ctx: UtilityContext, member: Member, *, name: str
    ) -> None:
        """Recommend a manga to another user."""
        async with ctx.typing():
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
            await ctx.db_user.add_to_list(conn, record=db_manga)

        await ctx.reply(embed=self.recommend_output(db_manga))

    @recommend.command(name="music")
    async def recommend_music(
        self, ctx: UtilityContext, member: Member, *, name: str
    ) -> None:
        """Recommend music to another user."""
        async with ctx.typing():
            data = await self.bot.music_client.fetch_music_data(name)

        db_music = models.ContentRecord(
            user_id=member.id,
            name=name,
            type=ContentType.Music,
            recommended_by=ctx.author.id,
            url=data.external_urls["spotify"],
        )

        async with self.bot.db_pool.acquire() as conn:
            await ctx.db_user.add_to_list(conn, record=db_music)

        await ctx.reply(embed=self.recommend_output(db_music))

    @commands.command(name="recommended", aliases=["list"])
    async def recommended(self, ctx: UtilityContext, list_type: ContentType) -> None:
        """Returns all the content that you've been recommended."""
        async with self.bot.db_pool.acquire() as conn:
            content = await ctx.db_user.get_content_list(conn, content_type=list_type)

        if len(content) == 0:
            await ctx.send(
                embed=Embed(
                    title=f"{ctx.author.display_name}'s {list_type.value} list",
                    description="Nothing to see here!",
                    colour=EmbedColour.Error.value,
                ).set_footer(text="Maybe add one 👀")
            )
            return

        formatted = [
            f"[{r.name}]({r.url})\n_Recommended by_ <@{r.recommended_by}>"
            for r in content
        ]
        menu = pagination.grouped(
            formatted,
            title=f"{ctx.author.display_name}'s {list_type.value} list",
            group_size=4,
        )
        await menu.start(ctx)


def setup(bot: UtilityBot) -> None:
    bot.add_cog(Recommendations(bot))
