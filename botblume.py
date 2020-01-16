import configargparse

def setup_config_arguments(argParser: configargparse.ArgParser):
    argParser.add_argument('-c', '--config-file', required=False, is_config_file=True, help='Path to the Config File which should be used.')
    argParser.add_argument('-t', '--telegram_api_token', required=True, help='Your Telegram Bot - Token.')
    argParser.add_argument('-ma', '--mqtt_server_address', required=False, default='127.0.0.1', help='The IP - Address of the MQTT - Server')
    argParser.add_argument('-mp', '--mqtt_server_port', required=False, type=int, default=1887, help='The port of the MQTT - Server.')
    
argumentParser = configargparse.ArgParser(default_config_files=['./config.conf'])

setup_config_arguments(argumentParser)

args = argumentParser.parse_args()
print(args)