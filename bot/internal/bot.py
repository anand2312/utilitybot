"""Bot definition."""
import os
from typing import Any, Mapping

import firebase_admin
from aiohttp import ClientSession
from aioscheduler import Manager
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from google.cloud import firestore
from loguru import logger

from bot.backend.apis import dictionary  # add more clients here as we go
from bot.backend.apis import crypto


class UtilityBot(commands.Bot):
    """
    Subclass of commands.Bot - to add some custom functionality.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.slash = SlashCommand(self, sync_commands=True, override_type=True)
        self.manager = Manager(
            5
        )  # creates a Scheduler manager which manages 5 TimedSchedulers.

        # initializing firebase
        self.firebase = firebase_admin.initialize_app()

        # initializing firestore (database)
        self.db = firestore.AsyncClient()

        # set logger level
        debug = (
            os.environ.get("DEBUG", False) == "true"
        )  # if not set, this will be False
        # logger.add(sys.stderr, level="DEBUG" if debug else "INFO")

        # set os.environ to a bot variable for easy access
        self.environ = os.environ

        # bot variable for list of cryptos to cache
        self._crypto_list = ["BTC", "ETH", "ADA", "XRM", "XLM", "XRP", "NANO", "VET", "DOGE"]

        # cache API response data

        # currently cached APIs include:
        #   'crypto'
        # caches are of format:
        # {cache_name: {last_updated: utc datetime, data: data}}
        self.api_caches: Mapping[str, Mapping[str, Any]] = {}

        # map of running task loops
        self.task_loops = {}

        self.initialize_api_clients()

    async def on_ready(self) -> None:
        logger.info("Ready!")

        if not getattr(self, "http_session", None):
            # make http client session
            self.http_session = ClientSession()
            logger.info("Created HTTP ClientSession")
            # start task loops
            self.start_task_loops()

        self.manager.start()
        logger.info("Started Scheduler manager")

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
        self.crypto_client = crypto.CryptoClient(self)

    def start_task_loops(self) -> None:
        if len(self.task_loops) == 0:
            logger.warning(
                "No task loops to start. Make sure you've added them to the bot variable."
            )
        for name, task in self.task_loops.items():
            logger.info(f"Starting Loop: {name}")
            task.start()
        logger.info("All task loops started.")
