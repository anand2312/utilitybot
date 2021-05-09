import os

from dotenv import find_dotenv, load_dotenv
from discord import AllowedMentions
from discord.ext import commands
from loguru import logger

from bot.internal.bot import UtilityBot

load_dotenv(find_dotenv())


CMD_EXTENSIONS = {"jishaku", "bot.commands.dictionary", "bot.commands.reminders"}
SLASH_EXTENSIONS = {"bot.slash_commands.dictionary"}

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


bot.run(os.getenv("TOKEN"))
