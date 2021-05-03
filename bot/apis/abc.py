"""Base class definition for the API clients."""
from typing import Any, Optional, Union
from abc import ABC, abstractmethod

from discord import Embed

from bot.internal.bot import UtilityBot


class AbstractAPIClient(ABC):
    def __init__(self, bot: UtilityBot) -> None:
        self.bot = bot

    @abstractmethod
    async def fetch_data(self, *args: Any, **kwargs: Any) -> Optional[dict]:
        pass

    @abstractmethod
    def parse_data(self, data: dict) -> Any:
        pass

    @abstractmethod
    def prepare_output(self, data: Any, mode: str) -> Union[str, Embed]:
        """
        Prepare the final output to be sent to the user.

        Arguments:
            data: The dictionary of the parsed API data.
            mode: The output mode. Can be either "string" or "embed".
            The string output choice exists for the ephemeral messages.
        """
        pass
