"""Schedule reminders for later."""
from datetime import datetime, timedelta

from discord import Embed, Forbidden, User
from discord.ext import commands

from bot.utils.constants import EmbedColour


class Reminder:
    """
    Represents a Reminder.
    """

    def __init__(
        self,
        ctx: commands.Context,
        *,
        delay: timedelta,
        content: str,
        title: str = "Reminder!",
    ) -> None:
        self.ctx = ctx
        self.bot = ctx.bot
        self.target = ctx.author
        self._delay = delay
        self.content = content
        self.title = title

    @property
    def embed(self) -> Embed:
        """
        Embed to be sent to the user.
        """
        set_at = self.ctx.message.created_at
        em = Embed(
            title=self.title,
            description=self.content,
            timestamp=set_at,
            color=EmbedColour.Info.value,
        )
        em.set_author(name=self.target, icon_url=self.target.avatar_url)
        em.set_footer(text="Reminder was set", icon_url=self.ctx.bot.user.avatar_url)

        return em

    def schedule_reminder(self) -> None:
        """
        Schedules a reminder to be sent out later.

        Arguments:
            bot: The running Bot instance
            delay: The time after which the reminder must be sent.
        """
        when = datetime.utcnow() + self._delay
        self.bot.manager.schedule(self.execute_reminder(), when)

    async def execute_reminder(self) -> None:
        """
        Sends the reminder in DMs to the user.
        If the user has DMs disabled, pings the user in channel
        in which they called the command.
        """
        try:
            await self.target.send(embed=self.embed)
        except Forbidden:
            await self.ctx.send(
                content=f"{self.target.mention}, here's your reminder:",
                embed=self.embed,
            )
