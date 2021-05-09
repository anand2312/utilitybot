"""Standard reminder command."""
from datetime import datetime
from typing import Optional

from discord import Embed
from discord.ext import commands
from loguru import logger

from bot.backend.reminders import Reminder
from bot.internal.bot import UtilityBot
from bot.utils.converters import TimeDelta
from bot.utils.constants import EmbedColour


class ReminderCog(commands.Cog):
    """
    Standard commands for setting reminders.
    """

    def __init__(self, bot: UtilityBot) -> None:
        self.bot = bot

    @commands.command(name="remind")
    async def remind(
        self, ctx: commands.Context, delay: TimeDelta, *, content: str
    ) -> None:
        """
        Set a reminder to be sent to you at a future time.

        The `delay` argument should be a string, like:
            `3h4m` -> represents 3 hours and 4 minutes.
        """
        logger.debug(f"Reminder command called by {ctx.author}")
        when = (
            datetime.utcnow() + delay
        )  # type: ignore ; pylance won't understand converters
        embed = Embed(
            title="Reminder set!", colour=EmbedColour.Info.value, timestamp=when
        )

        embed.set_footer(text="You will be reminded", icon_url=ctx.bot.user.avatar_url)
        embed.set_author(
            name=ctx.author.display_name, url=ctx.author.avatar_url
        )  # type: ignore ; dpy issue

        Reminder(
            ctx, delay=delay, content=content
        ).schedule_reminder()  # type: ignore ; converter

        await ctx.reply(embed=embed)


def setup(bot: UtilityBot) -> None:
    bot.add_cog(ReminderCog(bot))
