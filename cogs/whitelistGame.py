import os
import sys
from random import randint

import discord
from discord import app_commands
from discord.ext import commands

# Define path for the database module and add it to sys.path
cogs_path = os.path.join(os.getcwd(), 'cogs')
sys.path.append(cogs_path)
from database import DataBase  # Import database module


class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dataBase = DataBase(self.bot)  # Initialize a new database object

    # Define a command for trying user's luck for the whitelist role
    @commands.command(name="whitelist", description="Try your luck")
    async def whitelist(self, ctx) -> None:
        if ctx.channel.id == self.bot.whitelist_channel:
            self.bot.menu_channel = ctx.channel.id
            user = ctx.author  # Get the user who interacted
            guild = ctx.guild
            # Get the whitelist and verified roles
            verified_role = discord.utils.get(guild.roles, name="✅Verified")
            whitelist_role = discord.utils.get(guild.roles, name="Whitelist")
            channel = ctx.channel
            if verified_role not in user.roles:
                await ctx.reply(
                    content=f"{user.mention}, you must obtain the {verified_role.mention} role to run this command")
                return
            # Check if the user already has the role
            if whitelist_role in user.roles:
                await ctx.reply(
                    content=f"{user.mention}, you already have the {whitelist_role.name} role.")
            else:
                # Get the user's point and calculate chance
                point = int(await self.dataBase.get_data(user_id=user.id, data_name="Point"))
                chance = point + 1
                # Check user's luck and assign the role if lucky
                if randint(1, 100) <= chance:
                    await user.add_roles(whitelist_role)
                    await ctx.reply(
                        content=f"{user.mention}, congratulations! You've won the {whitelist_role.name} role!"
                                f"\n`Your current luck`: **%{chance}**")
                    await channel.set_permissions(user, send_messages=False)
                    await self.dataBase.update_data(user_id=user.id, data_name="Whitelist", new_value="1")
                else:
                    await ctx.reply(
                        content=f"{user.mention}, sorry, you didn't win the {whitelist_role.name} role."
                                f"\n`Your current luck`: **%{chance}**")

    # Define a slash command for clearing messages
    @app_commands.command(name="clear", description="Clear messages")
    @app_commands.default_permissions(administrator=True)  # only admin can run this command
    async def clear(self, interaction: discord.Interaction, amount: int) -> None:
        # Defer the response to avoid "bot did not respond" error
        await interaction.response.defer()
        # Purge the messages
        await interaction.channel.purge(limit=amount + 1)
        # Send a confirmation message
        await interaction.channel.send(content=f"Successfully deleted **{amount}** messages", delete_after=5)


async def setup(bot: commands.Bot) -> None:
    # Add SlashCommands as a cog to the bot
    await bot.add_cog(SlashCommands(bot), guilds=[discord.Object(id=1121084336133902346)])
