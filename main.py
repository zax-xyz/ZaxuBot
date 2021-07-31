from src.bot import Bot


def main():
    bot = Bot()

    try:
        bot.run()
    finally:
        for db in bot.dbs.values():
            bot.loop.run_until_complete(db.close())


if __name__ == "__main__":
    main()
