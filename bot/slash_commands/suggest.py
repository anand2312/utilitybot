from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

from bot.backend import suggestions as suggest_backend


GUILDS = [298871492924669954,]


class SlashSuggest(commands.Cog):
    """
    Suggestions command: slash command.
    """
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
    @cog_ext.cog_slash(
        name="suggest",
        description="Send a suggestion for this server.",
        options=[
            create_option(
                name="suggestion",
                description="your suggestion",
                option_type=3,
                required=True
            )
        ],
        guild_ids=GUILDS
    )
    async def suggest_command(self, ctx: SlashContext, suggestion: str) -> None:
        embed = suggest_backend.build_embed(suggestion, ctx.author)
        channel = await suggest_backend.get_guild_suggestions_channel(self.bot, ctx.guild.id)
        await suggest_backend.send_to_suggestions(channel, embed=embed)
        
def setup(bot: commands.Bot) -> None:
    bot.add_cog(SlashSuggest(bot))
    
    
