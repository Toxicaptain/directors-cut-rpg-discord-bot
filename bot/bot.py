"""A Discord bot that rolls Outgunned dice.

The code below is adapted from:
https://github.com/Rapptz/discord.py/blob/master/examples/app_commands/basic.py
"""
from typing import Optional
from dotenv import load_dotenv
import os

import discord
from discord import app_commands

from bot.controller import (
    RollController,
    CoinController,
    D6Controller,
    HelpController)


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents, dev_guild_id: Optional[int] = None):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.dev_guild = None
        if dev_guild_id:
            self.dev_guild = discord.Object(dev_guild_id)
        print(f'Development guild: {self.dev_guild}')

    async def setup_hook(self):
        """Setup the global comments on the guild.
        
        If a development guild is specified, the global commands are copied to that guild.
        This ensures that they are available right away, without the delay of up to an hour.
        """
        if self.dev_guild:
            self.tree.copy_global_to(guild=self.dev_guild)
        await self.tree.sync(guild=self.dev_guild)


def main():
    # Read environment variables
    load_dotenv()
    # The Discord app's token
    TOKEN = os.getenv('DISCORD_TOKEN')
    # Optional: The ID of the Discord server (aka guild) used for development.
    DEV_GUILD_ID = int(os.getenv('DEV_GUILD_ID')) if os.getenv('DEV_GUILD_ID') else None
    if not TOKEN:
        raise ValueError('DISCORD_TOKEN is not set in the environment variables.')

    intents = discord.Intents.default()
    client = MyClient(intents=intents, dev_guild_id=DEV_GUILD_ID)

    @client.event
    async def on_ready():
        print(f'Logged in as {client.user} (ID: {client.user.id})')
        print('------')

    @client.tree.command()
    async def help(interaction: discord.Interaction):
        """Outputs help text."""
        await HelpController().handle_help(interaction)

    @client.tree.command()
    @app_commands.describe(
        dice='The number of dice to roll',
    )
    async def roll(interaction: discord.Interaction, dice: int):
        """Roll a number of Outgunned dice."""
        await RollController().handle_roll(interaction, dice)

    @client.tree.command()
    async def coin(interaction: discord.Interaction):
        """Flip a coin."""
        await CoinController().handle_coin(interaction)

    @client.tree.command()
    async def d6(interaction: discord.Interaction):
        """Roll a d6."""
        await D6Controller().handle_d6(interaction)

    client.run(TOKEN)

if __name__ == '__main__':
    main()
