from discord.ext import commands
from discord import app_commands
import discord
from data.currency import add_bananas

async def define_admin_add_currency_command(tree, servers):
    def is_owner():
        async def predicate(interaction: discord.Interaction):
            return interaction.user.id == 212635381391294464
        return predicate

    @tree.command(name="addcurrency", description="Add currency to a user", guilds=servers)
    @app_commands.check(is_owner())
    async def add_currency(interaction: discord.Interaction, user: discord.User, amount: int):
        try:
            await add_bananas(str(user.id), amount)
            await interaction.response.send_message(f"Added {amount} bananas to {user.display_name}'s account.")
        except Exception as e:
            await interaction.response.send_message(f"Failed to add currency: {str(e)}")

    @add_currency.error
    async def add_currency_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You do not have permission for this command.", ephemeral=True)
        else:
            await interaction.response.send_message("An error occurred while processing your command.", ephemeral=True)
