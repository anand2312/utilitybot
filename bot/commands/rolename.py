"""Randomly choose role name"""

import random
from typing import Dict, List

from aiohttp import ClientResponseError
from decouple import config
from discord import Embed
from discord.ext import commands, tasks
from loguru import logger

from bot.internal.bot import UtilityBot
from bot.internal.context import UtilityContext
from bot.utils.constants import EmbedColour


class Rolenames(commands.Cog):
    """Auto role-name change commands"""

    BASE_URL = "https://utilitybot-misc-backends.an23.workers.dev"
    ROLE_ID = 420169837524942848
    GUILD_ID = 298871492924669954

    def __init__(self, bot: UtilityBot) -> None:
        self.bot = bot
        self.api_key = config("UTILITYBOT_API_KEY")
        self.headers = {"API_KEY": self.api_key}

        self.bot.task_loops["rolename"] = self.change_role_name

    async def get_role_names(self) -> List[str]:
        logger.info("Fetching role names from bot API")
        async with self.bot.http_session.get(
            Rolenames.BASE_URL + "/rolenames", headers=self.headers
        ) as res:
            if not res.status == 200:
                logger.error(
                    f"Bot API returned non-200 status code: {res.status}\n{await res.json()}"
                )
                res.raise_for_status()

            json: Dict[str, List[str]] = await res.json()
            return json["rolenames"]

    async def add_role_name(self, name: str, by: int) -> None:
        logger.info(f"Adding role name {name} by {by}")
        json = {"rolename": name, "added_by": str(by)}
        async with self.bot.http_session.post(
            Rolenames.BASE_URL + "/rolenames", headers=self.headers, json=json
        ) as res:
            if not res.status == 200:
                logger.error(
                    f"Bot API returned non-200 status code: {res.status}\n{await res.json()}"
                )
                res.raise_for_status()

    async def delete_role_name(self, name: str) -> None:
        logger.info(f"Deleting role name {name}")
        json = {"rolename": name}
        async with self.bot.http_session.delete(
            Rolenames.BASE_URL + "/rolenames", headers=self.headers, json=json
        ) as res:
            if not res.status == 200:
                logger.error(
                    f"Bot API returned non-200 status code: {res.status}\n{await res.json()}"
                )
                res.raise_for_status()

    @commands.group(name="rolename", aliases=["rn"])
    async def rn_group(self, ctx: UtilityContext) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid command")

    @rn_group.command(name="add", aliases=["a"])
    async def rn_add(self, ctx: UtilityContext, rolename: str) -> None:
        await self.add_role_name(rolename, ctx.author.id)
        embed = Embed(
            title="Added!",
            description=f"Added **{rolename}** to list",
            colour=EmbedColour.Success.value,
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=embed)

    @rn_group.command(name="remove", aliases=["rm"])
    async def rn_remove(self, ctx: UtilityContext, rolename: str) -> None:
        try:
            await self.delete_role_name(rolename)
        except ClientResponseError:
            await ctx.send(f"Whoops some error occurred \n <@271586885346918400>")
            return

        embed = Embed(
            title="Removed!",
            description=f"Removed **{rolename}** to list",
            colour=EmbedColour.Warning.value,
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=embed)

    @rn_group.command(name="list", aliases=["l"])
    async def rn_list(self, ctx: UtilityContext) -> str:
        names = await self.get_role_names()
        embed = Embed(
            title="List of role names",
            description="\n".join([f"• {name}" for name in names]),
            colour=EmbedColour.Info.value,
        )
        await ctx.reply(embed=embed)

    @tasks.loop(hours=8)
    async def change_role_name(self) -> None:
        guild = self.bot.get_guild(Rolenames.GUILD_ID)
        if not guild:
            logger.warning("get_guild failed in change_role_name. check the cache?")
            return
        role = guild.get_role(Rolenames.ROLE_ID)
        if not role:
            logger.warning("get_role failed in change_role_name. check the cache?")
            return
        new_name = random.choice(await self.get_role_names())
        logger.info(f"Changing role name from {role.name} to {new_name}")
        await role.edit(name=new_name)

    @change_role_name.before_loop
    async def before_rolename_loop(self) -> None:
        logger.info("rolename loop starting")
        await self.bot.wait_until_ready()


def setup(bot: UtilityBot) -> None:
    bot.add_cog(Rolenames(bot))
