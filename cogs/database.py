import random
import string

from discord.ext import commands


class DataBase(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cur = self.bot.conn.cursor()  # Define cursor with self.bot.conn from main.py

    async def create_database(self):
        try:
            # Create table in database
            self.cur.execute("CREATE TABLE IF NOT EXISTS verify(Discord_ID TEXT, Code TEXT, Address TEXT, "
                             "Inviter TEXT, Point TEXT, Verified TEXT, Whitelist TEXT)")
            self.bot.conn.commit()  # save it to database
            self.bot.database_active = True
        except Exception as e:
            print(f"An error occurred while creating the database: {e}")

    async def register_to_database(self, user_id):
        try:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))  # Generate a random code
            # save user's discord id with special code in database table
            self.cur.execute("INSERT INTO verify(Discord_ID, Code, Point) VALUES (%s, %s, %s)", (user_id, code, 0))
            self.bot.conn.commit()  # save it to database table
        except Exception as e:
            print(f"An error occurred while registering to the database: {e}")

    async def remove_from_database(self, user_id):
        try:
            # Delete user from database
            self.cur.execute("DELETE FROM verify WHERE Discord_ID=%s", (str(user_id),))
            self.bot.conn.commit()  # save changes to database
        except Exception as e:
            print(f"An error occurred while removing from the database: {e}")

    async def is_registered(self, user_id):
        try:
            # Check that is user registered to database
            self.cur.execute("SELECT * FROM verify WHERE Discord_ID=%s", (str(user_id),))
            return self.cur.fetchone() is not None  # return true or false value
        except Exception as e:
            print(f"An error occurred while checking registration status: {e}")

    async def is_data_exist(self, data_name, value):
        try:
            self.cur.execute("SELECT * FROM verify WHERE {} = %s".format(data_name), (value,))
            data = self.cur.fetchone()

            if data is None:
                return False  # Value does not exist in database
            else:
                return True  # Value exists in database
        except Exception as e:
            print(f"An error occurred while checking if data exists: {e}")

    async def get_data(self, user_id, data_name):
        try:
            # Get data from table with user_id and data_name
            self.cur.execute(f"SELECT {data_name} FROM verify WHERE Discord_ID=%s", (str(user_id),))
            data = self.cur.fetchone()
            return data[0] if data else None
        except Exception as e:
            print(f"An error occurred while getting data: {e}")

    async def update_data(self, user_id, data_name, new_value):
        try:
            # Update user data
            if new_value is None:
                self.cur.execute(f"UPDATE verify SET {data_name}=%s WHERE Discord_ID=%s", (None, str(user_id)))
            else:
                self.cur.execute(f"UPDATE verify SET {data_name}=%s WHERE Discord_ID=%s", (new_value, str(user_id)))
            self.bot.conn.commit()  # save it to database table
        except Exception as e:
            print(f"An error occurred while updating data: {e}")

    # pull event with 'data' parameter
    async def save_address(self, data):
        try:
            user_address = str(data['userAddress'])  # define user address
            user_id = str(data['discordId'])  # define discord id
            user_code = str(data['secretCode'])  # define secret code
            # check that is data exist on database
            if await self.is_data_exist(data_name='Code', value=user_code):
                # check that is address already registered to database
                address = await self.get_data(user_id=user_id, data_name='Address')
                # define verified_log channel and user and user's inviter
                channel = self.bot.get_channel(self.bot.verified_log_channel)
                user = await self.bot.fetch_user(user_id)
                if address is None:  # if address value is empty
                    # add user's wallet address to database
                    self.cur.execute("UPDATE verify SET Address=%s WHERE Code=%s", (user_address, user_code))
                    self.bot.conn.commit()
                    if await self.get_data(user_id=user_id, data_name="Verified") != "1":

                        # Check if the user has an inviter in the database
                        inviter_id = await self.get_data(user_id=user_id, data_name="Inviter")
                        if inviter_id is not None:
                            inviter = await self.bot.fetch_user(inviter_id)
                        else:
                            inviter = None

                        # send information message
                        if inviter is not None:
                            await channel.send(
                                f"{user.mention} **Successfully verified wallet address!** | `Inviter:` "
                                f"{inviter.mention} **+ 3%** chance increased")
                        else:
                            await channel.send(
                                f"{user.mention} **Successfully verified wallet address!** | No inviter found.")
                    else:
                        await channel.send(f"{user.mention} **Successfully changed wallet address!**")
        except Exception as e:
            print(f"An error occurred while saving address: {e}")


async def setup(bot):
    try:
        # Add cog to bot.
        await bot.add_cog(DataBase(bot))
    except Exception as e:
        print(f"An error occurred while setting up the bot: {e}")
