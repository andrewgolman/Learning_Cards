from telegram.ext import Updater
from db import queries
import say
import register
import handlers
import logging

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

token = open("token", "r").read().strip()


def main():
    updater = Updater(token=token)
    dp = updater.dispatcher

    for handler in handlers.simple_handlers:
        dp.add_handler(handler)

    for handler in handlers.conversation_handlers:
        dp.add_handler(handler)

    dp.add_handler(handlers.unknown_message_handler)

    dp.add_error_handler(handlers.telegram_error_handler)

    updater.start_polling()
    # updater.idle()


if __name__ == '__main__':
    main()
