from twitchio.ext import commands


class Module:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def purgeme(self, ctx):
        '''Purge the user who called the command'''
        await ctx.timeout(ctx.author.name, 1, 'F')


def prepare(bot):
    bot.add_cog(Module(bot))
