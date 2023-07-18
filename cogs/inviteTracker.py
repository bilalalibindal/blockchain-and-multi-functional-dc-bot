import os
import sys

import DiscordUtils
from discord.ext import commands

cogs_path = os.path.join(os.getcwd(), 'cogs')
sys.path.append(cogs_path)
from database import DataBase
from welcomeGoodbye import WelcomeGoodbye


class InviteTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracker = DiscordUtils.InviteTracker(bot)
        self.dataBase = DataBase(self.bot)
        self.welcomeGoodbye = WelcomeGoodbye(self.bot)

    # This event will run when user join the server
    @commands.Cog.listener()
    async def on_member_join(self, member):
        inviter = await self.tracker.fetch_inviter(member)  # Define inviter who invited the member
        await self.welcomeGoodbye.welcome_message(user=member,
                                                  inviter=inviter)  # run welcome message from welcomeGoodbye cog
        if await self.dataBase.is_registered(user_id=member.id) is False:  # Check that is user joint server in the past
            await self.dataBase.register_to_database(user_id=member.id)  # save new member to database
            # Check that is user invited to our server in the past
            if await self.dataBase.get_data(user_id=member.id, data_name="Inviter") is None:
                # Add to database inviter of new member
                await self.dataBase.update_data(user_id=member.id, data_name="Inviter", new_value=inviter.id)

    # This event will run when user left the server
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.welcomeGoodbye.goodbye_message(user=member)  # run goodbye message from welcomeGoodbye cog
        address = await self.dataBase.get_data(user_id=member.id, data_name="Address")  # get user's address
        whitelist = await self.dataBase.get_data(user_id=member.id, data_name="Whitelist")  # get user's whitelist info
        # if user is not get whitelist and not save any wallet address we can delete him on database
        if address is None and whitelist is None:
            await self.dataBase.remove_from_database(user_id=member.id)  # Delete user with the function


async def setup(bot):
    # Add cog to bot
    await bot.add_cog(InviteTracker(bot))
