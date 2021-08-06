"""Standard commands for recommending content to other users."""
from typing import List, Union

from discord import Embed, Member
from discord.ext import commands

from bot.backend import anime
from bot.backend import models
from bot.internal.bot import UtilityBot
from bot.internal.context import UtilityContext
from bot.utils import pagination
from bot.utils.constants import ContentType, EmbedColour
from bot.utils.converters import URL


class Recommendations(commands.Cog):
    """Standard commands for recommending content to other users."""

    def __init__(self, bot: UtilityBot) -> None:
        self.bot = bot

    def recommend_output(self, records: List[models.ContentRecord]) -> Embed:
        """
        Prepares the embed output for a `recommend x` command.

        Args:
            records: List of ContentRecord objects, for each user that something was recommended to.

        Returns:
            The embed to be sent as the output.
        """
        if len(records) > 1:
            last_record = records[-1]
            uptil_last = ", ".join([f"<@{r.user_id}>" for r in records[:-1]])
            last = f"<@{last_record.user_id}>'s"
            out = f"Added [{last_record.name}]({last_record.url}) to {uptil_list} and {last} {last_record.type.value} lists."
        else:
            record = records[0]
            out = f"Added [{record.name}]({record.url}) to <@{record.user_id}>'s {record.type.value} list."
        
        em = Embed(
            title="Recommended!",
            description=out,
            color=EmbedColour.Success.value,
        )
        return em  # TODO: add header/footer images with users pfp

    @commands.command(name="recommend")
    async def recommend(
        self,
        ctx: UtilityContext,
        content_type: ContentType,
        members: commands.Greedy[Member],
        *,
        name: Union[URL, str],
    ) -> None:
        """Recommend content to users"""
        async with ctx.typing():
            if isinstance(name, URL):
                embed = ctx.message.embeds[0]
                url = str(name)
                name = embed.title
            else:
                if content_type in [ContentType.Anime, ContentType.Manga]:
                    data = await anime.get_anime_manga(
                        self.bot, query=name, _type=content_type
                    )
                    name = data["title"]
                    url = data["siteUrl"]
                elif content_type == ContentType.Music:
                    data = await self.bot.music_client.fetch_track_data(name)
                    name = data.name
                    url = data.external_urls["spotify"]

            db_records = [
                models.ContentRecord(
                    user_id=member.id,
                    name=name,
                    type=content_type,
                    recommended_by=ctx.author.id,
                    url=url,
                )
                for member in members
            ]

        async with self.bot.db_pool.acquire() as conn:
            for record in db_records:
                db_member = models.User(id=record.user_id)
                await db_member.add_to_list(conn, record=record)

        await ctx.reply(embed=self.recommend_output(db_records))

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
