"""Cog to link issues and pull requests from Github."""
import re
from typing import Tuple

import discord
from discord.ext import commands
from loguru import logger


ISSUE_REGEX = re.compile(
    r"((?P<org>[a-zA-Z0-9][a-zA-Z0-9\-]{1,39})\/)?(?P<repo>[\w\-\.]{1,100})#(?P<number>[0-9]+)"
)


class Issues(commands.Cog):
    """
    Cog to link issues and PRs automatically in chat.
    """

    LINK_FORMAT = "https://github.com/{org}/{repo}/issues/{issue_number}".format

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def get_issue_url_parts(self, match: re.Match) -> Tuple:
        as_dict = match.groupdict()

        org = as_dict.get("org") or "cs-gang"
        repo = as_dict.get("repo")
        number = as_dict.get("number")

        return org, repo, number

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        match = ISSUE_REGEX.match(message.content.strip().lower())

        if not match:
            return

        org, repo, num = self.get_issue_url_parts(match)

        logger.info(f"Matched issue: {org}/{repo}#{num}")
        link = Issues.LINK_FORMAT(org=org, repo=repo, issue_number=num)

        await message.reply(link)
        return


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Issues(bot))
