import os

from dotenv import find_dotenv, load_dotenv
from discord.ext import commands
from loguru import logger

from bot.internal.bot import UtilityBot

load_dotenv(find_dotenv())


EXTENSIONS = {"jishaku"}

bot = UtilityBot(
    command_prefix=commands.when_mentioned_or("u!"),
    help_command=commands.MinimalHelpCommand(),
)  # TODO: implement helpcommand

for ext in EXTENSIONS:
    try:
        bot.load_extension(ext)
    except Exception as e:
        logger.error(f"Exception while loading {ext} extension:\n{e}")
    else:
        logger.info(f"Loaded extension: {ext}")

bot.run(os.getenv("TOKEN"))
