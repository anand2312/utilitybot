from typing import Any

from aiohttp import ClientSession
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from loguru import logger

from bot.apis import dictionary  # add more clients here as we go


class UtilityBot(commands.Bot):
    """
    Subclass of commands.Bot - to add some custom functionality.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.slash = SlashCommand(self, sync_commands=True, override_type=True)

        self.initialize_api_clients()

    async def on_ready(self) -> None:
        logger.info("Ready!")
        if not getattr(self, "http_session", None):
            self.http_session = ClientSession()
            logger.info("Created HTTP ClientSession")

    async def on_command_error(self, ctx: commands.Context, error: Any) -> None:
        ignored = (commands.CommandNotFound,)
        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"This command is on cooldown; wait {int(error.retry_after)} seconds 🙂",
                delete_after=7,
            )
            return
        else:
            raise error

    def initialize_api_clients(self) -> None:
        # instantiate more clients here as we go
        self.dictionary_client = dictionary.DictionaryClient(self)
