"""Interacting with the dictionary API."""
from logging import error
from typing import List, Optional, Union

from loguru import logger
from discord import Color, Embed

from bot.apis.abc import AbstractAPIClient


class DictionaryClient(AbstractAPIClient):
    API_URL = "https://api.dictionaryapi.dev/api/v2/entries/{language}/{word}".format

    async def fetch_data(self, *, language: str = "en_GB", word: str) -> Optional[list]:
        """
        Fetches data from the API.

        Arguments:
            language: The language the word is in.
            word: The word to find the meaning of.
        Returns:
            list (this API returns a list), of the raw JSON response.
        """
        async with self.bot.http_session.get(
            DictionaryClient.API_URL(language=language, word=word)
        ) as resp:
            if resp.status == 200:
                logger.info(f"Fetched meaning of {word}")
            else:
                logger.warning(
                    f"Dictionary API returned non-200 status code: {resp.status}"
                )
            return await resp.json()

    def parse_data(self, data: Optional[Union[List[dict], dict]] = None) -> dict:
        if not data:
            # data dict not found
            # i.e the API returned non-200 status code and didn't return anything
            return {"error": "An internal exception occurred."}

        if isinstance(data, dict):
            # returned a "word not found response", the title only exists in that case
            return {"error": "Could not find the meaning for the word you searched."}

        data_dict = data[0]

        output = {}

        output["title"] = data_dict["word"]

        # forming a hyperlink for the phonetic pronounciation
        phonetic_text = data_dict["phonetics"][0]["text"]
        phonetic_audio = data_dict["phonetics"][0]["audio"]

        output["phonetic"] = f"[{phonetic_text}]({phonetic_audio})"

        output["meanings"] = []

        for meaning in data_dict["meanings"]:
            part_of_speech = meaning["partOfSpeech"]
            definition = meaning["definitions"][0]["definition"]
            example = meaning["definitions"][0].get("example")

            out_string = f"_({part_of_speech})_ {definition}\n{'_Example: ' + example + '_' if example else ''}\n"
            output["meanings"].append(out_string)

        return output

    def prepare_output(
        self, data: dict, *, mode: str = "embed"
    ) -> Optional[Union[str, Embed]]:
        if mode not in ["string", "embed"]:
            raise TypeError("Mode must be either string or embed.")

        err = data.get("error")
        if err:
            if mode == "string":
                return err
            else:
                return Embed(title="Error", description=err, color=Color.red())

        if mode == "string":
            return self._make_string_output(data)
        else:
            em = Embed(title=data["title"], color=0xF4C2C2)

            em.description = data["phonetic"]
            em.description += data["phonetic"]
            em.description += "\n\n"
            em.description += "\n".join(data["meanings"])

            return em

    def _make_string_output(self, data: dict) -> str:
        out = f"__**Dictionary**__: {data['title']}\n\n"
        out += data["phonetic"]
        out += "\n\n"
        out += "\n".join(data["meanings"])
        return out
