import logging
from telegram.ext import Updater, CommandHandler

class TelegramBot():
  def __init__(self, token):
    self.__updater = Updater(token=token, use_context=True)
    self.__dispatcher = self.__updater.dispatcher
    self.__logger = logging.getLogger().getChild('TelegramBot')


  def setupAndStart(self):
    testHandler = CommandHandler('test', self.test)
    self.__dispatcher.add_handler(testHandler)

  def test(self, update, context):
    print('lol')
    context.bot.send_message(chat_id=update.effective_chat.id, text='lol')
    
  def listen(self):
    self.__updater.start_polling()
