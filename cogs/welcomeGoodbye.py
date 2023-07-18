import discord
from discord.ext import commands


class WelcomeGoodbye(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Welcome and goodbye messages will be sent to this channel
        self.channel_id = self.bot.joinLeftChannel

    # welcome message with two parameters pulling from inviteTracker.py
    async def welcome_message(self, user, inviter):
        channel = self.bot.get_channel(self.channel_id)
        # create embed, it will send welcome message by tagging user and who invited him
        embed = discord.Embed(title=f"🎉 Welcome, {user.name}!",
                              description=f"{user.mention} **has joined!**\n\n\u200b\n"
                                          f"`inviter`: {inviter.mention}",
                              colour=discord.Colour.green())
        embed.set_thumbnail(url=user.display_avatar.url)  # put users avatar on embed
        await channel.send(embed=embed)  # send the message

    # goodbye message with member parameter pulling from inviteTracker.py
    async def goodbye_message(self, user):
        channel = self.bot.get_channel(self.channel_id)  # define the channel
        # create embed, it will send goodbye message by tagging user
        embed = discord.Embed(title=f"👋 Goodbye, {user.name}!",
                              description=f"{user.mention} **has left!**",
                              colour=discord.Colour.red())
        embed.set_thumbnail(url=user.display_avatar.url)  # put users avatar on embed
        await channel.send(embed=embed)  # send the message


async def setup(bot):
    # Add cog to bot
    await bot.add_cog(WelcomeGoodbye(bot))
