"""Base class definition for the API clients."""
from typing import Any, Optional, Union
from abc import ABC, abstractmethod

from discord import Embed


class AbstractAPIClient(ABC):
    """
    Abstract base class for all API clients.
    """

    def __init__(
        self, bot: "UtilityBot"
    ) -> None:  # type: ignore ; this causes circular importing
        self.bot = bot

    @abstractmethod
    async def fetch_data(self, *args: Any, **kwargs: Any) -> Optional[dict]:
        """
        Get data from the API via HTTP request.
        """
        pass

    @abstractmethod
    def parse_data(self, data: dict) -> Any:
        """
        Parse the raw output sent by the API.

        Arguments:
            data: The raw API response
        Returns:
            Parsed data (of any format)
        """
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
