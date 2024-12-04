"""Handles different dice sets"""
from enum import Enum
from bot.config import config

class DiceSet(Enum):
    NUMBERS = 'numbers'
    OUTGUNNED = 'outgunned'
    OUTGUNNED_ADVENTURE = 'outgunned_adventure'
    HOUSEHOLD = 'household'


class EmojiDiceConverter:
    """Converts dice rolls to and from emoji.
    
    Uses the specified dice set, defaulting to the outgunned dice set.
    """
    DICE_EMOJI_MAP_NUMBERS = {
        1: ':one:',
        2: ':two:',
        3: ':three:',
        4: ':four:',
        5: ':five:',
        6: ':six:'
    }

    DICE_EMOJI_MAP_SPECIAL = {
        DiceSet.OUTGUNNED: {
            'dev' : {
                1: '<:1outgunned:1313725926554734632>',
                2: '<:2outgunned:1313725949682122774>',
                3: '<:3outgunned:1313725961702866954>',
                4: '<:4outgunned:1313725971873927189>',
                5: '<:5outgunned:1313725981810360411>',
                6: '<:6outgunned:1313725991092486174>'
            },
            'prod' : {
                1: '<:1outgunned:1312661394075816026>',
                2: '<:2outgunned:1312661420399136809>',
                3: '<:3outgunned:1312661431807901746>',
                4: '<:4outgunned:1312661446806605824>',
                5: '<:5outgunned:1312661455371505715>',
                6: '<:6outgunned:1312661464963743754>'
            }
        },
        DiceSet.OUTGUNNED_ADVENTURE: {
            'dev' : {
                1: '<:1oga:1313726032905506848>',
                2: '<:2oga:1313726118725156884>',
                3: '<:3oga:1313726130842501130>',
                4: '<:4oga:1313726143970676846>',
                5: '<:5oga:1313726153252536332>',
                6: '<:6oga:1313726163499089950>'
            },
            'prod' : {
                # TODO
                1: '<:1outgunned:1312661394075816026>',
                2: '<:2outgunned:1312661420399136809>',
                3: '<:3outgunned:1312661431807901746>',
                4: '<:4outgunned:1312661446806605824>',
                5: '<:5outgunned:1312661455371505715>',
                6: '<:6outgunned:1312661464963743754>'
            }
        },
        DiceSet.HOUSEHOLD: {
            'dev' : {
                1: '<:1household:1313726193194766348>',
                2: '<:2household:1313726205358374953>',
                3: '<:3household:1313726215739277343>',
                4: '<:4household:1313726225549889608>',
                5: '<:5household:1313726235247116328>',
                6: '<:6household:1313726246429134929>'
            },
            'prod' : {
                1: '<:1outgunned:1312661394075816026>',
                2: '<:2outgunned:1312661420399136809>',
                3: '<:3outgunned:1312661431807901746>',
                4: '<:4outgunned:1312661446806605824>',
                5: '<:5outgunned:1312661455371505715>',
                6: '<:6outgunned:1312661464963743754>'
            }
        }
    }

    def __init__(self, dice_set=DiceSet.OUTGUNNED):
        if dice_set == DiceSet.NUMBERS:
            self.dice_emoji_map = self.DICE_EMOJI_MAP_NUMBERS
        else:
            # Since custom emoji are app specific, we need to use different emoji
            # ids for the development and production environments.
            env = 'dev' if config.dev_mode else 'prod'
            self.dice_emoji_map = self.DICE_EMOJI_MAP_SPECIAL[dice_set][env]
        
        self.emoji_dice_map = {v: k for k, v in self.dice_emoji_map.items()}

    def dice_to_emoji(self, dice):
        return self.dice_emoji_map.get(dice)

    def emoji_to_dice(self, emoji):
        return self.emoji_dice_map.get(emoji)
