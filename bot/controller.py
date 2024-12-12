"""The Outgunned bot controller layer.

This module contains classes for handling commands for the Outgunned bot,
including generating the view for the roll command with buttons for rerolling,
free rerolling, and going all in.
"""
import discord
from bot.dice import DiceSet
from bot.message import MessageGenerator, MessageParser
from bot.roll import RollHistory, Roller
from bot.channel_settings import channel_settings

EMBED_COLOR = discord.Color.gold()

def dice_set_for_interaction(interaction: discord.Interaction) -> DiceSet:
    """Returns the dice set for the interaction's channel."""
    dice_set = channel_settings.get_dice_set(interaction.channel_id)
    print('Channel id:', interaction.channel_id)
    print('Dice set:', dice_set)
    return dice_set


class SettingsController:
    """Handles the settings command for the Outgunned bot."""
    async def handle_settings(self, interaction: discord.Interaction, dice_set_str: str):
        """Handles the /settings Discord command.

        Sets the dice set for the channel.
        May be used to set additional settings in the future.

        Args:
            interaction: The Discord interaction.
            dice_set_short: The short string representation of the dice set.
        """
        dice_set = DiceSet(dice_set_str)
        channel_settings.set_dice_set(interaction.channel_id, dice_set)
        embed = discord.Embed(description=f'Set the dice set to {dice_set.value}', color=EMBED_COLOR)
        await interaction.response.send_message(embed=embed)


class RollController:
    """Handles roll commands for the Outgunned bot."""
    async def handle_roll(self, interaction: discord.Interaction, num_dice: int):
        """Handles the /roll Discord command.

        Responds with a message containing the result of the roll, as
        well as a view containing buttons for rerolling, free rerolling,
        and going all in.
        """
        roller = Roller(num_dice=num_dice)
        roller.roll()
        view = RollView(
            can_reroll=roller.roll_history.can_reroll(),
            can_free_reroll=roller.roll_history.can_free_reroll(),
            can_go_all_in=roller.roll_history.can_go_all_in())
        content = MessageGenerator(
            dice_set_for_interaction(interaction)
        ).generate_roll_message(roller.roll_history)
        embed = discord.Embed(description=content, color=EMBED_COLOR)
        await interaction.response.send_message(embed=embed, view=view)    


class CoinController:
    """Handles the coin commands for the Outgunned bot."""
    async def handle_coin(self, interaction: discord.Interaction):
        """Handles the /coin Discord command.

        Responds with a message containing the result of the coin flip.
        """
        embed = discord.Embed(description=MessageGenerator().generate_coin_message(), color=EMBED_COLOR)
        await interaction.response.send_message(embed=embed)


class D6Controller:
    """Handles the d6 command for the Outgunned bot."""
    async def handle_d6(self, interaction: discord.Interaction):
        """Handles the /d6 Discord command.

        Responds with a message containing the result of the d6 roll.
        """
        embed = discord.Embed(description=MessageGenerator().generate_d6_message(), color=EMBED_COLOR)
        await interaction.response.send_message(embed=embed)


class HelpController:
    """Handles help commands for the Outgunned bot."""
    async def handle_help(self, interaction: discord.Interaction):
        """Handles the /help Discord command.

        Responds with a help message.
        """
        embed = discord.Embed(description=MessageGenerator().generate_help_message(), color=EMBED_COLOR)
        await interaction.response.send_message(embed=embed)


class RollView(discord.ui.View):
    """A view for the roll command.

    Contains buttons for rerolling, free rerolling, and going all in.
    """
    def __init__(self, can_reroll: bool, can_free_reroll: bool, can_go_all_in: bool):
        super().__init__(timeout=None)
        if can_reroll:
            self.add_item(self.RerollButton())
        if can_free_reroll:
            self.add_item(self.FreeRerollButton())
        if can_go_all_in:
            self.add_item(self.AllInButton())

    class RerollButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label='Re-roll', style=discord.ButtonStyle.green)

        async def callback(self, interaction: discord.Interaction):
            print('Rerolling...')
            dice_set = dice_set_for_interaction(interaction)
            roll_history = MessageParser(interaction, dice_set).roll_history
            if not roll_history.can_reroll():
                raise RuntimeError('Cannot perform reroll')
            Roller(roll_history=roll_history).reroll()

            await self.view._update_message(interaction, roll_history, dice_set)

    class FreeRerollButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label='Free Re-roll', style=discord.ButtonStyle.blurple)

        async def callback(self, interaction: discord.Interaction):
            print('Free rerolling...')
            dice_set = dice_set_for_interaction(interaction)
            roll_history = MessageParser(interaction, dice_set).roll_history
            if not roll_history.can_free_reroll():
                raise RuntimeError('Cannot perform free reroll')
            Roller(roll_history=roll_history).free_reroll()

            await self.view._update_message(interaction, roll_history, dice_set)

    class AllInButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label='All In', style=discord.ButtonStyle.red)

        async def callback(self, interaction: discord.Interaction):
            print('All in...')
            dice_set = dice_set_for_interaction(interaction)
            roll_history = MessageParser(interaction, dice_set).roll_history
            if not roll_history.can_go_all_in():
                raise RuntimeError('Cannot go all in')
            Roller(roll_history=roll_history).all_in()

            await self.view._update_message(interaction, roll_history, dice_set)

    async def _update_message(self, interaction: discord.Interaction, roll_history: RollHistory, dice_set: DiceSet):
        updated_view = RollView(
            can_reroll=roll_history.can_reroll(),
            can_free_reroll=roll_history.can_free_reroll(),
            can_go_all_in=roll_history.can_go_all_in())

        message = MessageGenerator(dice_set).generate_roll_message(roll_history)
        embed = discord.Embed(description=message, color=EMBED_COLOR)
        try:
            # await interaction.edit_original_response(embed=embed, view=updated_view)
            # await interaction.message.edit(embed=embed, view=updated_view)
            await interaction.response.edit_message(embed=embed, view=updated_view)
        except Exception as e:
            print(f"Failed to update message: {e}")
