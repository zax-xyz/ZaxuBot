from twitchio.ext import commands

from cfg import config


class Module:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def zcommands(self, ctx):
        """Get a list of commands registered in the bot"""
        commands = self.bot.commands
        coms = [f"{config.prefix}{c}" for c in commands]

        await ctx.send(", ".join(coms))

    @commands.command()
    async def zping(self, ctx):
        """Just a ping"""
        await ctx.send("pong")

    @commands.command()
    async def uptime(self, ctx):
        """Get how long the bot has been running"""
        await ctx.send(f"Bot has been running for {self.bot.uptime}")


def prepare(bot):
    bot.add_cog(Module(bot))
