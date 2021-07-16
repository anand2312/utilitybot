"""Interacting with the crypto API"""
from typing import Any

from loguru import logger
from decouple import config
from discord import Embed

from bot.backend.apis.abc import AbstractAPIClient
from bot.utils.constants import EmbedColour


class CryptoClient(AbstractAPIClient):
    """
    Gets Cryptocurrency data from the CoinMarketCap API.
    """

    API_URL = "https://pro-api.coinmarketcap.com"

    async def fetch_data(self) -> dict:
        headers = {
            "Accepts": "application/json",
            "Accept-Encoding": "deflate, gzip",
            "X-CMC_PRO_API_KEY": config("COINMARKETCAP_API_KEY"),
        }
        # request data only for the necessary cryptos
        # maintain this as a list on a bot variable
        cryptos = ",".join(self.bot._crypto_list)

        url = CryptoClient.API_URL + "/v1/cryptocurrency/quotes/latest"

        params = {"symbol": cryptos}

        async with self.bot.http_session.get(
            url, headers=headers, params=params
        ) as resp:
            if resp.status == 200:
                logger.info(f"Fetched Crypto data")
            else:
                logger.warning(
                    f"Crypto API returned non-200 status code: {resp.status}"
                    f"Output: {await resp.json()}"
                )
            return await resp.json()

    def parse_data(self, data: dict) -> dict:
        # returns data in the format:
        # name: {
        #   name: coin name,
        #   percentage_change_1h: ...,
        #   percentage_change_24h: ...,
        #   ...
        #   value: ... (USD),
        #  }
        out = {}

        # refer https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyQuotesLatest
        # for format

        all_data = data["data"]

        for coin in all_data.values():
            coin_data = {}
            coin_data["name"] = coin["name"]
            coin_data["symbol"] = coin["symbol"]

            coin_data["percent_change_1h"] = coin["quote"]["USD"]["percent_change_1h"]
            coin_data["percent_change_24h"] = coin["quote"]["USD"]["percent_change_24h"]
            coin_data["percent_change_7d"] = coin["quote"]["USD"]["percent_change_7d"]
            coin_data["percent_change_30d"] = coin["quote"]["USD"]["percent_change_30d"]
            coin_data["price"] = coin["quote"]["USD"]["price"]

            out[coin["symbol"]] = coin_data

        return out

    def prepare_output(self, crypto_data: Any) -> Embed:
        """
        Prepares Embed output for a specified crypto.
        """

        embed = Embed(
            title=f"{crypto_data['symbol']} - {crypto_data['name']}",
            color=EmbedColour.Info.value,
        )

        embed.description = f"**Value**: ${crypto_data['price']}\n"

        embed.add_field(
            name="Percentage Change",
            value=f"1h: {crypto_data['percent_change_1h']}\n"
            f"24h: {crypto_data['percent_change_24h']}\n"
            f"7d: {crypto_data['percent_change_7d']}\n"
            f"30d: {crypto_data['percent_change_30d']}\n",
            inline=False,
        )

        # set embed timestamp before sending

        return embed
