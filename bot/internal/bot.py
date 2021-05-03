from aiohttp import ClientSession
from discord.ext import commands
from loguru import logger


# TODO: ???
class UtilityBot(commands.Bot):
    """
    Subclass of commands.Bot - to add some custom functionality.
    """

    async def on_ready(self) -> None:
        logger.info("Ready!")
        if not getattr(self, "http_session"):
            self.http_session = ClientSession()
            logger.info("Created HTTP ClientSession")
