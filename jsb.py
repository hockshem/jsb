from dotenv import load_dotenv
import os 
from typing import List

import discord
from discord.ext import commands
from discord.ext.commands import Context
import logging

from constants.directories import COGS_DIR
from membercard import create_membercard_embed

class JerSideBitch(commands.Bot):
    def __init__(
        self, 
        *args,
        initial_extensions: List[str],
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.initial_extensions = initial_extensions
    
    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            await self.load_extension(extension)
    
    async def on_ready(self):
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        print('------')
        await create_membercard_embed(self)

load_dotenv()
token = os.getenv('BOT_TOKEN')

JER_GUILD = discord.Object(id=939846269562667059)
PREFIX = '?'

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

extensions = [COGS_DIR[2:] + '.' + f[:-3] for f in os.listdir(COGS_DIR) if f.endswith('.py')]
bot = JerSideBitch(command_prefix=PREFIX, intents=intents, initial_extensions=extensions)

@bot.command()
@commands.is_owner()
async def sync(ctx: Context):
    bot.tree.copy_global_to(guild=JER_GUILD)
    synced = await bot.tree.sync(guild=JER_GUILD)
    await ctx.send(f'Synced {len(synced)} commands.')

bot.run(token, log_handler=handler)