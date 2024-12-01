"""The Outgunned bot controller layer.

This module contains classes for handling commands for the Outgunned bot,
including generating the view for the roll command with buttons for rerolling,
free rerolling, and going all in.
"""
import discord
from bot.message import MessageGenerator, MessageParser
from bot.roll import Roller

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
        await interaction.response.send_message(MessageGenerator().generate_roll_message(roller.roll_history), view=view)    


class CoinController:
    """Handles the coin commands for the Outgunned bot."""
    async def handle_coin(self, interaction: discord.Interaction):
        """Handles the /coin Discord command.

        Responds with a message containing the result of the coin flip.
        """
        await interaction.response.send_message(MessageGenerator().generate_coin_message())


class D6Controller:
    """Handles the d6 command for the Outgunned bot."""
    async def handle_d6(self, interaction: discord.Interaction):
        """Handles the /d6 Discord command.

        Responds with a message containing the result of the d6 roll.
        """
        await interaction.response.send_message(MessageGenerator().generate_d6_message())


class HelpController:
    """Handles help commands for the Outgunned bot."""
    async def handle_help(self, interaction: discord.Interaction):
        """Handles the /help Discord command.

        Responds with a help message.
        """
        await interaction.response.send_message(MessageGenerator().generate_help_message())


class RollView(discord.ui.View):
    """A view for the roll command.

    Contains buttons for rerolling, free rerolling, and going all in.
    """
    def __init__(self, can_reroll: bool, can_free_reroll: bool, can_go_all_in: bool):
        super().__init__()
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
            roll_history = MessageParser(interaction).roll_history
            if not roll_history.can_reroll():
                raise RuntimeError('Cannot perform reroll')
            Roller(roll_history=roll_history).reroll()

            await self.view._update_message(interaction, roll_history)

    class FreeRerollButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label='Free Re-roll', style=discord.ButtonStyle.blurple)

        async def callback(self, interaction: discord.Interaction):
            print('Free rerolling...')
            roll_history = MessageParser(interaction).roll_history
            if not roll_history.can_free_reroll():
                raise RuntimeError('Cannot perform free reroll')
            Roller(roll_history=roll_history).free_reroll()

            await self.view._update_message(interaction, roll_history)

    class AllInButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label='All In', style=discord.ButtonStyle.red)

        async def callback(self, interaction: discord.Interaction):
            print('All in...')
            roll_history = MessageParser(interaction).roll_history
            if not roll_history.can_go_all_in():
                raise RuntimeError('Cannot go all in')
            Roller(roll_history=roll_history).all_in()

            await self.view._update_message(interaction, roll_history)

    async def _update_message(self, interaction, roll_history):
        updated_view = RollView(
            can_reroll=roll_history.can_reroll(),
            can_free_reroll=roll_history.can_free_reroll(),
            can_go_all_in=roll_history.can_go_all_in())

        message = MessageGenerator().generate_roll_message(roll_history)
        await interaction.response.edit_message(content=message, view=updated_view)
