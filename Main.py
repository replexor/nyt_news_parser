from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update
from dotenv import dotenv_values
import threading
from State import State
from Parsing import loadToTelegram

env = dotenv_values('.env')

def getNews(update: Update, context: CallbackContext):
    if len(context.args) > 0:
        if context.args[0] == "on" and State.tread == None:
            State.tread = threading.Thread(target=loadToTelegram, args=(update, context))
            State.treadStop = False
            State.tread.start()
            context.bot.sendMessage(chat_id=update.effective_chat.id, text="Новости включены!")
        elif context.args[0] == "off" and State.tread != None:
            State.treadStop = True
            State.tread = None
            context.bot.sendMessage(chat_id=update.effective_chat.id, text="Новости отключены!")
        else:
            context.bot.sendMessage(chat_id=update.effective_chat.id, text="Неправильная команда!")
    else:
        context.bot.sendMessage(chat_id=update.effective_chat.id, text="Неправильная команда!")


def getGreeting(update: Update, context: CallbackContext):
    context.bot.sendMessage(chat_id=update.effective_chat.id, text="Добро пожаловать!")

if __name__ == '__main__':
    updater = Updater(token=env['TG_TOKEN'], use_context=True)
    updater.dispatcher.add_handler(CommandHandler('news', getNews))
    updater.dispatcher.add_handler(CommandHandler('start', getGreeting))
    updater.start_polling()
    