from datetime import timedelta
from discord.ext import commands
from discord import app_commands
import discord
from data.currency import get_bananas, remove_bananas
from utils.emoji_helper import BANANA_COIN_EMOJI

async def define_assassinate_command(tree, servers):
    @tree.command(name="assassinate", description="Timeout a specific user for 180 seconds", guilds=servers)
    async def assassinate(interaction: discord.Interaction, member: discord.Member):
        user_id = str(interaction.user.id)
        current_bananas = await get_bananas(user_id)
        timeout_cost = 10000
        timeout_time = 180
        if current_bananas < timeout_cost:
            await interaction.response.send_message(f"You don't have enough {BANANA_COIN_EMOJI}!")
            return

        if member.bot or discord.utils.get(member.roles, name="A") is not None:
            await interaction.response.send_message("You cannot assassinate this user.")
            return

        duration = discord.utils.utcnow() + timedelta(seconds=timeout_time)
        try:
            await member.edit(timed_out_until=duration)
            await remove_bananas(user_id, timeout_cost)
            await interaction.response.send_message(f"{member.display_name} has been timed out for {timeout_time} seconds!")
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to timeout this user.")
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}")