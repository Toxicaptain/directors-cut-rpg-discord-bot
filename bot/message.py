"""The Octane bot message layer.

This module contains classes for generating and parsing messages for the
Octane bot. It also contains a class for converting dice rolls to and
from emoji.

The output will look something like this:

Roll:  :one: :one: :two: :four: :four: :six: :six: :six: :six:
Re-roll: :two: :four: :five: => :one: :six: :six:
All In: :one: :one: :one: :six: :six: :six: :six: :six:
----------
1 Extreme: :six: :six: :six: :six:
2 Basic: :one: :one: , :four: :four:
N/A: :two:


In case of lost successes due to to a failed reroll, we append a line like this:

LOST 1 Basic: :four: :four:
"""
import random
import re
import textwrap
import discord
from bot.dice import DiceSet, EmojiDiceConverter
from bot.roll import RollPhase, Roll, RollHistory

class RollPhaseMessageConverter:
    """Converts roll phases to and from strings."""
    PHASE_STRING_MAP = {
        RollPhase.INITIAL: 'Roll',
        RollPhase.REROLL: 'Re-roll',
        RollPhase.FREE_REROLL: 'Free Re-roll',
        RollPhase.ALL_IN: 'All In'
    }
    STRING_PHASE_MAP = {v: k for k, v in PHASE_STRING_MAP.items()}

    def phase_to_string(self, phase):
        return self.PHASE_STRING_MAP.get(phase)

    def string_to_phase(self, string):
        return self.STRING_PHASE_MAP.get(string)


class MessageGenerator:
    """Generates messages for the Octane bot."""
    # NB: We considered extracting each message type into its own class, but
    #     decided to keep them together for simplicity and because the roll
    #     message requires an OctaneRoller parameter, while the coin message
    #     doesn't.
    def __init__(self, dice_set=DiceSet.OCTANE):
        self.emoji_dice_converter = EmojiDiceConverter(dice_set=dice_set)

    def generate_roll_message(self, roll_history: RollHistory):
        """Generates a message containing the result of the roll."""
        message = ''
        # Append rolls
        for roll_phase in [RollPhase.INITIAL, RollPhase.REROLL, RollPhase.FREE_REROLL, RollPhase.ALL_IN]:
            message += self._generate_roll_line(roll_history, roll_phase)

        message += '\n----------'
 
        # Append matches (regular and lost)
        final_roll = roll_history.get_final_roll()
        message += self._generate_matches_text(final_roll.matches)
        message += self._generate_matches_text(final_roll.failed_matches, lost=True)
 
        return message
    
    def _generate_roll_line(self, roll_history: RollHistory, roll_phase: RollPhase):
        """Generates a single line of the roll message."""
        roll = roll_history.get_roll(roll_phase)
        if roll:
            roll_phase_name = RollPhaseMessageConverter().phase_to_string(roll_phase)
            # Show thumbs up/down for rerolls
            roll_emoji = ''
            if roll_phase in [RollPhase.REROLL, RollPhase.ALL_IN]:
                roll_emoji = ' :thumbsdown:' if roll.failed_reroll else ' :thumbsup:'
            elif roll_phase == RollPhase.FREE_REROLL:
                # Free rerolls don't show thumbs down as no success is lost. Still
                # show thumbs up if the reroll improved the result over the initial roll.
                if roll.is_better_than(roll_history.get_roll(RollPhase.INITIAL)):
                    roll_emoji = ' :thumbsup:'
            return f'\n{roll_phase_name}{roll_emoji}: ' + ' '.join(
                self.emoji_dice_converter.dice_to_emoji(die) for die in roll.dice)
        return ''

    def _generate_matches_text(self, matches, lost=False):
        """Appends the matches (regular or lost) to the message."""
        message = ''
        lost_text = 'LOST ' if lost else ''
        for num_matches, dice in sorted(matches.items(), reverse=True):
            message += (f'\n{lost_text}{len(dice)} {number_of_matches_to_success_name(num_matches)}: ' + 
                        ' , '.join(' '.join(
                            self.emoji_dice_converter.dice_to_emoji(die) for _ in range(num_matches)) for die in dice))
        return message

    def generate_coin_message(self):
        """Generates a message containing the result of the coin flip."""
        coin = random.randint(1, 2)
        return 'Coin flip: ' + ('HEADS (bad)' if coin == 1 else 'TAILS (good)')
    
    def generate_d6_message(self):
        """Generates a message containing the result of the d6 roll."""
        converter = EmojiDiceConverter(dice_set=DiceSet.NUMBERS)
        return 'D6: ' + converter.dice_to_emoji(random.randint(1, 6))
    
    def generate_help_message(self):
        """Generates a help message."""
        return textwrap.dedent(
            """
            **Help**

            This dice rolling bot supports the following commands:
                
                `/roll <num_dice>`: Roll the specified number of dice.
                `/coin`: Flip a coin.
                `/d6`: Roll a d6.
                `/settings <dice_set>`: Set the dice set (Octane, Homestead, etc.) for the current channel.

            The `/roll` command automatically sorts the rolled dice and groups them by the number of matches. It also shows any applicable reroll buttons (Reroll, Free Reroll, All In).

            For more info, see the Github page:
            https://github.com/digitalhobbit/directors-cut-rpg-discord-bot
            """
        )

    
class MessageParser:
    """Parses a previously sent message to extract the dice rolls.
    
    This allows us to reroll the dice based on the original message.

    Attributes:
        emoji_dice_converter: An EmojiDiceConverter instance.
        roll_history: The roll history.
    """
    def __init__(self, interaction: discord.Interaction, dice_set=DiceSet.OCTANE):
        self.emoji_dice_converter = EmojiDiceConverter(dice_set=dice_set)
        self.roll_history = None
        self._parse_roll_history(interaction.message)
    
    def _parse_roll_history(self, message: str):
        """Parses the dice rolls from a message."""
        self.roll_history = RollHistory()
        if not message.embeds:
            raise ValueError('Message does not contain an embed.')
        embed = message.embeds[0]
        lines = embed.description.split('\n')
        for line in lines:
            if line.startswith('---'):
                break
            for roll_phase in [RollPhase.INITIAL, RollPhase.REROLL, RollPhase.FREE_REROLL, RollPhase.ALL_IN]:
                self._parse_roll_line(line, roll_phase)

    def _parse_roll_line(self, line: str, roll_phase: RollPhase):
        """Parses a single line of the roll message."""
        prefix_pattern = re.compile(rf'{RollPhaseMessageConverter().phase_to_string(roll_phase)}( :thumbsup:| :thumbsdown:)?: ')
        match = prefix_pattern.match(line)
        if match:
            dice_string = line[match.end():]
            dice = [self.emoji_dice_converter.emoji_to_dice(die) for die in dice_string.split(' ') if die != '']
            self.roll_history.add_roll(roll_phase, Roll(dice))

def number_of_matches_to_success_name(num_matches):
    match num_matches:
        case 2:
            return 'Basic'
        case 3:
            return 'Critical'
        case 4:
            return 'Extreme'
        case 5:
            return 'Impossible'
        case 6:
            return 'Jackpot'
        case 7:
            return 'Jackpot'
        case 8:
            return 'Jackpot'
        case 9:
            return 'Jackpot'
        case _:
            return 'N/A'
