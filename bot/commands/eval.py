import asyncio
from io import StringIO
from typing import Optional

import discord
from discord.ext import commands

from bot.utils.converters import CodeblockConverter


PISTON_API_URL = "https://emkc.org/api/v1/piston/execute"


class EvalListener(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
    def prepare_file_output(self, content: str, language: str) -> discord.File:
        """
        Put outputs in File objects that will be rendered by Discord.
        """
        lang_to_extension = {
            "python": "py",
            "rust": "rs",
            "javascript": "js"
        }
        buffer = StringIO(content)
        return discord.File(buffer, filename=f"output.{lang_to_extension.get(language, 'txt')}")
        
    async def wait_for_response(self, message: discord.Message) -> bool:
        """
        Waits 30 seconds for the user to respond to evaluate the codeblock.
        """
        await message.add_reaction("▶")
        
        def check(rxn: discord.Reaction, user: discord.User) -> bool:
            return str(rxn.emoji) == "▶" and user == message.author
        
        try:
            _, _ = await self.bot.wait_for("reaction_add", check=check, timeout=30)
        except asyncio.TimeoutError:
            return False
        else:
            return True
        
    async def _run_eval(self, ctx: commands.Context, language: str, code: str) -> dict:
        json = {'language': language, 'source': code}
        async with ctx.typing():
            async with self.bot.http_session.post(PISTON_API_URL, json=json) as response:
                return await response.json()
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> Optional[discord.Message]:
        ctx = await self.bot.get_context(message)
        match, code = await CodeblockConverter().convert(ctx, message.content)
        
        language = match.group("lang")
        
        to_eval = await self.wait_for_response(message)
        
        if not to_eval:
            return
        
        eval_data = await self._run_eval(ctx, language, code)
        
        error_msg = eval_data.get("msg")
        if error_msg:
            return await ctx.reply(
                embed=discord.Embed(
                    title="Something went wrong.", description=error_msg, color=discord.Colour.red()
                )
            )
        
        if eval_data["language"] in ("python2", "python3"):
            eval_data["language"] = "python"
            
        output = eval_data["output"].strip().replace("```", '`\u200b``')
        lines = output.splitlines()
        
        file = self.prepare_file_output(output, language)
        return await ctx.reply(file=file)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(EvalListener(bot))
