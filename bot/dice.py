"""Handles different dice sets"""
from enum import Enum
from bot.config import config

class DiceSet(Enum):
    OUTGUNNED = 'outgunned'
    OUTGUNNED_ADVENTURE = 'outgunned_adventure'
    HOUSEHOLD = 'household'
    NUMBERS = 'numbers'
    COLOR_SYMBOLS = 'color_symbols'
    COLOR_SQUARES = 'color_squares'


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

    DICE_EMOJI_MAP_COLOR_SYMBOLS = {
        1: ':red_circle:',
        2: ':green_square:',
        3: ':large_blue_diamond:',
        4: ':purple_heart:',
        5: ':star:',
        6: ':white_square_button:'
    }

    DICE_EMOJI_MAP_COLOR_SQUARES = {
        1: ':red_square:',
        2: ':green_square:',
        3: ':blue_square:',
        4: ':purple_square:',
        5: ':yellow_square:',
        6: ':brown_square:'
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
                1: '<:1oga:1314069121276575805>',
                2: '<:2oga:1314069144576069742>',
                3: '<:3oga:1314069153937887313>',
                4: '<:4oga:1314069165103120455>',
                5: '<:5oga:1314069175450210314>',
                6: '<:6oga:1314069184216305675>'
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
                1: '<:1household:1314069222648713256>',
                2: '<:2household:1314069238432137257>',
                3: '<:3household:1314069248074846208>',
                4: '<:4household:1314069281365033060>',
                5: '<:5household:1314069295688585339>',
                6: '<:6household:1314069305767366778>'
            }
        }
    }

    def __init__(self, dice_set=DiceSet.OUTGUNNED):
        if dice_set == DiceSet.NUMBERS:
            self.dice_emoji_map = self.DICE_EMOJI_MAP_NUMBERS
        elif dice_set == DiceSet.COLOR_SYMBOLS:
            self.dice_emoji_map = self.DICE_EMOJI_MAP_COLOR_SYMBOLS
        elif dice_set == DiceSet.COLOR_SQUARES:
            self.dice_emoji_map = self.DICE_EMOJI_MAP_COLOR_SQUARES
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
