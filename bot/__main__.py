from decouple import config
from discord import AllowedMentions
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
}
SLASH_EXTENSIONS = {"bot.slash_commands.dictionary", "bot.slash_commands.reminders"}

bot = UtilityBot(
    command_prefix=commands.when_mentioned_or("u!"),
    help_command=commands.MinimalHelpCommand(),
    allowed_mentions=AllowedMentions(everyone=False, users=True, replied_user=True),
)  # TODO: implement helpcommand

for ext in CMD_EXTENSIONS.union(SLASH_EXTENSIONS):
    try:
        bot.load_extension(ext)
    except Exception as e:
        logger.error(f"Exception while loading {ext} extension:\n{e}")
    else:
        logger.info(f"Loaded extension: {ext}")


bot.run(config("TOKEN"))
