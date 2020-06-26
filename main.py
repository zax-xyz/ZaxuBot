from src import bot


def main():
    _bot = bot.Bot()

    try:
        _bot.loop.run_until_complete(_bot.start())
    except KeyboardInterrupt:
        try:
            _bot.loop.run_until_complete(_bot.pbs_db.close())
        except (AttributeError, ValueError):
            pass
    finally:
        _bot._ws.teardown()


if __name__ == "__main__":
    main()
