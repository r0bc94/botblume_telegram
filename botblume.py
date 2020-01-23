import coloredlogs
import logging
import configargparse
 
from time import sleep

from src.mqtt_client import MqttClient
from src.telegram_bot import TelegramBot
from src.flower_handler import FlowerHandler

import paho.mqtt.client as mqtt

from yaml import safe_load

LOGGING_FORMAT = '[%(levelname)s] %(asctime)s %(name)s: %(message)s'
LOGGING_LEVEL_COLORS = {
    'debug': {
        'color': 'black',
        'bright': True
    },
    'warning': {
        'color': 'yellow'
    },
    'error': {
        'color': 'red',
    }
}

LOGGING_FIELD_COLORS = {
    'levelname': {
        'color': 'green',
    },
    'name': {
        'color': 'blue'
    },
    'asctime': {
        'color': 'cyan'
    }
}

def setup_logger(logger: logging.Logger, logDebug: bool):
    loglevel = 'DEBUG' if logDebug else 'INFO'
    coloredlogs.install(loglevel, fmt=LOGGING_FORMAT, level_styles=LOGGING_LEVEL_COLORS, field_styles=LOGGING_FIELD_COLORS)
    logger.debug('Logger installed')

    if logDebug:
        logger.info('Debug Logs Activated')

def setup_config_arguments(argParser: configargparse.ArgParser):
    argParser.add_argument('-c', '--config-file', required=False, is_config_file=True, help='Path to the Config File which should be used.')
    argParser.add_argument('-t', '--telegram_api_token', required=True, help='Your Telegram Bot - Token.')
    argParser.add_argument('-ma', '--mqtt_server_address', required=False, default='127.0.0.1', help='The IP - Address of the MQTT - Server')
    argParser.add_argument('-mp', '--mqtt_server_port', required=False, type=int, default=1887, help='The port of the MQTT - Server.')
    argParser.add_argument('-d', '--debug', required=False, action='store_true', default=False, help='Set this Switch for additional debug logs.')
    
argumentParser = configargparse.ArgParser(default_config_files=['./config.conf'])

setup_config_arguments(argumentParser)
args = argumentParser.parse_args()

logger = logging.getLogger(__name__)
setup_logger(logger,  args.debug)

flowerHandler = FlowerHandler()
flowerHandler.parse('flowers.yaml')

# def cb(message):
#     print(message)

# mqttClient = MqttClient('192.168.1.5', 1883, 'blume', cb)
# mqttClient.start()


# chatId = ''

# def telegramCB(update, context):
#     print(update)
#     print(context)
#     global chatId
#     chatId = update.message.chat_id

# telegramBot = TelegramBot(args.telegram_api_token, telegramCB)
# telegramBot.setupAndStart()
# telegramBot.listen()

# while True:
#     sleep(1)
#     print(chatId)
#     if chatId: 
#         telegramBot.sendMessage(chatId, 'test', photo=open('cat.jpg', 'rb'))
#         chatId = ''
    # mqttClient.querySensor(1)
