from datetime import datetime

from twitchio.ext import commands

from cfg import auth, config
from src.utils import colored, current_time, plural


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            prefix=config.prefix,
            irc_token=auth.irc_token,
            client_secret=auth.client_secret,
            client_id=auth.client_id,
            nick=auth.username,
            initial_channels=config.channels,
        )

        self.dbs = {}

        for module in config.modules:
            self.load_module(module)

    @property
    def uptime(self):
        time_now = datetime.now()
        time_delta = time_now - self.start_time
        d = datetime(1, 1, 1) + time_delta

        days = f"{d.day - 1} day{plural(d.day - 1)}"
        hours = f"{d.hour} hour{plural(d.hour)}"
        minutes = f"{d.minute} minute{plural(d.minute)}"
        seconds = f"{d.second} second{plural(d.second)}"

        return f"{days}, {hours}, {minutes}, {seconds}"

    async def event_ready(self):
        print("Bot ready")
        print("Username:", auth.username)
        print("Channels:", ", ".join(config.channels))

        self.start_time = datetime.now()

    async def event_message(self, message):
        username = message.author.name
        msg = message.content
        print(
            "{}  {}: {}".format(
                current_time(), colored(username, "blue", attrs=["bold"]), msg
            )
        )

        if username == self.nick:
            return

        await self.handle_commands(message)
