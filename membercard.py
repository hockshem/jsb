from datetime import date
from os import path

import discord
from discord.ext import commands
from discord.ui import View, Button

from constants.channels import EVENT_CHANNEL_ID, ROLE_CHANNEL_ID
from constants.directories import PFP_DIR, MEMBERCARDS_DIR, TEMPLATE_DIR
from constants.roles import CORE_TEAM_ROLE_ID, COLLAB_TEAM_ROLE_ID, COLLAB_TRAINEE_ROLE_ID, SMART_TRADER_ROLE_ID, OG_ROLE_ID, DESIGNER_ROLE_ID, RAIDER_ROLE_ID, MALE_ROLE_ID, FEMALE_ROLE_ID

from PIL import Image, ImageFont, ImageDraw

async def create_membercard_embed(bot: commands.Bot):
    event_channel = bot.get_channel(EVENT_CHANNEL_ID)
    
    if event_channel.last_message_id is not None: 
        try: 
            last_message = await event_channel.fetch_message(event_channel.last_message_id)
            if last_message.author.id == bot.user.id:
                await last_message.delete()
        except discord.NotFound:
            pass

    title = "Jer's 一周年纪念卡 ✨"
    description = '时光不老，我们不散！💕'
    event_embed = discord.Embed(title=title, description=description)
    
    component_view = View(timeout=None)
    card_button = Button()
    card_button.label = ''
    card_button.emoji = '💌'
    card_button.style = discord.ButtonStyle.success
    card_button.callback = get_membercard
    component_view.add_item(card_button)
    
    event_image_name = 'jer_card.png'
    event_image_path = f'{MEMBERCARDS_DIR}/{event_image_name}'
    file = discord.File(event_image_path, filename=event_image_name)

    event_embed.set_image(url=f'attachment://{event_image_name}')
    await event_channel.send(file=file, embed=event_embed, view=component_view)

async def get_membercard(interaction: discord.Interaction):
    """Get your first anniversary membercard now!"""

    member = interaction.user
    member_roles = [role.id for role in member.roles]

    file_name = f'{member.id}.png'
    membercard_file_path = f'{MEMBERCARDS_DIR}/{file_name}'
    pfp_file_path = f'{PFP_DIR}/{file_name}'

    highest_role_id = member_roles[-1]
    highest_role = ''

    if highest_role_id == CORE_TEAM_ROLE_ID:
        highest_role = 'core_team'
    elif highest_role_id == COLLAB_TEAM_ROLE_ID or highest_role_id == COLLAB_TRAINEE_ROLE_ID:
        highest_role = 'collab_team'
    elif highest_role_id == SMART_TRADER_ROLE_ID:
        highest_role = 'smart_trader'
    elif highest_role_id == OG_ROLE_ID or highest_role_id == DESIGNER_ROLE_ID:
        highest_role = 'og'
    elif highest_role_id == RAIDER_ROLE_ID:
        highest_role = 'raider'
    elif highest_role_id == FEMALE_ROLE_ID:
        highest_role = 'female'
    elif highest_role_id == MALE_ROLE_ID:
        highest_role = 'male'

    if not highest_role:
        await interaction.response.send_message(f'请先到 <#{ROLE_CHANNEL_ID}> 领取身份组。', ephemeral=True)
        return

    pfp_exists = path.exists(pfp_file_path)
    if not pfp_exists:
        await member.display_avatar.with_size(256).save(pfp_file_path)

    joined_date = member.joined_at.date()
    create_membercard(member.id, f'{member.name}#{member.discriminator}', highest_role, f'{get_joined_days(joined_date)}')

    file = discord.File(membercard_file_path, filename=file_name)
    membercard_embed = discord.Embed(title='我的一周年纪念卡 ✨', description='No utilities, no roadmap. Just for the vibes!🤟')

    membercard_embed.set_image(url=f'attachment://{file_name}')
    await interaction.response.send_message(file=file, embed=membercard_embed, ephemeral=True)

def create_membercard(user_id, name, role, joined_days):
    username_mid_anchor = (490, 348)
    days_mid_anchor = (568, 376)
    
    # TODO: add error handling when the pfp doesn't exist yet
    pfp_url = f'{PFP_DIR}/{user_id}.png'
    template_url = f'{TEMPLATE_DIR}/{role}.jpg'

    if user_id == 921256448669933589:
        template_url = f'{TEMPLATE_DIR}/belle.jpg'

    pfp = Image.open(pfp_url)
    template = Image.open(template_url)

    pfp_row_size, pfp_col_size = pfp.size
    region = (352, 53, 352 + pfp_col_size, 53 + pfp_row_size)
    template.paste(pfp, region)

    font = ImageFont.truetype('./fonts/msjhbd.ttc', 20)
    draw = ImageDraw.Draw(template)
    draw.text(username_mid_anchor, name, fill=(255, 255, 255), font=font, anchor='mm')
    draw.text(days_mid_anchor, joined_days, fill=(255, 255, 255), font=font, anchor='mm')

    template.save(f'{MEMBERCARDS_DIR}/{user_id}.png')

def get_joined_days(joined_date):
    today = date.today()
    delta = today - joined_date
    return delta.days