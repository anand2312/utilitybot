from contextlib import asynccontextmanager
from typing import AsyncIterator, List, Optional, Union, TYPE_CHECKING

import discord
from discord.ext import commands

from bot.backend.models import User

if TYPE_CHECKING:
    from bot.internal.bot import UtilityBot


class UtilityContext(commands.Context):
    """
    Custom context class with some helper functions.
    """

    @property
    def db_user(self) -> User:
        return User(id=self.author.id)  # type: ignore ; dpy weird

    @asynccontextmanager
    async def reaction_menu(
        self,
        *,
        message: Optional[discord.Message] = None,
        emojis: List[Union[str, discord.Emoji]],
        wait: int = 60,
        prompt: discord.Embed
    ) -> AsyncIterator[discord.Reaction]:
        """
        Starts a reaction menu. The context manager will automatically clear reactions.
        Args:
            All arguments are keyword-only.
            message: The message object that will be edited to `prompt`. If None, a new message is sent.
            prompt: Embed containing the prompt question.
            emojis: Set of emojis that will be added as reactions.
            wait: seconds to wait before clearing the reactions. Defaults to 60.
        Yields:
            discord.Reaction
        The context manager will automatically clear reactions.
        """
        if message:
            await message.edit(embed=prompt)
        else:
            message: discord.Message = await self.send(embed=prompt)

        emoji_set = set()
        for emoji in emojis:
            await message.add_reaction(emoji)
            emoji_set.add(str(emoji))

        def check(
            reaction: discord.Reaction, user: Union[discord.Member, discord.User]
        ) -> bool:
            return (
                reaction.message == message
                and str(reaction) in emoji_set
                and user == self.author
            )

        self.bot: UtilityBot  # to quite pylance down in the next `wait_for`

        try:
            reaction, _ = await self.bot.wait_for(
                "reaction_add", check=check, timeout=wait
            )
            yield reaction
        finally:
            if not isinstance(
                message.channel, discord.DMChannel
            ):  # clearing reactions in DMs raises Forbidden
                await message.clear_reactions()
