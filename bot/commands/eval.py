import asyncio
from datetime import datetime
from io import StringIO
from typing import Mapping, Optional

import discord
from discord.ext import commands, tasks

from bot.utils.converters import CodeblockConverter


PISTON_API_URL = "https://emkc.org/api/v1/piston/execute"


class EvalListener(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        # update bot's task loop mapping
        self.bot.task_loops["eval_message_cache"] = self.clear_stale_eval_messages
        self._eval_messages: Mapping[
            discord.Message, discord.Message
        ] = {}  # dict of code message to bot's reply

    @property
    def lang_to_extension(self) -> dict:
        return {"python": "py", "rust": "rs", "javascript": "js"}
  
    def prepare_file_output(self, content: str, language: str) -> discord.File:
        """
        Put outputs in File objects that will be rendered by Discord.
        """
        buffer = StringIO(content)
        return discord.File(
            buffer, filename=f"output.{self.lang_to_extension.get(language, 'txt')}"
        )
    
    def prepare_standard_output(self, content: str, language: str) -> str:
        """
        Put outputs in a codeblock. This output method is preferred until
        Discord finally supports file rendering on mobile as well.
        """
        return (
            f"Ran your **{language}** code\n"
            f"```{self.lang_to_extension.get(language, 'txt')}\n"
            f"{content}\n"
            f"```"
        )
        
    async def wait_for_response(
        self, message: discord.Message, emoji: str = "▶"
    ) -> bool:
        """
        Waits 30 seconds for the user to respond to evaluate the codeblock.
        """
        await message.add_reaction(emoji)

        def check(rxn: discord.Reaction, user: discord.User) -> bool:
            return str(rxn.emoji) == emoji and user == message.author

        try:
            _, _ = await self.bot.wait_for("reaction_add", check=check, timeout=30)
        except asyncio.TimeoutError:
            return False
        else:
            return True

    async def _run_eval(self, ctx: commands.Context, language: str, code: str) -> dict:
        json = {"language": language, "source": code}
        async with ctx.typing():
            async with self.bot.http_session.post(
                PISTON_API_URL, json=json
            ) as response:
                return await response.json()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> Optional[discord.Message]:
        """
        Add a playbutton reaction to messages with codeblocks, to evaluate the code and
        send the output in chat.
        """
        if message.author.bot:
            return

        ctx = await self.bot.get_context(message)
        match, code = await CodeblockConverter().convert(ctx, message.content)

        try:
            language = match.group("lang")
        except AttributeError:
            # match returned None
            return

        to_eval = await self.wait_for_response(message)

        if not to_eval:
            return

        eval_data = await self._run_eval(ctx, language, code)

        error_msg = eval_data.get("msg")
        if error_msg:
            return await ctx.reply(
                embed=discord.Embed(
                    title="Something went wrong.",
                    description=error_msg,
                    color=discord.Colour.red(),
                )
            )

        if eval_data["language"] in ("python2", "python3"):
            eval_data["language"] = "python"

        output = eval_data["output"].strip().replace("```", "`\u200b``")
        lines = output.splitlines()

        # file = self.prepare_file_output(output, language)  TODO: back to files once discord supports
        # reply = await ctx.reply(file=file)
        out = self.prepare_standard_output(output, language)
        reply = await ctx.reply(out)
        # add message to cache
        self._eval_messages[message] = reply

    @commands.Cog.listener()
    async def on_message_edit(
        self, before: discord.Message, after: discord.Message
    ) -> None:
        """
        Re-evaluate code if they are edited.
        """
        if after.author.bot:
            return

        bot_reply = self._eval_messages.get(before)

        if not bot_reply:  # not a code eval block, ignore
            return

        ctx = await self.bot.get_context(after)
        match, code = await CodeblockConverter().convert(ctx, after.content)
        try:
            language = match.group("lang")
        except AttributeError:
            # match returned None
            return

        to_eval = await self.wait_for_response(after, emoji="🔁")

        if not to_eval:
            return

        eval_data = await self._run_eval(ctx, language, code)

        error_msg = eval_data.get("msg")
        if error_msg:
            return await ctx.reply(
                embed=discord.Embed(
                    title="Something went wrong.",
                    description=error_msg,
                    color=discord.Colour.red(),
                )
            )

        if eval_data["language"] in ("python2", "python3"):
            eval_data["language"] = "python"

        output = eval_data["output"].strip().replace("```", "`\u200b``")
        lines = output.splitlines()

        # file = self.prepare_file_output(output, language) TODO: file outputs
        out = self.prepare_standard_output(output, language)
        await bot_reply.delete()
        # reply = await ctx.reply(file=file)
        await ctx.reply(out)

    @tasks.loop(minutes=1)
    async def clear_stale_eval_messages(self) -> None:
        """
        Go through the cache and remove the old messages.
        """
        now = datetime.utcnow()

        for message in self._eval_messages:
            delta = now - message.created_at

            if delta.seconds >= 600:
                del self._eval_messages[message]


def setup(bot: commands.Bot) -> None:
    bot.add_cog(EvalListener(bot))
