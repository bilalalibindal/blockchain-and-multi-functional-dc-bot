import asyncio
import json
import os
import sys

from discord.ext import commands
from web3 import Web3
from web3.middleware import geth_poa_middleware

cogs_path = os.path.join(os.getcwd(), 'cogs')
sys.path.append(cogs_path)
from database import DataBase


class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dataBase = DataBase(self.bot)  # define database class from cog
        # infura api to check polygon events
        self.w3 = Web3(Web3.HTTPProvider(
            'https://polygon-mainnet.infura.io/v3/ad2265b3f61848e7b6754d338bd81aa5'))
        self.contract = self.setup_contract()  # setup contract when bot first starts

    # setup contract of verify
    def setup_contract(self):
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        with open('contractAbi.json') as file:
            contract_abi = json.load(file)
        return self.w3.eth.contract(address=self.bot.verify_contract_address, abi=contract_abi)

    async def listen_event(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            if self.bot.database_active:
                block_number = self.w3.eth.block_number  # define current block number
                event_filter = {
                    "fromBlock": self.bot.block,  # block number where our contract is deployed
                    "toBlock": block_number,  # current block number
                    "address": self.bot.verify_contract_address,  # contract address
                    # event name and parameters
                    "topics": [self.w3.keccak(text="UserRegistered(address,uint256,string)").hex()]
                }
                self.bot.block = block_number  # change fromBlock as current block number
                events = self.w3.eth.get_logs(event_filter)  # get all events between fromBlock to toBlock numbers
                for event in events:
                    event_data = self.contract.events.UserRegistered().process_log(event)
                    data = event_data['args']
                    await self.dataBase.save_address(data=data)  # send data from event to function from database cog
            await asyncio.sleep(15)

    # this event will work in loop to listen_event function
    @commands.Cog.listener()
    async def on_connect(self):
        await self.dataBase.create_database()
        await self.bot.loop.create_task(self.listen_event())


async def setup(bot):
    # Add cog to bot.
    await bot.add_cog(Verify(bot))
