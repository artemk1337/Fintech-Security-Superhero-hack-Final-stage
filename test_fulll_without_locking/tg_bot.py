# !pip install python-telegram-bot --upgrade
from telegram.ext import Updater, CommandHandler, run_async
from telegram import ChatAction
from telegram import error
import logging
import os
import ctypes
from datetime import datetime

from private import telegram_admins, TOKEN, REQUEST_KWARGS, PC_info
from utils import block_system


class TelegramBot:
    def __init__(self, msg):
        self.msg_ = msg
        self.logger = None
        self.updater = None
        self.TOKEN = TOKEN
        self.REQUEST_KWARGS = REQUEST_KWARGS
        self.admins_id = telegram_admins
        self.pc_info = PC_info

    # logging errors
    def logging(self, filename='logs.txt'):
        if filename:
            logging.basicConfig(filename=filename,
                                filemode='a',
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                level=logging.INFO)
        else:
            logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    # hello-message
    def start(self, update, context):
        context.bot.send_chat_action(chat_id=update.message.chat.id,
                                     action=ChatAction.TYPING)
        print(update.message.from_user.id)
        update.message.reply_text("<b>Hello!</b>\n"
                                  f"Your id: <u>{update.message.from_user.id}</u>",
                                  parse_mode="HTML")

    def error(self, update, context):
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', update, context.error)
        # WE CAB LOCK SYSTEM HERE IF THERE'RE PROBLEMS WITH TELEGRAM CONNECTION

    def send_message_admin(self, update, context):
        import signal
        for id_ in self.admins_id:
            context.bot.send_chat_action(chat_id=id_,
                                         action=ChatAction.TYPING)
            context.bot.send_message(chat_id=id_,
                                     text=f"<b>{self.msg_}</b>\n\n"
                                          f"<em>{self.pc_info}</em>",
                                     parse_mode='HTML'
                                     )
        os.kill(os.getpid(), signal.SIGINT)

    def start_bot(self):
        # pp = PicklePersistence(filename='conversationbot')
        pp = False
        self.updater = Updater(self.TOKEN,
                               persistence=pp,
                               use_context=True,
                               request_kwargs=self.REQUEST_KWARGS)
        self.dp = self.updater.dispatcher
        self.dp.add_handler(CommandHandler('start', self.start))  # /start
        self.logging(None)
        self.dp.add_error_handler(self.error)
        self.updater.is_idle = False
        try:
            self.updater.start_polling()
        except error.NetworkError:
            # block_system()
            pass
        print("Start bot")

        if self.msg_ != 'TEST BOT':
            self.send_message_admin(self.updater, self.dp)

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        # self.updater.idle()

    @run_async
    def shutdown(self):
        self.updater.stop()
        self.updater.is_idle = False


if __name__ == "__main__":
    tg = TelegramBot('TEST BOT')
    tg.start_bot()





