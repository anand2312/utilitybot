from discord.ext import commands

from bot.backend.models import User


class UtilityContext(commands.Context):
    """
    Custom context class with some helper functions.
    """

    @property
    def db_user(self) -> User:
        return User(id=self.author.id)  # type: ignore ; dpy weird
