import logging
from telegram.ext import Updater, CommandHandler

class TelegramBot():
  def __init__(self, token, messageCallback):
    self.__updater = Updater(token=token, use_context=True)
    self.__dispatcher = self.__updater.dispatcher
    self.__logger = logging.getLogger().getChild('TelegramBot')
    self.__messageCallback = messageCallback

  def setupAndStart(self):
    self.__dispatcher.add_handler(CommandHandler('wasserstand', self.__flowerCommand))

  def __flowerCommand(self, update, context):
    self.__messageCallback(update, context)
    
  def listen(self):
    self.__updater.start_polling()
