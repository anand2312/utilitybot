from bot.internal.bot import UtilityBot
from datetime import datetime

from discord import Embed
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

from bot.backend.reminders import Reminder
from bot.utils.constants import EmbedColour
from bot.utils.converters import TimeDelta


GUILD_IDS = [298871492924669954]


class SlashReminders(commands.Cog):
    """
    Reminders cog: Slash commands version.
    """

    @cog_ext.cog_slash(
        name="remind",
        description="Sets a reminder.",
        options=[
            create_option(
                name="delay",
                description="after how much time you should be reminded",
                option_type=3,
                required=True,
            ),
            create_option(
                name="content",
                description="what to remind you about.",
                option_type=3,
                required=True,
            ),
        ],
        guild_ids=GUILD_IDS,
    )
    async def slash_reminder(self, ctx: SlashContext, delay: str, content: str) -> None:
        await ctx.defer()

        td = await TimeDelta().convert(ctx, delay)
        when = datetime.utcnow() + td

        em = Embed(title="Reminder set!", colour=EmbedColour.Info.value, timestamp=when)
        em.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        em.set_footer(text="You will be reminded", icon_url=ctx.bot.user.avatar_url)

        Reminder(ctx, delay=td, content=content).schedule_reminder()

        await ctx.send(embed=em)


def setup(bot: UtilityBot) -> None:
    bot.add_cog(SlashReminders(bot))
