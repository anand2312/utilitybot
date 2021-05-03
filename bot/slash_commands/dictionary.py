from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

from bot.apis import dictionary
from bot.internal.bot import UtilityBot


GUILD_IDS = [298871492924669954]  # TODO: make global


class SlashDictionary(commands.Cog):
    """
    Dictionary cog: Slash commands version.
    """

    def __init__(self, bot) -> None:
        print("init runs")
        self.bot = bot
        print(self.bot)

    @cog_ext.cog_slash(
        name="dictionary",
        description="Find the meaning of a word easily.",
        guild_ids=GUILD_IDS,
        options=[
            create_option(
                name="word",
                description="Word to search for",
                option_type=3,
                required=True,
            ),
            create_option(
                name="ephemeral",
                description="Whether the output should be visible to everyone or not",
                option_type=5,
                required=False,
            ),
        ],
    )
    async def slash_dictionary(
        self, ctx: SlashContext, word: str, ephemeral: bool = False
    ) -> None:
        await ctx.defer(hidden=ephemeral)

        api_data = await self.bot.dictionary_client.fetch_data(word=word)
        parsed_data = self.bot.dictionary_client.parse_data(api_data)

        if ephemeral:
            output = self.bot.dictionary_client.prepare_output(
                parsed_data, mode="string"
            )
            await ctx.send(output)
            return
        else:
            embed = self.bot.dictionary_client.prepare_output(parsed_data, mode="embed")
            await ctx.send(embed=embed)
            return


def setup(bot: UtilityBot) -> None:
    bot.add_cog(SlashDictionary(bot))
