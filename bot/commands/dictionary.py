import typing as t

from discord.ext import commands

from bot.apis import dictionary
from bot.internal.bot import UtilityBot


class Dictionary(commands.Cog):
    """
    Standard commands for finding meanings of words.
    """

    def __init__(self, bot: UtilityBot) -> None:
        self.bot = bot
        self.dictionary = bot.dictionary_client

    @commands.command(name="dictionary", aliases=["meaning"], usage="<word>")
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.user)
    async def get_word_meaning(self, ctx: commands.Context, word: str) -> None:
        """
        Find the meaning of a word easily.
        """
        async with ctx.typing():
            api_data = await self.dictionary.fetch_data(word=word)
            parsed_data = self.dictionary.parse_data(api_data)

            embed = self.dictionary.prepare_output(parsed_data, mode="embed")

            await ctx.reply(embed=embed, mention_author=False)


def setup(bot: UtilityBot) -> None:
    bot.add_cog(Dictionary(bot))
