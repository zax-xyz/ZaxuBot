from src import bot

if __name__ == "__main__":
    bot = bot.Bot()

    try:
        bot.loop.run_until_complete(bot.start())
    except KeyboardInterrupt:
        try:
            bot.loop.run_until_complete(bot.pbs_db.close())
        except (AttributeError, ValueError):
            pass
    finally:
        bot._ws.teardown()
