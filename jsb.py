import os
from dotenv import load_dotenv
import discord
import logging
from datetime import date
from discord import app_commands
from discord.ui import View, Button
from membercards import create_membercard
from constants.directories import PFP_DIR, MEMBERCARDS_DIR
from constants.roles import CORE_TEAM_ROLE_ID, COLLAB_TEAM_ROLE_ID, SMART_TRADER_ROLE_ID, OG_ROLE_ID, RAIDER_ROLE_ID, MALE_ROLE_ID, FEMALE_ROLE_ID

load_dotenv()
token = os.getenv('BOT_TOKEN')

JER_GUILD = discord.Object(id=939846269562667059)

ROLE_CHANNEL_ID = 1031615410241552434
EVENT_CHANNEL_ID = 1072034044277166151

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

    event_channel = client.get_channel(EVENT_CHANNEL_ID)
    # if not event_channel.last_message_id is None: 
    #     last_message = await event_channel.fetch_message(event_channel.last_message_id)
    #     if last_message.author.id == client.user.id:
    #         await last_message.delete()
    
    title = "Jer's 一周年纪念卡 ✨"
    description = '时光不老，我们不散！💕'
    event_embed = discord.Embed(title=title, description=description)
    
    component_view = View(timeout=None)
    card_button = Button()
    card_button.label = ''
    card_button.emoji = '💌'
    card_button.style = discord.ButtonStyle.success
    card_button.callback = membercard
    component_view.add_item(card_button)
    
    event_image_name = 'jer_card.png'
    event_image_path = f'{MEMBERCARDS_DIR}/{event_image_name}'
    file = discord.File(event_image_path, filename=event_image_name)

    event_embed.set_image(url=f'attachment://{event_image_name}')
    await event_channel.send(file=file, embed=event_embed, view=component_view)

async def membercard(interaction: discord.Interaction):
    """Get your first anniversary membercard now!"""

    member = interaction.user
    member_roles = [role.id for role in member.roles]

    file_name = f'{member.id}.png'
    membercard_file_path = f'{MEMBERCARDS_DIR}/{file_name}'
    pfp_file_path = f'{PFP_DIR}/{file_name}'

    membercard_exists = os.path.exists(membercard_file_path)
    if not membercard_exists:
        highest_role = ''
        if OG_ROLE_ID in member_roles:
            highest_role = 'og'
        elif RAIDER_ROLE_ID in member_roles:
            highest_role = 'raider'
        elif FEMALE_ROLE_ID in member_roles: 
            highest_role = 'female'
        elif MALE_ROLE_ID in member_roles:
            highest_role = 'male'

        if not highest_role:
            await interaction.response.send_message(f'请先到 <#{ROLE_CHANNEL_ID}> 领取身份组。', ephemeral=True)
            return

        pfp_exists = os.path.exists(pfp_file_path)
        if not pfp_exists:
            await member.display_avatar.with_size(256).save(pfp_file_path)

        joined_date = member.joined_at.date()
        create_membercard(member.id, f'{member.name}{member.discriminator}', highest_role, f'{get_joined_days(joined_date)}')

    file = discord.File(membercard_file_path, filename=file_name)
    membercard_embed = discord.Embed(title='我的一周年纪念卡 ✨', description='No utilities, no roadmap. Just for the vibes!🤟')

    membercard_embed.set_image(url=f'attachment://{file_name}')
    await interaction.response.send_message(file=file, embed=membercard_embed, ephemeral=True)

def get_joined_days(joined_date):
    today = date.today()
    delta = today - joined_date
    return delta.days

client.run(token, log_handler=handler)