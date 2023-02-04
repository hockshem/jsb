import os
from dotenv import load_dotenv
import discord
import logging
from discord import app_commands

load_dotenv()
token = os.getenv('BOT_TOKEN')

JER_GUILD = discord.Object(id=939846269562667059)

class JSBClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=JER_GUILD)
        await self.tree.sync(guild=JER_GUILD)

intents = discord.Intents.default()
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
client = JSBClient(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

@client.tree.command()
@app_commands.describe(text='Text to send in the current channel')
async def send(interaction: discord.Interaction, text: str):
    """Sends the text into the current channel"""
    await interaction.response.send_message(text)

client.run(token, log_handler=handler)