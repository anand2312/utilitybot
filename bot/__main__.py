import importlib

from decouple import config
from discord import AllowedMentions
from discord import Intents
from discord.ext import commands
from loguru import logger

from bot.internal.bot import UtilityBot


CMD_EXTENSIONS = {
    "jishaku",
    "bot.commands.dictionary",
    "bot.commands.reminders",
    "bot.commands.crypto",
    "bot.commands.eval",
    "bot.commands.suggest",
    "bot.commands.issue_linking",
    "bot.commands.weeb",
    "bot.commands.recommend",
    "bot.commands.music",
    "bot.commands.rolename"
}
SLASH_EXTENSIONS = {"bot.slash_commands.dictionary", "bot.slash_commands.reminders"}

DEBUG = config("DEBUG", default=False, cast=bool)
intents = Intents.default()
intents.members = True
bot = UtilityBot(
    command_prefix=commands.when_mentioned_or("!!" if DEBUG else "u!"),
    help_command=commands.MinimalHelpCommand(),
    intents=intents,
    allowed_mentions=AllowedMentions(everyone=False, users=True, replied_user=True),
)  # TODO: implement helpcommand

for ext in CMD_EXTENSIONS.union(SLASH_EXTENSIONS):
    try:
        bot.load_extension(ext)
    except Exception as e:
        logger.error(f"Exception while loading {ext} extension:\n{e}")
        if DEBUG:
            raise e
    else:
        logger.info(f"Loaded extension: {ext}")


@bot.command(name="reload-module", aliases=["rm"])
@commands.is_owner()
async def reloadm(ctx, name: str) -> None:
    module = importlib.import_module(name)
    importlib.reload(module)
    await ctx.reply(f":white_check_mark: Reloaded {name}")


bot.run(config("TOKEN"))
