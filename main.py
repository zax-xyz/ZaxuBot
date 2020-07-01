from src.bot import Bot


def main():
    bot = Bot()

    try:
        bot.loop.run_until_complete(bot.start())
    except KeyboardInterrupt:
        for db in bot.dbs.values():
            bot.loop.run_until_complete(db.close())
    finally:
        bot._ws.teardown()


if __name__ == "__main__":
    main()
