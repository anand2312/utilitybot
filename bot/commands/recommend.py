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

    @commands.command(name="recommend")
    async def recommend(
        self,
        ctx: UtilityContext,
        content_type: ContentType,
        member: Member,
        *,
        name: str,
    ) -> None:
        """Recommend content to users"""
        async with ctx.typing():
            if content_type in [ContentType.Anime, ContentType.Manga]:
                data = await anime.get_anime_manga(
                    self.bot, query=name, _type=content_type
                )
                name = data["title"]
                url = data["siteUrl"]
            elif content_type == ContentType.Music:
                data = await self.bot.music_client.fetch_music_data(name)
                name = data.name
                url = data.external_urls["spotify"]

            db = models.ContentRecord(
                user_id=member.id,
                name=name,
                type=content_type,
                recommended_by=ctx.author.id,
                url=url,
            )

        async with self.bot.db_pool.acquire() as conn:
            await ctx.db_user.add_to_list(conn, record=db)

        await ctx.reply(embed=self.recommend_output(db))

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
