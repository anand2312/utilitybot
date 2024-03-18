"""Bot definition."""

from typing import Any
from typing import Mapping
from typing import Type

import discord
from aiohttp import ClientSession
from aioscheduler import Manager
from asyncpg import create_pool
from decouple import config
from discord.ext import commands
from discord_slash import SlashCommand
from loguru import logger

from bot.backend.apis import crypto
from bot.backend.apis import dictionary
from bot.backend.apis import music  # add more clients here as we go
from bot.backend.exceptions import ContentNotFoundError
from bot.backend.models import Guild
from bot.internal.context import UtilityContext


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

        # set logger level
        debug = config("DEBUG", False) == "true"  # if not set, this will be False
        # logger.add(sys.stderr, level="DEBUG" if debug else "INFO")

        # bot variable for list of cryptos to cache
        self._crypto_list = [
            "BTC",
            "ETH",
            "ADA",
            "XRM",
            "XLM",
            "XRP",
            "XNO",
            "VET",
            "DOGE",
        ]

        # cache API response data

        # currently cached APIs include:
        #   'crypto'
        # caches are of format:
        # {cache_name: {last_updated: utc datetime, data: data}}
        self.api_caches: Mapping[str, Mapping[str, Any]] = {}

        # map of running task loops
        self.task_loops = {}

        # create db pool; await on_ready
        # self.db_pool = create_pool(config("DB_URI"))

        self.initialize_api_clients()

    async def on_ready(self) -> None:
        logger.info("Ready!")

        if not getattr(self, "http_session", None):
            # make http client session
            self.http_session = ClientSession()
            logger.info("Created HTTP ClientSession")
            # start task loops
            self.start_task_loops()
            # actually connect to the db
            # await self.db_pool
            # logger.info("Connected to database")

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
        elif isinstance(error, ContentNotFoundError):
            embed = discord.Embed(
                title="Nope", description=error.args[0], color=discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Error.",
                description=str(error.__cause__),
                color=discord.Colour.red(),
            )
            await ctx.send(embed=embed)
            return
        else:
            raise error

    async def on_guild_join(self, guild: discord.Guild) -> None:
        # register new guilds to the database
        logger.info(f"Added to {guild.name} with {guild.member_count} members.")
        db_guild = Guild(id=guild.id)

        async with self.db_pool.acquire() as conn:
            await db_guild.save(conn)
            member_ids = [member.id for member in guild.members]
            await db_guild.bulk_save_members(conn, members=member_ids)

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        # delete the guilds data when they remove the bot
        async with self.db_pool.acquire() as conn:
            await Guild(id=guild.id).delete(conn)

    async def get_context(
        self, message: discord.Message, *, cls: Type[commands.Context] = None
    ) -> commands.Context:
        return await super().get_context(message, cls=cls or UtilityContext)

    def initialize_api_clients(self) -> None:
        # instantiate more clients here as we go
        self.dictionary_client = dictionary.DictionaryClient(self)
        self.crypto_client = crypto.CryptoClient(self)
        self.music_client = music.MusicClient()

    def start_task_loops(self) -> None:
        if len(self.task_loops) == 0:
            logger.warning(
                "No task loops to start. Make sure you've added them to the bot variable."
            )
        for name, task in self.task_loops.items():
            logger.info(f"Starting Loop: {name}")
            task.start()
        logger.info("All task loops started.")
