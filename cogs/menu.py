import os
import random
import string
import sys

import discord
from discord import app_commands
from discord import ui
from discord.ext import commands

cogs_path = os.path.join(os.getcwd(), 'cogs')
sys.path.append(cogs_path)
from database import DataBase


# The View class is used to represent the components of a message.
# We create a RegisterButton subclass for our custom view that includes a register button.


class RegisterButton(discord.ui.View):
    def __init__(self, bot) -> None:
        # The View will stop listening to interactions after a certain amount of time
        # Since timeout is set to None, the View will keep listening for interactions indefinitely
        super().__init__(timeout=None)
        self.bot = bot  # Define bot instance to use anywhere
        self.dataBase = DataBase(self.bot)  # Define Database() class to reach functions defined that class

    # We define a button with the 'button' decorator.
    # This decorator allows us to create a button and the function that will be executed when it's clicked.
    # This button will be used for registration to the game.
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, emoji="✅", custom_id="join")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user  # get user id with button
        address = await self.dataBase.get_data(user_id=user.id, data_name='Address')  # bring user's address
        # check that is user registered or not
        if await self.dataBase.is_registered(user_id=user.id):
            # is user not verified an address
            if address is None:
                # bring user's code to put it to the link
                code = await self.dataBase.get_data(user_id=user.id, data_name="Code")
                # Create an embed with the URL and send it to the user with embed
                url = f'https://petrolworld.io/verify.html?discordID={user.id}&code={code}'

                embed = discord.Embed(
                    title="🔒 Wallet Verification",
                    description=f"Hello, {user.mention}!\n\n"
                                f"🔹 To verify your wallet address, click [here]({url})."
                                f" This process requires a fee of **0.5 MATIC**.\n\n"
                                f"⚠️ Your unique verification code is **`{code}`**."
                                f" Please ensure that it's present on the page"
                                f" when you're redirected. Do not share this code with anyone.\n\n"
                                f"💼 You'll need a MetaMask wallet to proceed. Click the 'Verify' button,"
                                f" add the Polygon Mainnet to your networks, and confirm the transaction.\n\n"
                                f"✅ Your wallet address will be saved to our database"
                                f" after the transaction is confirmed."
                                f" Once done, you can press the verify button"
                                f" again to obtain the 'Verified' role in our server."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            # if user verified an address
            else:
                guild = interaction.guild
                member = guild.get_member(user.id)
                verified_role = discord.utils.get(guild.roles, name="✅Verified")
                # Create an embed
                embed = discord.Embed(
                    title="🟢 Wallet Address Verified",
                    description=f"{user.mention}\n\n"
                                f"`Your wallet address:` **{address}**\n\n"
                                f"🔄 To change or delete your wallet address,"
                                f" use the '/reset_address' command.\n"
                                f"Note: This will erase your address and unique code from our database. "
                                f"And require you to verify your wallet again.\n\n"
                                f"⚠️ 'Verified' role will be lost upon resetting. "
                                f"Your 'Whitelist' role and other benefits remain intact."
                                f"But you may lose the benefits of being whitelisted"
                                f" until a new wallet address is added."
                )

                await interaction.response.send_message(embed=embed, ephemeral=True)
                if verified_role not in member.roles:  # Check if the user has the role
                    await member.add_roles(verified_role)  # If not, give the role

                    # check that is user verified a wallet first time?
                    if await self.dataBase.get_data(user_id=member.id, data_name="Verified") != "1":
                        # Change user's verified value as 1
                        await self.dataBase.update_data(user_id=member.id, data_name="Verified", new_value=1)
                        # After member verified his wallet, increase point of inviter
                        inviter = await self.dataBase.get_data(user_id=user.id, data_name="Inviter")  # get inviter id
                        # increase user's point who invited that new verified member
                        if inviter is not None:
                            point = int(await self.dataBase.get_data(user_id=inviter, data_name="Point"))
                            point += 3
                            # Update point value in database
                            await self.dataBase.update_data(user_id=inviter, data_name="Point", new_value=point)

        # user is not registered or verified yet
        else:
            # if user is not registered yet...
            await self.dataBase.register_to_database(user_id=user.id)  # user registered successfully
            # bring user's code to put it to the link
            code = await self.dataBase.get_data(user_id=user.id, data_name="Code")
            # Create an embed with the URL and send it to the user with embed
            url = f'https://petrolworld.io/verify.html?discordID={user.id}&code={code}'
            embed = discord.Embed(
                title="🔒 Wallet Verification",
                description=f"Hello, {user.mention}!\n\n"
                            f"🔹 To verify your wallet address, click [here]({url})."
                            f" This process requires a fee of **0.5 MATIC**.\n\n"
                            f"⚠️ Your unique verification code is **`{code}`**."
                            f" Please ensure that it's present on the page"
                            f" when you're redirected. Do not share this code with anyone.\n\n"
                            f"💼 You'll need a MetaMask wallet to proceed. Click the 'Verify' button,"
                            f" add the Polygon Mainnet to your networks, and confirm the transaction.\n\n"
                            f"✅ Your wallet address will be saved to our database"
                            f" after the transaction is confirmed."
                            f" Once done, you can press the verify button"
                            f" again to obtain the 'Verified' role in our server."
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            # ephemeral messages can only view by user


class ResetModal(ui.Modal, title="RESET WALLET ADDRESS"):
    def __init__(self, bot, user) -> None:
        # The View will stop listening to interactions after a certain amount of time
        # Since timeout is set to None, the View will keep listening for interactions indefinitely
        super().__init__(timeout=None)
        self.bot = bot  # Define bot instance to use anywhere
        self.dataBase = DataBase(self.bot)  # Define Database() class to reach functions defined that class
        self.user = user

    reset = ui.TextInput(label="Type 'RESET MY WALLET ADDRESS'",
                         placeholder="RESET MY WALLET ADDRESS")

    async def on_submit(self, interaction: discord.Interaction):
        if str(self.reset.value) == "RESET MY WALLET ADDRESS":
            guild = interaction.guild
            member = guild.get_member(self.user.id)
            role = discord.utils.get(guild.roles, name="✅Verified")

            code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))  # Generate a random code
            await self.dataBase.update_data(user_id=self.user.id, data_name='Code', new_value=code)
            await self.dataBase.update_data(user_id=self.user.id, data_name='Address', new_value=None)
            await interaction.response.send_message(f'{self.user.mention} Your address has been reset', ephemeral=True)

            if role in member.roles:  # Check if the user has the role
                await member.remove_roles(role)  # If not, add the role
        else:
            await interaction.response.send_message(f'{self.user.mention} Please type correct text', ephemeral=True)


