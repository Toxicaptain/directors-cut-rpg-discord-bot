"""A Discord bot that rolls Outgunned dice.

The code below is adapted from:
https://github.com/Rapptz/discord.py/blob/master/examples/app_commands/basic.py
"""
import discord
from discord import app_commands

from bot.config import config
from bot.controller import (
    SettingsController,
    RollController,
    CoinController,
    D6Controller,
    HelpController,
    DynamicRerollButton,
    DynamicFreeRerollButton,
    DynamicAllInButton,)
from bot.dice import DiceSet


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.dev_guild = None
        if config.dev_guild_id:
            self.dev_guild = discord.Object(config.dev_guild_id)
        print(f'Development guild: {self.dev_guild}')

    async def setup_hook(self):
        """Setup the global commands on the guild.
        
        If a development guild is specified, the global commands are copied to that guild.
        This ensures that they are available right away, without the delay of up to an hour.
        """
        # Register dynamic buttons, so they still work after the bot restarts.
        self.add_dynamic_items(DynamicRerollButton, DynamicFreeRerollButton, DynamicAllInButton)
        if self.dev_guild:
            self.tree.copy_global_to(guild=self.dev_guild)
        await self.tree.sync(guild=self.dev_guild)

def generate_dice_set_choices():
    """Dynamically generate the dice set choices for the /settings command."""
    return [
        app_commands.Choice(name=dice_set.name.replace('_', ' ').title(), value=dice_set.value)
        for dice_set in DiceSet
    ]

def main():
    client = MyClient(intents=discord.Intents.default())

    @client.event
    async def on_ready():
        print(f'Logged in as {client.user} (ID: {client.user.id})')
        print('------')

    @client.tree.command()
    @app_commands.describe(
        dice_set='The dice set to use (Outgunned, Household, etc.)',
    )
    @app_commands.choices(
        dice_set=generate_dice_set_choices(),
    )
    async def settings(interaction: discord.Interaction, dice_set: str):
        """Set the channel settings, such as the dice set."""
        await SettingsController().handle_settings(interaction, dice_set)

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

    client.run(config.token)

if __name__ == '__main__':
    main()
