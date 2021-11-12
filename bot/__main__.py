from bot import updater, dispatcher
from telegram.ext import CommandHandler
from telegram.update import Update
from telegram.ext import CallbackContext
import bot.clip as clip


def start(update: Update, context: CallbackContext):
    context.bot.send_message(update.message.chat_id, text="send /clip youtube-link 3:20 4:25 to clip a youtube video "
                                                          "where 3:20 is the start time of the clip and 4:25 is the "
                                                          "end time")


start_handler = CommandHandler('start', start, run_async=True)
dispatcher.add_handler(start_handler)
clip.add_handler()
updater.start_polling()
