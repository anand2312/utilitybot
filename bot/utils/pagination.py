# TODO: rewrite when dpy 2.0 hits!
"""
Functions and classes to easily handle pagination.
"""
from typing import Any
from discord.ext import menus


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
