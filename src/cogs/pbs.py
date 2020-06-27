import asyncio

import aiosqlite
from twitchio.ext import commands

from src.utils import is_mod


class PBs:

    def __init__(self, bot):
        self.bot = bot

        bot.loop.run_until_complete(self.create_table())

    async def create_table(self):
        '''Create the pb SQL table if it doesn't already exist'''
        self.db = await aiosqlite.connect('pbs.db')
        self.bot.dbs['pbs'] = self.db

        async with self.db.cursor() as cursor:
            await cursor.execute('''CREATE TABLE IF NOT EXISTS times (
                game TEXT NOT NULL PRIMARY KEY COLLATE NOCASE,
                time TEXT NOT NULL
            )''')

            await self.db.commit()

    async def get_game(self, ctx):
        '''Gets the currently playing game from a live stream'''
        stream = await ctx.channel.get_stream()
        if stream is None:
            return None, None

        name = stream['user_name']
        return name, await self.get_game_name(stream['game_id'])

    async def get_game_name(self, game_id):
        '''Given a numeric game id, fetches the name of the game'''
        game = await self.bot.get_games(game_id)
        return game[0]['name']

    async def get_display_name(self, username):
        '''Gets a user's display name from their username'''
        user = await self.bot.get_users(username)
        return user[0].display_name

    @commands.command(name='pb', aliases=['getpb'])
    async def get_pb(self, ctx, *, game=None):
        '''
        Get the streamer's PB for a game.

        Uses the current stream game if none given
        '''
        if game is None:
            channel, game = await self.get_game(ctx)
            if game is None:
                # Channel not live
                return await ctx.send(
                    "Command doesn't work by itself when not live yet (try "
                    "specifying the game)"
                )
        else:
            channel = await self.get_display_name(ctx.channel.name)

        # Get PB from database
        async with self.db.cursor() as cursor:
            await cursor.execute('SELECT game, time FROM times WHERE game = ?',
                                 (game,))

            pb = await cursor.fetchone()
            if pb is None:
                return await ctx.send(f"No PB found for {game}")

        game, pb = pb

        await ctx.send(f"{channel}'s current {game} PB is {pb}")

    @commands.check(is_mod)
    @commands.command(name='setpb')
    async def set_pb(self, ctx, time, *, game=None):
        '''
        Sets the streamer's PB for a game

        Uses the current stream game if none given.
        '''
        game = game or (await self.get_game(ctx))[1]
        if game is None:
            # Channel not live
            return await ctx.send(
                "Command doesn't work by itself when not live yet (try "
                "specifying the game)"
            )

        # Add or replace PB in database
        async with self.db.cursor() as cursor:
            await cursor.execute(
                'REPLACE INTO times (game, time) VALUES (?, ?)',
                (game, time)
            )
            await self.db.commit()

            await cursor.execute('SELECT game FROM times WHERE game = ?',
                                 (game,))
            game = (await cursor.fetchone())[0]

        await ctx.send(f"Set PB for {game} to {time}")

    @commands.check(is_mod)
    @commands.command(name='delpb', aliases=['deletepb'])
    async def delete_pb(self, ctx, *, game=None):
        '''
        Deletes the streamer's PB for a game

        Uses the current stream game if none given.
        '''
        game = game or (await self.get_game(ctx))[1]
        if game is None:
            # Channel not live
            return await ctx.send(
                "Command doesn't work by itself when not live yet (try "
                "specifying the game)"
            )

        # Delete PB from database
        async with self.db.cursor() as cursor:
            await cursor.execute('SELECT game FROM times WHERE game = ?',
                                 (game,))

            row = await cursor.fetchone()
            if row is None:
                return await ctx.send(f"No PB found for {game}")

            await cursor.execute('DELETE FROM times WHERE game = ?', (game,))
            await self.db.commit()

            game = row[0]

        await ctx.send(f"Deleted PB for {game}")


def prepare(bot):
    bot.add_cog(PBs(bot))


def breakdown(bot):
    bot.loop.create_task(close_db(bot))


async def close_db(bot):
    await bot.dbs['pbs'].close()
    del bot.dbs['pbs']
