# TODO: rewrite when dpy 2.0 hits!
"""
Functions and classes to easily handle pagination.
"""
from typing import Any

from discord import Embed
from discord.ext import menus
from more_itertools import chunked

from bot.utils.constants import EmbedColour


class ListEmbedSource(menus.ListPageSource):
    def __init__(self, data: Any) -> None:
        super().__init__(data, per_page=1)

    async def format_page(self, menu: Any, page: Any) -> Any:
        return page


def quick_embed_paginate(embeds: list) -> menus.MenuPages:
    """
    Does the two step process of making ListPageSource, and making MenuPages in one function.

    Usage:
    ```py
    list_of_embeds = [discord.Embed(description=i) for i in range(5)]
    menu = quick_embed_paginate(list_of_embeds)
    await menu.start()
    """
    source = ListEmbedSource(embeds)
    return menus.MenuPages(source=source, clear_reactions_after=True)


def grouped(
    items: list,
    *,
    title: str,
    group_size: int = 3,
    url: str = None,
    colour: EmbedColour = EmbedColour.Info,
) -> menus.MenuPages:
    """
    Split a list into groups of `group_size`, and display each group on it's own embed.

    Args:
        items: The list of items to be grouped and paginated.
        title: The title to be set for the Embeds.
        group_size: The size of each group to be shown on a single embed.
        url: Optional URL for the embeds.
        colour: Optional color for the embeds.
    Returns:
        The MenuPages instance.
    """

    embeds = []

    for chunk in chunked(items, group_size):
        embeds.append(
            Embed(
                title=title,
                colour=colour.value,
                description="\n\n".join(chunk),
                url=url,
            )
        )

    no_of_embeds = len(embeds)

    for page, embed in enumerate(embeds):
        embed.set_footer(text=f"Page {page}/{no_of_embeds}")

    return quick_embed_paginate(embeds)
