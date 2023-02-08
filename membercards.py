from PIL import Image, ImageFont, ImageDraw
from constants.directories import PFP_DIR, MEMBERCARDS_DIR, TEMPLATE_DIR

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