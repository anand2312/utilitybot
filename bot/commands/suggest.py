"""Suggestions command"""

from discord.ext import commands

from bot.backend import suggestions as suggest_backend


class Suggest(commands.Cog):
    """
    Create suggestions for the server, which will be relayed to the server's suggestions channel.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="suggest", aliases=["suggestion"])
    async def suggest_command(self, ctx: commands.Context, *, suggestion: str) -> None:
        embed = suggest_backend.build_embed(suggestion, ctx.author)
        channel = await suggest_backend.get_guild_suggestions_channel(
            self.bot, ctx.guild.id
        )
        await suggest_backend.send_to_suggestions(channel, embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Suggest(bot))
