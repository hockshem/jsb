import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from typing import Optional
from jnw_fileops import get_bal_pts
from constants.roles import CORE_TEAM_ROLE_ID

class RedeemButton(Button):
    def __init__(self, max_redemption: int, required_points: int, parent_view: View, bot: commands.Bot):
        super().__init__(label='Redeem 💰', style=discord.ButtonStyle.success, custom_id='Redeem')
        self.max_redemption = max_redemption
        self.required_points = required_points
        self.parent_view = parent_view
        self.bot = bot
        self.player_list = []
        self.winners = []
    
    def end_redeem(self) -> None:
        button = discord.ui.Button(style=discord.ButtonStyle.gray, label='Event Ended', disabled=True)
        self.parent_view.remove_item(self)
        self.parent_view.add_item(button)
    
    async def callback(self, interaction: discord.Interaction) -> None:
        player = interaction.user
        player_balance = get_bal_pts(player.id)

        if player_balance < self.required_points:
            await interaction.response.send_message(f'{player.mention}, you don\'t have enough `$JNW`.', ephemeral=True)
            return

        if player in self.player_list:
            await interaction.response.send_message('You already redeemed a spot.', ephemeral=True)
            return

        self.player_list.append(player)
        self.winners.append(player)
        await interaction.response.send_message(f'{player.mention} successfully redeemed a spot! 🎉')

        if len(self.player_list) == self.max_redemption:
            self.end_redeem()
            await interaction.message.edit(view=self.parent_view)
            
            winners_str = '\n'.join([winner.mention for winner in self.winners])
            winners_embed = discord.Embed(title='Winners 🎉', description=f'The winners are: \n {winners_str}')
            
            channel = interaction.message.channel
            await channel.send(embed=winners_embed)


class Giveaway(commands.GroupCog, name='prize'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot 
        super().__init__()
    
    async def cog_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        err_msg = 'An unknown error occured.'
        if isinstance(error, app_commands.MissingRole):
            err_msg = f'Only <@&{error.missing_role}> can use that command.'
        await interaction.response.send_message(err_msg, ephemeral=True)

    @app_commands.command(name='redeem')
    @app_commands.describe(prize='Item to be redeemed', max_redemption='Max number of people who can redeem the prize', required_points='$JNW required to redeem the prize')
    @app_commands.checks.has_role(CORE_TEAM_ROLE_ID)
    async def redeem(
        self,
        interaction: discord.Interaction,
        prize: str,
        max_redemption: int,
        required_points: Optional[int] = 0
    ) -> None:
        """First come first served prize redemption event"""
        author = interaction.user
        redemption_embed = discord.Embed(title=f'{prize} x {max_redemption}', description='First come first served!\n Click the \'Redeem\' button below to reserve a spot!')
        redemption_embed.add_field(name='Required $JNW', value=required_points)

        component_view = View(timeout=None)
        component_view.add_item(RedeemButton(max_redemption, required_points, component_view, self.bot))

        redemption_embed.set_footer(text=author, icon_url=author.avatar.url)
        await interaction.response.send_message(embed=redemption_embed, view=component_view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Giveaway(bot))