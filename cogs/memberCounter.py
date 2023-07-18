import discord
from discord.ext import tasks, commands


class MemberCounter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Update stats task is started when the Cog is loaded
        self.update_stats.start()

    # This event runs when the Cog is unloaded
    def cog_unload(self):
        # Cancel the update stats task
        self.update_stats.cancel()

    # This is a task that runs in the background and starts after the bot is ready
    @tasks.loop(minutes=10.0)
    async def update_stats(self):
        # Make the bot wait until it is ready and has received all necessary data
        await self.bot.wait_until_ready()

        # self.bot.discord_server = server ID
        # Get the guild object
        guild = self.bot.get_guild(self.bot.discord_server)

        # Define the channel IDs
        member_count_channel = self.bot.get_channel(1121084336133902355)
        verified_count_channel = self.bot.get_channel(1122055733513551872)
        whitelisted_count_channel = self.bot.get_channel(1123626238012047440)

        # Count total members
        normal_members = len([member for member in guild.members if
                              discord.utils.get(member.roles, name="⛽member")])

        # Count members with the "Verified" role
        verified_members = len([member for member in guild.members if
                                discord.utils.get(member.roles, name="✅Verified")])
        # Count members with the "Whitelist" role
        whitelisted_members = len([member for member in guild.members if
                                   discord.utils.get(member.roles, name="Whitelist")])
        # Update the member count channel name
        await member_count_channel.edit(name=f"⭐｜Members:  {normal_members}")

        # Update the verified count channel name
        await verified_count_channel.edit(name=f"✅｜Verified:  {verified_members}")

        # Update the whitelist count channel name
        await whitelisted_count_channel.edit(name=f"✔ ｜Whitelist:   {whitelisted_members}")


# This function runs when the Cog is loaded
async def setup(bot):
    # Add the Cog to the bot
    await bot.add_cog(MemberCounter(bot))
