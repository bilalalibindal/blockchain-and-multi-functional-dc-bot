import os
import sys

import aiohttp
import discord
import psycopg2
from discord.ext import commands


class MyBot(commands.Bot):
    def __init__(self):
        self.session = None
        self.discord_server = 1121084336133902346  # Discord server's id
        self.block = 44471527  # Verify smart contract's block number
        self.verify_contract_address = '0x42458f6F1955e88DDcb5104cEedA6d12599A71a6'  # Verify smart contract's address
        self.database_active = True  # Checks is database activated
        # connect to database
        self.conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        # self.application_id = 1004415803703177247
        super().__init__(command_prefix=".",
                         intents=discord.Intents.all(),
                         application_id=1123625330863779931)
        # Channels
        self.verified_log_channel = 1124610079975542876
        self.joinLeftChannel = 1121084336557539332
        self.menu_channel = 0
        self.whitelist_channel = 1121084336930828330

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        await bot.tree.sync(guild=discord.Object(id=self.discord_server))

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')


bot = MyBot()
bot.run(os.environ["DISCORD_TOKEN"])
