import coloredlogs
import logging
import configargparse
 
from time import sleep

from src.mqtt_client import MqttClient
from src.telegram_bot import TelegramBot
from src.flower_handler import FlowerHandler

from src.types.message import Message
from src.types.user_message import UserMessage

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

mqttClient = None
telegramBot = None

lastChatIds = []

def mqttCallback(message: Message):
    if message.requested:
        global lastChatIds
        messageToSend = f'Water level at {message.aggregatedValue} %'
        telegramBot.sendMessage(lastChatIds[0], messageToSend)

        messageForState: UserMessage = flowerHandler.getMessage(int(message.sensorNumber), int(message.aggregatedValue))
        if messageForState:
            if messageForState.includePhoto:
                telegramBot.sendMessage(lastChatIds[0], messageForState.message, photo=messageForState.photoPath)

            else:
                telegramBot.sendMessage(lastChatIds[0], messageForState.message)

        lastChatIds = lastChatIds[1:]

def telegramCallback(update, context):
    print('todo: send request to the mqtt - client')
    logger.debug('Sending a Request to the MQTT - Handler')
    
    chatId = update.message.chat.id
    if len(context.args) != 1:
        telegramBot.sendMessage(chatId, 'Wrong Arguments :(. See /help for any additional informations.\nTodo: Implement /help command.')
        return
    
    flowerName = context.args[0]
    flower = flowerHandler.getFlower(flowerName)
    logger.debug(f'Sending an mqtt - request for flower: {flower}')
    mqttClient.querySensor(flower)
    lastChatIds.append(chatId)

flowerHandler = FlowerHandler()

try:
    flowerHandler.parse('flowers.yaml')
except ValueError:
    logger.error('Failed to parse the flower file.')
    exit(1)

mqttClient = MqttClient(args.mqtt_server_address, args.mqtt_server_port, 'blume', mqttCallback)
telegramBot = TelegramBot(args.telegram_api_token, telegramCallback)

logger.info('Starting the MQTT - Client')
mqttClient.start()

try:
    logger.info('Entering the Telegram Bot listener loop')
    telegramBot.setup()
    telegramBot.listen()
except KeyboardInterrupt:
    logger.info('Shutting down the bot...')
