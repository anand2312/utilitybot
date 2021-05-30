import re
from typing import Mapping, Set, Union

import discord
from discord.ext import commands

from bot.utils.constants import EmbedColour

PAIN_PASTE_RE = re.compile(r"(?P<link>https://why\.life\-is\-pa\.in/[A-Za-z0-9]{6})")
POOP_PASTE_RE = re.compile(r"(?P<link>https://poopoolicious\.likes\-throwing\.rocks/[A-Za-z0-9]{6})")

class Starboard(commands.Cog):
        """
        Commands and listeners for the starboard.
        """
        
        def __init__(self, bot: commands.Bot) -> None:
            self.bot = bot
            self._awaiting_stars: Mapping[discord.Message, Set[discord.Member]] = {}
            # mapping of message to list of valid users who have reacted to it with a "star" emoji
            self._starred = set()
                
        async def get_guild_star_emojis(self, guild: int) -> list:
            """
            Get the "star" emojis for a guild from the database.
            """
            # implement this once db middleware is set up
            return ["⭐"]
        
        async def get_guild_star_threshold(self, guild: int) -> int:
            """
            Gets the minimum number of stars set by the guild to send
            a message to the starboard.
            """
            # implement this once db middleware is set up
            return 2
        
        async def get_guild_starboard(self, guild: int) -> discord.TextChannel:
            """
            Gets the guild's starboard channel.
            """
            # implement this once db middleware is set up
            return self.bot.get_channel(839175209851289618)
        
        async def get_valid_reaction_users(self, rxn: discord.Reaction) -> Set[discord.Member]:
            """
            Returns the list of "valid" users from the reaction.
            The person who authored the message, and the bot itself are not valid.
            """
            users = set()
            async for user in rxn.users():
                if user == self.bot.user:
                    continue
                if user == rxn.message.author:
                    continue
                users.add(user)
            return users
        
        def build_embed(self, msg: discord.Message, is_crajy: bool = False) -> discord.Embed:
            embed = discord.Embed(colour=EmbedColour.Info.value)
            embed.set_author(name=msg.author.display_name, url=msg.jump_url, icon_url=msg.author.avatar_url)
            
            embed.description = msg.content

            if len(msg.attachments) > 0:
                attachment = msg.attachments[0]

                if attachment.content_type.startswith("image"):
                    embed.set_image(url=attachment.url)
                
            if is_crajy:
                matched = PAIN_PASTE_RE.search(msg.content) or POOP_PASTE_RE.search(msg.content)
                if not matched:
                    embed.timestamp = msg.created_at
                    return embed
                       
                link = matched.groupdict()["link"]
                embed.set_image(url=link+".png")
            
            emded.timestamp = msg.created_at
            
            return embed        
            
        @commands.Cog.listener()
        async def on_reaction_add(self, reaction: discord.Reaction, user: Union[discord.User, discord.Member]) -> None:
            if reaction.me:
                return
            
            if reaction.message in self._starred:
                return
            
            emojis = await self.get_guild_star_emojis(reaction.message.guild.id)
            if str(reaction) not in emojis:
                return
            
            threshold = await self.get_guild_star_threshold(reaction.message.guild.id)
            
            current_users = self._awaiting_stars.setdefault(reaction.message, set())
            current_users.update(await self.get_valid_reaction_users(reaction))
            self._awaiting_stars[reaction.message] = current_users
            
            if len(current_users) == threshold:
                channel = await self.get_guild_starboard(reaction.message.guild.id)
                
                # just for crajy server, if one of the sharex upload links are sent, use that as the image kwarg for embed
                if reaction.message.guild.id == 298871492924669954:
                    embed = self.build_embed(reaction.message, is_crajy=True)
                else:
                    embed = self.build_embed(reaction.message)
                await channel.send(embed=embed)
                del self._awaiting_stars[reaction.message]
                self._starred.add(reaction.message)
                          
def setup(bot: commands.Bot) -> None:
    bot.add_cog(Starboard(bot))
