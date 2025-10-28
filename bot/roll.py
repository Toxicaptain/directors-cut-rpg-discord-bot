"""This module handles the actual dice rolling logic."""
import random
from enum import Enum

# Enum that defines the different phases of a roll
class RollPhase(Enum):
    INITIAL = 1
    REROLL = 2
    FREE_REROLL = 3
    ALL_IN = 4


class Roll:
    """Encapsulates a single Octane dice roll.
    
    Attributes:
        dice: The sorted dice roll results.
        num_dice: The number of dice rolled.
        matches: A dictionary that maps the number of matches to the dice that
            matched that number of times.
        failed_reroll: A boolean indicating if the roll was a failed reroll.
        failed_matches: A dictionary structured the same as matches, but only
            containing the dice that were lost due to a failed reroll.
    """
    def __init__(self, dice: list = []):
        """Initializes the Roll object with the given parameters.

        Args:
            num_dice: The number of dice rolled.
            dice: The dice roll results.
        """
        self.dice = sorted(dice)
        self.num_dice = len(dice)
        self.matches = self._group_matches()
        self.failed_reroll = False
        self.failed_matches = {}

    def matched_dice(self):
        """Returns the dice that matched at least one other die."""
        # Determine matched dice by excluding non_matched dice (i.e. matches[1]) from the full dice list
        non_matches = self.matches.get(1, [])
        return [die for die in self.dice if die not in non_matches]
    
    def non_matched_dice(self):
        """Returns the dice that did not match any other die."""
        return self.matches.get(1, [])

    def mark_as_failed_reroll(self):
        """Marks the roll as a failed reroll.
        
        This means that the player attempted to reroll, but the result was not
        better than the original roll. In this case, we need to remove one of
        the successes from the original roll.
        """
        self.failed_reroll = True

        # Move the lowest success from matches to failed_matches
        lowest_match = min(key for key in self.matches.keys() if key > 1)
        lost_dice = self.matches[lowest_match].pop(0)
        self.failed_matches = {lowest_match: [lost_dice]}

        # Remove the key if there are no more dice with that number of matches
        if not self.matches[lowest_match]:
            del self.matches[lowest_match]

    def mark_as_failed_all_in(self):
        """Marks the roll as a failed attempt to go all in.
        
        This means that the player attempted to go all in, but the result was not
        better than the previous roll. In this case, we need to remove all of the
        successes from the original roll.
        """
        self.failed_reroll = True
        non_matched_dice = self.matches.pop(1, None)
        self.failed_matches = self.matches
        self.matches = {1: non_matched_dice}

    def is_better_than(self, other_roll: 'Roll'):
        """Compares this roll to another roll and returns true if it is better.
        
        A roll is considered better if it either has more successes than the other
        roll, or if it has higher magnitude successes. Note that 3 lower successes
        are equivalent to 1 higher success, and vice versa.
        """
        # Iterate over both sets of matches. For each basic success (matches[2]), count it as 1.
        # For each critical success (matches[3]), count it as 3. And so on (matches[4] = 9,
        # matches[5] = 27, etc.). Then compare the total scores.
        score = sum((3 ** (num_matches - 1)) * len(dice) for num_matches, dice in self.matches.items() if num_matches > 1)
        other_score = sum((3 ** (num_matches - 1)) * len(dice) for num_matches, dice in other_roll.matches.items() if num_matches > 1)
        return score > other_score

    def _group_matches(self):
        """Groups the dice by the number of matches.
        
        Octane is based on different numbers of matches, so we keep track of
        these using a dictionary. The keys are the number of matches
        (e.g. 1, 2, 3, 4, 5, 6), and the values are lists of the dice that
        matched that number of times. They key 1 represents dice that did not
        match any other dice.
        E.g. {1: [1, 2, 3], 2: [4, 5], 3: [6]} represents a roll that had 3 6s,
        2 4s and 5s, and single 1, 2, and 3.
        """
        counts = {}
        for die in self.dice:
            counts[die] = counts.get(die, 0) + 1
        
        matches = {}
        for die, count in counts.items():
            if count not in matches:
                matches[count] = []
            matches[count].append(die)
        return matches
    
    def __str__(self):
        return f'Roll(dice={self.dice}, num_dice={self.num_dice}, matches={self.matches})'


