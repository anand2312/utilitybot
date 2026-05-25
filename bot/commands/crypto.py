"""Standard commands for getting cryptocurrency values."""

from datetime import datetime

from discord.ext import commands, tasks
from loguru import logger

from bot.internal.bot import UtilityBot


class Crypto(commands.Cog):
    """
    Standard commands for getting cryptocurrency values.
    """

    def __init__(self, bot: UtilityBot) -> None:
        self.bot = bot
        self.api = bot.crypto_client

        # adding task loop to bot variable
        self.bot.task_loops["crypto"] = self.crypto_cache_loop

    @commands.group(name="crypto", invoke_without_command=True)
    async def crypto_group(self, ctx: commands.Context, crypto: str) -> None:
        """
        Gets data about specified cryptocurrency.
        Currently supported crypto include:
            "BTC", "ETH", "ADA", "XRM", "XLM", "XRP", "NANO", "IOTA", "VET"
        """

        cached_data = self.bot.api_caches["crypto"]

        if not cached_data and (len(self.bot.api_caches) != 0):
            raise ValueError(
                "Looks like the cache wasn't ready yet. Please try again later."
            )

        embed = self.api.prepare_output(cached_data["data"][crypto.upper()])
        embed.timestamp = cached_data["last_updated"]
        embed.set_footer(text="Data last updated", icon_url=self.bot.user.avatar_url)

        logger.debug(f"Crypto command called by {ctx.author} for crypto {crypto}")

        await ctx.send(embed=embed)

    def _update_cache(self, data: dict) -> None:
        """
        Updates the bot's internal cache with the crypto data.
        """
        logger.info("Updating crypto cache")
        self.bot.api_caches["crypto"] = {  # type: ignore
            "data": data,
            "last_updated": datetime.utcnow(),
        }

    @tasks.loop(hours=1)
    async def crypto_cache_loop(self) -> None:
        """
        Fetches data every hour from the API
        and updates the cache.
        """
        raw_response = await self.api.fetch_data()
        parsed = self.api.parse_data(raw_response)
        self._update_cache(parsed)
        logger.info("Crypto data fetched")

    @crypto_cache_loop.before_loop
    async def before_crypto_cache(self) -> None:
        logger.info("Crypto data loop starting")
        await self.bot.wait_until_ready()


def setup(bot: UtilityBot) -> None:
    bot.add_cog(Crypto(bot))
