from twitchio.ext import commands
from mpd import MPDClient

from cfg import config
from cfg import mpd_auth


class Module:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["currentsong"])
    async def current_song(self, ctx):
        try:
            client = MPDClient()
            client.connect("localhost", 6600)
            client.password(mpd_auth.password)

            song = client.currentsong()
        except:
            return await ctx.send("Error getting current song")
        finally:
            client.close()

        to_send = '"{}" by {}'.format(song["title"], song["artist"])
        if "album" in song:
            to_send += f" [{song['album']}]"

        await ctx.send(to_send)


def prepare(bot):
    bot.add_cog(Module(bot))
