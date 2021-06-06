"""Argument type converters."""
import itertools
from datetime import timedelta
import re

from discord.ext import commands


FORMATTED_CODE_REGEX = re.compile(
    r"```(?P<lang>[a-z+]+)?\s*" r"(?P<code>.*)" r"\s*" r"```", re.DOTALL | re.IGNORECASE
)


class CodeBlockConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, code: str):
        """
        Returns a codeblock from the message.
        """
        match = FORMATTED_CODE_REGEX.search(code)
        if match:
            code = match.group("code")

        return match, code


class TimeConversionError(Exception):
    pass


class TimeDelta(commands.Converter):
    """
    Converter to convert a time string into a `datetime.timedelta`
    object.
    """

    async def convert(self, ctx: commands.Context, arg: str) -> timedelta:
        return get_timedelta(arg)


def get_timedelta(arg: str) -> timedelta:
    """
    Converts a time string into an equivalent timedelta object.

    Arguments:
        arg: The string to be converted.
    Returns:
        timedelta
    Raises:
        TimeConversionError, if the string wasn't properly formatted.
    """
    try:
        arg = arg.lower()
        amts, units = [], []

        unit_mapping = {
            "h": "hours",
            "hour": "hours",
            "m": "minutes",
            "minute": "minutes",
            "s": "seconds",
            "second": "seconds",
            "d": "days",
            "day": "days",
            "month": "months",  # m already assigned for minutes
            "year": "years",
        }

        grouped = itertools.groupby(arg, key=str.isdigit)

        for key, group in grouped:
            if key:  # means isdigit returned true, meaning they are numbers
                amts.append(int("".join(group)))
            else:
                units.append(
                    unit_mapping["".join(group)]
                )  # convert h -> hours, m -> minutes and so on

        return timedelta(**dict(zip(units, amts)))
    except Exception as e:
        raise TimeConversionError from e
