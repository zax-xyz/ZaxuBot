from src import bot


def main():
    _bot = bot.Bot()

    try:
        _bot.loop.run_until_complete(_bot.start())
    except KeyboardInterrupt:
        for db in _bot.dbs.values():
            _bot.loop.run_until_complete(db.close())
    finally:
        _bot._ws.teardown()


if __name__ == "__main__":
    main()
