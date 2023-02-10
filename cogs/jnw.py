import discord
from discord.ext import commands
from discord import app_commands
from typing import Union, Optional

from jnw_fileops import get_acc_pts, get_bal_pts, update_pts
from constants.roles import CORE_TEAM_ROLE_ID

class JNWPoints(commands.GroupCog, name='jnw'):
    def __init__(self) -> None:
        super().__init__()

    @app_commands.command(name='view')
    @app_commands.describe(member='the member to query the $JNW for, defaulting to yourself if omitted')
    async def view_points(self, interaction: discord.Interaction, member: Optional[discord.Member]):
        """Get the balance $JNW of yourself or the selected member."""
        member = member or interaction.user

        accumulated = get_acc_pts(member.id)
        balance = get_bal_pts(member.id)
        
        embed = discord.Embed(title=f'{member}')
        embed.add_field(name='Accumulated $JNW', value=accumulated, inline=False)
        embed.add_field(name='Balance $JNW', value=balance, inline=False)
        
        avatar = member.avatar.url
        embed.set_thumbnail(url=avatar)
        await interaction.response.send_message(embed=embed)
    

    @app_commands.command(name='update')
    @app_commands.describe(points='amount of $JNW to update', target='selected member or role for the entered $JNW to be updated')
    @app_commands.checks.has_role(CORE_TEAM_ROLE_ID)
    async def update_member(self, interaction: discord.Interaction, points: int, target: Union[discord.Member, discord.Role]):
        """Update the $JNW points of the selected member or members of the selected role."""
        d = ''
        t = ''
        if points > 0:
            t = 'Added'
            d = 'received'
        else: 
            t = 'Deducted'
            d = 'lost'

        if isinstance(target, discord.Member):
            prev_bal = get_bal_pts(target.id)
            update_pts(target.id, points)
            new_bal = get_bal_pts(target.id)

            embed = discord.Embed(title=f'$JNW {t}!', description=f'{target.name} {d} `{points}` $JNW.')
            avatar = target.avatar.url
            embed.set_thumbnail(url=avatar)
            embed.add_field(name='Previous Balance', value=f'{prev_bal} $JNW', inline=False)
            embed.add_field(name='Current Balance', value=f'{new_bal} $JNW', inline=False)
            
            await interaction.response.send_message(embed=embed)
        
        elif isinstance(target, discord.Role):
            await interaction.response.defer(thinking=True, ephemeral=True)

            members = target.members
            total_affected = len(members)
            member_id = [member.id for member in members]
            memberlist = [f'<@{id}>' for id in member_id]
            
            update_pts(member_id, points)
            
            embed = discord.Embed(title=f'$JNW {t}!', description=f'`{total_affected}` members of role `{target.name}` {d} `{points}` $JNW.')
            
            namelist_str = ', '.join(memberlist)
            if len(namelist_str) < 1000:
                embed.add_field(name='Member List', value=namelist_str)

            await interaction.followup.send(embed=embed)
        
        else:
            print(f'{type(target)}: {target}')
            await interaction.response.send_message('An unknown error occured.')
        
async def setup(bot: commands.Bot):
    await bot.add_cog(JNWPoints())
        