import logging
from telegram.ext import Updater, CommandHandler

class TelegramBot():
  def __init__(self, token, messageCallback):
    self.__updater = Updater(token=token, use_context=True)
    self.__dispatcher = self.__updater.dispatcher
    self.__logger = logging.getLogger().getChild('TelegramBot')
    self.__messageCallback = messageCallback

  def setup(self):
    self.__dispatcher.add_handler(CommandHandler('wasserstand', self.__flowerCommand))

  def __flowerCommand(self, update, context):
    self.__logger.debug('Update Received:')
    self.__logger.debug(update)
    self.__messageCallback(update, context)
    
  def sendMessage(self, chatId, message, photo=None):
    if photo:
      self.__updater.bot.send_photo(chat_id=chatId, photo=open(photo, 'rb'))
    
    self.__logger.debug(f'Sending Message to chat with id: {chatId}')
    self.__logger.debug(f'Message Content: {message}')
    self.__updater.bot.send_message(chat_id=chatId, text=message)

  def listen(self):
    self.__updater.start_polling()
