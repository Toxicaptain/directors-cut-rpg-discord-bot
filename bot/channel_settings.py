"""Encapsulates the user specified settings for a channel."""

import shelve

from bot.config import config
from bot.dice import DiceSet

class ChannelSettings:
    """Encapsulates the user specified settings for a channel."""
    def __init__(self):
        self.db = shelve.open(config.channel_settings_db)
    
    def __del__(self):
        self.db.close()

    def get_dice_set(self, channel_id: int) -> DiceSet:
        """Return the dice set for the channel.
        
        Args:
            channel_id: The ID of the channel.
        
        Returns:
            The dice set for the channel, defaulting to the Octane dice set.
        """
        return self.db.get(str(channel_id), DiceSet.OCTANE)
    
    def set_dice_set(self, channel_id: int, dice_set: DiceSet):
        """Set the dice set for the channel.
        
        Args:
            channel_id: The ID of the channel.
            dice_set: The dice set for the channel.
        """
        print(f'Setting dice set for channel {channel_id}:', dice_set)
        self.db[str(channel_id)] = dice_set


channel_settings = ChannelSettings()