class Menu(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.registerButton = RegisterButton(self.bot)
        self.dataBase = DataBase(self.bot)

    # The menu command. This is a slash command that administrators can use to create the registration menu.

    @app_commands.command(name="verify_menu",
                          description="Create a verify menu")
    @app_commands.default_permissions(administrator=True)
    async def verify_menu(self, interaction: discord.Interaction) -> None:
        self.bot.menu_channel = interaction.channel_id  # define channel
        # Create an embed message for the registration menu.
        embed = discord.Embed(
            title="🟢 Petrol World Registration",
            description="**Welcome to Petrol World!** ⛽\n\n"
                        "🔑 To get **'Verified'** role, you need to confirm your wallet address.\n\n"
                        "➥ Click the '✅**Verify**' button below and follow the instructions.\n\n"
        )

        # Send the registration menu as a response to the slash command.
        await self.dataBase.create_database()
        await interaction.channel.send(embed=embed, view=self.registerButton)
        await interaction.response.defer()

    @app_commands.command(name="reset_address",
                          description="reset your address")
    async def reset_address(self, interaction: discord.Interaction) -> None:
        user = interaction.user
        await interaction.response.send_modal(ResetModal(bot=self.bot, user=user))

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.application_id == 1123625330863779931:
            await self.verify(interaction)

    async def verify(self, interaction: discord.Interaction):
        user = interaction.user  # get user id with button
        address = await self.dataBase.get_data(user_id=user.id, data_name='Address')  # bring user's address
        # check that is user registered or not
        if await self.dataBase.is_registered(user_id=user.id):
            # is user not verified an address
            if address is None:
                # bring user's code to put it to the link
                code = await self.dataBase.get_data(user_id=user.id, data_name="Code")
                # Create an embed with the URL and send it to the user with embed
                url = f'https://petrolworld.io/verify.html?discordID={user.id}&code={code}'

                embed = discord.Embed(
                    title="🔒 Wallet Verification",
                    description=f"Hello, {user.mention}!\n\n"
                                f"🔹 To verify your wallet address, click [here]({url})."
                                f" This process requires a fee of **0.5 MATIC**.\n\n"
                                f"⚠️ Your unique verification code is **`{code}`**."
                                f" Please ensure that it's present on the page"
                                f" when you're redirected. Do not share this code with anyone.\n\n"
                                f"💼 You'll need a MetaMask wallet to proceed. Click the 'Verify' button,"
                                f" add the Polygon Mainnet to your networks, and confirm the transaction.\n\n"
                                f"✅ Your wallet address will be saved to our database"
                                f" after the transaction is confirmed."
                                f" Once done, you can press the verify button"
                                f" again to obtain the 'Verified' role in our server."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            # if user verified an address
            else:
                guild = interaction.guild
                member = guild.get_member(user.id)
                verified_role = discord.utils.get(guild.roles, name="✅Verified")
                # Create an embed
                embed = discord.Embed(
                    title="🟢 Wallet Address Verified",
                    description=f"{user.mention}\n\n"
                                f"`Your wallet address:` **{address}**\n\n"
                                f"🔄 To change or delete your wallet address,"
                                f" use the '/reset_address' command.\n"
                                f"Note: This will erase your address and unique code from our database. "
                                f"And require you to verify your wallet again.\n\n"
                                f"⚠️ 'Verified' role will be lost upon resetting. "
                                f"Your 'Whitelist' role and other benefits remain intact."
                                f"But you may lose the benefits of being whitelisted"
                                f" until a new wallet address is added."
                )

                await interaction.response.send_message(embed=embed, ephemeral=True)
                if verified_role not in member.roles:  # Check if the user has the role
                    await member.add_roles(verified_role)  # If not, give the role

                    # check that is user verified a wallet first time?
                    if await self.dataBase.get_data(user_id=member.id, data_name="Verified") != "1":
                        # Change user's verified value as 1
                        await self.dataBase.update_data(user_id=member.id, data_name="Verified", new_value=1)
                        # After member verified his wallet, increase point of inviter
                        inviter = await self.dataBase.get_data(user_id=user.id, data_name="Inviter")  # get inviter id
                        # increase user's point who invited that new verified member
                        if inviter is not None:
                            point = int(await self.dataBase.get_data(user_id=inviter, data_name="Point"))
                            point += 3
                            # Update point value in database
                            await self.dataBase.update_data(user_id=inviter, data_name="Point", new_value=point)

        # user is not registered or verified yet
        else:
            # if user is not registered yet...
            await self.dataBase.register_to_database(user_id=user.id)  # user registered successfully
            # bring user's code to put it to the link
            code = await self.dataBase.get_data(user_id=user.id, data_name="Code")
            # Create an embed with the URL and send it to the user with embed
            url = f'https://petrolworld.io/verify.html?discordID={user.id}&code={code}'
            embed = discord.Embed(
                title="🔒 Wallet Verification",
                description=f"Hello, {user.mention}!\n\n"
                            f"🔹 To verify your wallet address, click [here]({url})."
                            f" This process requires a fee of **0.5 MATIC**.\n\n"
                            f"⚠️ Your unique verification code is **`{code}`**."
                            f" Please ensure that it's present on the page"
                            f" when you're redirected. Do not share this code with anyone.\n\n"
                            f"💼 You'll need a MetaMask wallet to proceed. Click the 'Verify' button,"
                            f" add the Polygon Mainnet to your networks, and confirm the transaction.\n\n"
                            f"✅ Your wallet address will be saved to our database"
                            f" after the transaction is confirmed."
                            f" Once done, you can press the verify button"
                            f" again to obtain the 'Verified' role in our server."
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

            # ephemeral messages can only view by user


# This function is used to set up the cog. A cog is a collection of commands that can be added to the bot.
async def setup(bot: commands.Bot) -> None:
    # Add the cog to the bot. The cog contains the commands and the associated functions.
    await bot.add_cog(Menu(bot), guilds=[discord.Object(id=1121084336133902346)])