class RollHistory:
    """Encapsulates a complete Octane dice roll.
    
    This includes the original roll, rerolls, and the final results.

    Attributes:
        num_dice: The number of dice rolled.
        rolls: A dictionary that maps the phase of the roll to the Roll object.
    """
    def __init__(self):
        """Initializes the RollHistory object."""
        self.num_dice = None
        self.rolls = {}

    def add_roll(self, phase: RollPhase, roll: Roll):
        """Adds a roll to the history."""
        self.rolls[phase] = roll
        if not self.num_dice:
            self.num_dice = roll.num_dice
    
    def get_roll(self, phase: RollPhase):
        """Gets the roll for the given phase."""
        return self.rolls.get(phase)
    
    def get_final_roll(self):
        """Gets the final roll, which is the last roll in the history."""
        # NB: Need to get the value of the enum, as direct enum comparison does not work
        return self.rolls.get(RollPhase(max([k.value for k in self.rolls.keys()])))

    def can_reroll(self):
        """Returns true if the player is allowed to reroll.
        
        This is allowed if the player has not yet performed a reroll, free reroll, or
        gone all in, and if there is at least one basic success, and if there is at least
        one non-matched die.
        """
        if (all(phase not in self.rolls for phase in [RollPhase.REROLL, RollPhase.FREE_REROLL, RollPhase.ALL_IN]) and
                self.get_final_roll().non_matched_dice() and
                self._has_at_least_one_success()):
            return True
        return False

    def can_free_reroll(self):
        """Returns true if the player is allowed to do a free reroll.
        
        This is allowed if the player has not yet done a free reroll, regular reroll,
        or gone all in, if there is at least one non-matched die, and under the
        assumption that they have an appropriate Feat (which we can't check for).
        """
        if (all(phase not in self.rolls for phase in [RollPhase.REROLL, RollPhase.FREE_REROLL, RollPhase.ALL_IN]) and
                self.get_final_roll().non_matched_dice()):
            return True
        return False

    def can_go_all_in(self):
        """Returns true if the player is allowed to go all in.
        
        This is allowed if the player has not yet gone all in, but has previously
        done a reroll or free reroll and got a better result, and there is at least
        one non-matched die.
        """
        last_roll = self.get_final_roll()
        if ((RollPhase.ALL_IN not in self.rolls) and
            any(phase in self.rolls for phase in [RollPhase.REROLL, RollPhase.FREE_REROLL]) and
            (not last_roll.failed_reroll) and
            (last_roll.is_better_than(self.get_roll(RollPhase.INITIAL))) and
            last_roll.non_matched_dice()):
            return True
        return False

    def _has_at_least_one_success(self):
        """Returns true if the roll includes at least one basic success."""
        return any(num_matches > 1 for num_matches in self.get_final_roll().matches)
    
    def __str__(self):
        return f'RollHistory(num_dice={self.num_dice}, rolls={self.rolls})'


class Roller:
    """Rolls Octane dice and encapsulates an entire roll including rerolls.

    Attributes:
        num_dice: The number of dice to roll.
        roll_history: The roll history.
    """
    def __init__(self, num_dice: int = 0, roll_history: RollHistory = None):
        """Initializes the Octane roller.
        
        Only one of the following parameters should be provided.

        Args:
            num_dice: The number of dice to roll.
            roll_history: The roll history to continue from.
        """
        if roll_history:
            self.num_dice = roll_history.num_dice
            self.roll_history = roll_history
        elif num_dice > 0:
            self.num_dice = num_dice
            self.roll_history = RollHistory()
        else:
            raise ValueError('Either num_dice or roll_history must be provided.')

    def roll(self):
        """Roll a number of Octane dice."""
        roll = Roll(self.roll_dice(self.num_dice))
        self.roll_history.add_roll(RollPhase.INITIAL, roll)

    def reroll(self):
        initial_roll = self.roll_history.get_roll(RollPhase.INITIAL)
        if initial_roll:
            rerolled_dice = self.roll_dice(len(initial_roll.matches[1]))
            combined_roll = Roll(initial_roll.matched_dice() + rerolled_dice)

            # Check if the reroll is better than the initial roll.
            # If not, we need to remove one of the previous successes.
            if not combined_roll.is_better_than(initial_roll):
                combined_roll.mark_as_failed_reroll()

            self.roll_history.add_roll(RollPhase.REROLL, combined_roll)
        else:
            raise ValueError('No initial roll to reroll.')
    
    def free_reroll(self):
        initial_roll = self.roll_history.get_roll(RollPhase.INITIAL)
        if initial_roll:
            rerolled_dice = self.roll_dice(len(initial_roll.matches[1]))
            combined_roll = Roll(initial_roll.matched_dice() + rerolled_dice)
            self.roll_history.add_roll(RollPhase.FREE_REROLL, combined_roll)
            # NB: We don't mark free rerolls as failed, as no successes are lost.
        else:
            raise ValueError('No initial roll to reroll.')
    
    def all_in(self):
        last_roll = self.roll_history.get_final_roll()
        if last_roll:
            rerolled_dice = self.roll_dice(len(last_roll.matches[1]))
            combined_roll = Roll(last_roll.matched_dice() + rerolled_dice)

            # Check if the reroll is better than the initial roll.
            # If not, we need to remove ALL of the previous successes.
            if not combined_roll.is_better_than(last_roll):
                combined_roll.mark_as_failed_all_in()

            self.roll_history.add_roll(RollPhase.ALL_IN, combined_roll)
        else:
            raise ValueError('No initial roll to reroll.')

    def roll_dice(self, num_dice: int):
        """Rolls a number of dice and returns the sorted result."""
        return sorted([random.randint(1, 6) for _ in range(num_dice)])
