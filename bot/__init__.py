from telegram.ext import Updater, Dispatcher
import logging
from dotenv import load_dotenv
import os


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
load_dotenv('config.env')

try:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
except KeyError:
    logging.error("Bot token not provided!")
    BOT_TOKEN = None
    quit()

updater = Updater(token=BOT_TOKEN)
dispatcher: Dispatcher = updater.dispatcher
