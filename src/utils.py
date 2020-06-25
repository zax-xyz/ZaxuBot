from datetime import datetime

from termcolor import colored


def current_time():
    t = datetime.now()
    return colored(t.strftime("%Y-%m-%d %H:%M:%S"), "green")


def is_mod(ctx):
    return ctx.author.is_mod


def plural(num):
    if abs(num) != 1:
        return "s"
    return ""
