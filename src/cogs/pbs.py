import re

import aiosqlite
import srcom
from twitchio.ext import commands

from src.utils import is_mod


class PBs:

    category_pat = re.compile(r"\[(.+?)\]")

    def __init__(self, bot):
        self.bot = bot

        bot.loop.run_until_complete(self.create_table())

    async def create_table(self):
        """Create the pb SQL table if it doesn't already exist"""
        self.db = await aiosqlite.connect("pbs.db")
        self.bot.dbs["pbs"] = self.db

        async with self.db.cursor() as cursor:
            await cursor.execute(
                """CREATE TABLE IF NOT EXISTS times (
                    game TEXT NOT NULL PRIMARY KEY COLLATE NOCASE,
                    time TEXT NOT NULL
                )"""
            )

            await self.db.commit()

    async def get_channel_info(self, ctx):
        """Gets information about a channel from a context object"""
        users = await self.bot.get_users(ctx.channel.name)
        channel_id = users[0].id

        channel = await self.bot.http.request(
            "GET",
            "/channels",
            params=[
                ("broadcaster_id", channel_id),
            ],
        )

        return channel[0]

    async def get_display_name(self, username):
        """Gets a user's display name from their username"""
        user = await self.bot.get_users(username)
        return user[0].display_name

    async def get_category(self, title):
        """Gets a speedrun category from the stream title

        Assumes the title begins with the category in square brackets - [CAT]
        """
        category = self.category_pat.match(title)
        if category is None:
            return None

        category = category[1]
        return category

    @commands.command(name="pb", aliases=["getpb"])
    async def get_pb(self, ctx, *, game=None):
        """Get the streamer's PB for a game.

        Uses the current stream game if none given
        """
        if game is None:
            channel = await self.get_channel_info(ctx)
            game = channel["game_name"]
            channel = channel["broadcaster_name"]
        else:
            channel = await self.get_display_name(ctx.channel.name)

        # Get PB from database
        async with self.db.cursor() as cursor:
            await cursor.execute(
                "SELECT game, time FROM times WHERE game = ?", (game,)
            )

            pb = await cursor.fetchone()
            if pb is None:
                return await ctx.send(f"No PB found for {game}")

        game, pb = pb

        await ctx.send(f"{channel}'s current {game} PB is {pb}")

    @commands.check(is_mod)
    @commands.command(name="setpb")
    async def set_pb(self, ctx, time, *, game=None):
        """Sets the streamer's PB for a game

        Uses the current stream game if none given.
        """
        game = game or (await self.get_channel_info(ctx))["game_name"]

        # Add or replace PB in database
        async with self.db.cursor() as cursor:
            await cursor.execute(
                "REPLACE INTO times (game, time) VALUES (?, ?)", (game, time)
            )
            await self.db.commit()

            await cursor.execute(
                "SELECT game FROM times WHERE game = ?", (game,)
            )
            game = (await cursor.fetchone())[0]

        await ctx.send(f"Set PB for {game} to {time}")

    @commands.check(is_mod)
    @commands.command(name="delpb", aliases=["deletepb"])
    async def delete_pb(self, ctx, *, game=None):
        """Deletes the streamer's PB for a game

        Uses the current stream game if none given.
        """
        game = game or (await self.get_channel_info(ctx))["game_name"]

        # Delete PB from database
        async with self.db.cursor() as cursor:
            await cursor.execute(
                "SELECT game FROM times WHERE game = ?", (game,)
            )

            row = await cursor.fetchone()
            if row is None:
                return await ctx.send(f"No PB found for {game}")

            await cursor.execute("DELETE FROM times WHERE game = ?", (game,))
            await self.db.commit()

            game = row[0]

        await ctx.send(f"Deleted PB for {game}")

    @commands.command(name="wr", aliases=["getwr"])
    async def get_wr(self, ctx, *, game=None):
        """Get the current WR for a game

        Uses the current stream game if none given.
        """
        game = game or (await self.get_channel_info(ctx))["game_name"]

        async with srcom.Client() as client:
            srcom_game = await client.get_game(name=game)
            default_cat = srcom_game.default_category

            category = await srcom.Category.from_id(default_cat, client)
            variables = await category.variables()
            subcategories = [var for var in variables if var.is_subcategory]
            params = {f"var-{var.id}": var.default for var in subcategories}

            record = await category.record(False, params)
            if record is None:
                return await ctx.send(f"World record for {game} not found")

            runner = await record.player()
            await ctx.send(
                "The world record for {} ({}) is {} by {}. {}".format(
                    game,
                    ", ".join(
                        [category.name]
                        + [v.values[v.default]["label"] for v in subcategories]
                    ),
                    record.time[:-3] if "." in record.time else record.time,
                    runner.name,
                    record.link,
                )
            )


def prepare(bot):
    bot.add_cog(PBs(bot))


def breakdown(bot):
    bot.loop.create_task(close_db(bot))


async def close_db(bot):
    await bot.dbs["pbs"].close()
    del bot.dbs["pbs"]
