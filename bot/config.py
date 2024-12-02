import os
from dotenv import load_dotenv

class Config:
    """Configuration for the bot.

    Reads the configuration from the environment variables.

    Attributes:
        token: The Discord app's token.
        dev_guild_id: The ID of the Discord server (aka guild) used for development.
        dev_mode: Whether the bot is running in development mode.
    """
    def __init__(self):
        load_dotenv()

        self.token = os.getenv('DISCORD_TOKEN')
        if not self.token:
            raise ValueError('DISCORD_TOKEN is not set in the environment variables.')

        self.dev_guild_id = os.getenv('DEV_GUILD_ID')
        self.dev_mode = bool(self.dev_guild_id)

config = Config()
