import discord
from discord.ext import commands
from discord import app_commands
from typing import Union, Optional

from jnw_fileops import get_acc_pts, get_bal_pts, update_pts
from constants.roles import CORE_TEAM_ROLE_ID
from constants.channels import RECORDS_CHANNEL_ID

class JNWPoints(commands.GroupCog, name='jnw'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    async def cog_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        err_msg = 'An unknown error occured.'
        if isinstance(error, app_commands.MissingRole):
            err_msg = f'Only <@&{error.missing_role}> can use that command.'
        await interaction.response.send_message(err_msg, ephemeral=True)

    @app_commands.command(name='view')
    @app_commands.describe(target_member='the member to query the $JNW for, defaulting to yourself if omitted')
    async def view_points(
        self, 
        interaction: discord.Interaction, 
        target_member: Optional[discord.Member] = None
    ) -> None:
        """Get the balance $JNW of yourself or the selected member."""
        target_member = target_member or interaction.user

        try:
            accumulated = get_acc_pts(target_member.id)
            balance = get_bal_pts(target_member.id)
        except Exception as e:
            error_embed = discord.Embed(
                title='Error',
                description=f'An error occurred while retrieving $JNW points: {e}'
            )
            await interaction.response.send_message(embed=error_embed)
            return
        
        embed = discord.Embed(title=f'{target_member}')
        embed.add_field(name='Accumulated $JNW', value=accumulated, inline=False)
        embed.add_field(name='Balance $JNW', value=balance, inline=False)
        
        avatar = target_member.avatar.url
        embed.set_thumbnail(url=avatar)
        
        await interaction.response.send_message(embed=embed)
    

    @app_commands.command(name='update')
    @app_commands.describe(points='amount of $JNW to update', target='selected member or role for the entered $JNW to be updated')
    @app_commands.checks.has_role(CORE_TEAM_ROLE_ID)
    async def update_member(
        self, 
        interaction: discord.Interaction, 
        points: int, 
        target: Union[discord.Member, discord.Role]
    ) -> None:
        """Update the $JNW points of the selected member or members of the selected role."""
        
        if points > 0:
            direction = 'received'
            transaction_type = 'Added'
        else: 
            direction = 'lost'
            transaction_type = 'Deducted'
        
        records_channel = self.bot.get_channel(RECORDS_CHANNEL_ID)

        # if a member is selected, then update the points of that member
        if isinstance(target, discord.Member):
            prev_bal = get_bal_pts(target.id)
            update_pts(target.id, points)
            new_bal = get_bal_pts(target.id)

            embed = discord.Embed(title=f'$JNW {transaction_type}!', description=f'{target.mention} {direction} `{points}` $JNW.')

            avatar = target.avatar.url
            embed.set_thumbnail(url=avatar)
            embed.add_field(name='Previous Balance', value=f'{prev_bal} $JNW', inline=False)
            embed.add_field(name='Current Balance', value=f'{new_bal} $JNW', inline=False)
            
            admin = interaction.user
            embed.set_footer(text=f'{admin.name}#{admin.discriminator}', icon_url=admin.avatar.url)
            
            # make a record whenever there is any $JNW points update
            await records_channel.send(embed=embed)
            await interaction.response.send_message(embed=embed)
        
        # if a role is selected, then update the points of all members having that role 
        elif isinstance(target, discord.Role):
            await interaction.response.defer(thinking=True)

            members = target.members
            total_affected = len(members)
            member_id = [member.id for member in members]
            member_mentions = [f'<@{id}>' for id in member_id]
            member_list = '\n'.join(member_mentions)
            
            try: 
                update_pts(member_id, points)
            except Exception as e:
                error_embed = discord.Embed(
                title='Error',
                description=f'An error occurred while updating $JNW points: {e}'
            )
                await interaction.followup.send(embed=error_embed)
                return
            
            embed = discord.Embed(
                title=f'$JNW {transaction_type}!', 
                description=f'`{total_affected}` members of role `{target.name}` {direction} `{points}` $JNW.'
            )
            
            if len(member_list) < 1000:
                embed.add_field(name='Member List', value=member_list)
            else: 
                # TODO: implement pagination
                pass
            
            admin = interaction.user
            embed.set_footer(text=f'{admin.name}#{admin.discriminator}', icon_url=admin.avatar.url)
            
            # make a record whenever there is any $JNW points update
            await records_channel.send(embed=embed)
            await interaction.followup.send(embed=embed)
        
        else:
            await interaction.response.send_message('An unknown error occured.')
        
async def setup(bot: commands.Bot):
    await bot.add_cog(JNWPoints(bot))
        