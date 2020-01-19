import logging
import paho.mqtt.client as mqtt


class MqttClient(mqtt.Client):
  """
  This Class represents the MQTT - Client which handles each mqtt - message.
  """
  def __init__(self, mqttAddress, mqttPort, mqttTopicName, callback, **kwargs):
    # self.__client = mqtt.Client(client_id=clientId)
    self.__callback = callback
    self.__logger = logging.getLogger().getChild('mqtt_client')

    self.__mqttAddress = mqttAddress
    self.__mqttPort = mqttPort
    self.__mqttTopicName = mqttTopicName

    super().__init__(kwargs)

  def start(self):
    """
    Tries to establish a connection to the mqtt - server on the given
    address and port.

    If the connection was sucessfull, the client will subscripe to each subtopic
    on the given root - topic. 
    """
    self.__logger.info(f'Trying to Connect to the MQTT - Server on {self.__mqttAddress}:{self.__mqttPort}')
    self.connect(self.__mqttAddress, self.__mqttPort)
    
    self.__logger.debug('Starting Listener Loop...')
    self.loop_start()

  def shutdown(self):
    self.__logger.debug('Stopping MQTT - Listener Loop')
    self.loop_stop()

  def on_connect(self, mqttc, obj, flags, rc):
    self.__logger.info('Connected to the MQTT - Server.')
    self.subscribe(f'{self.__mqttTopicName}/#')

  def on_message(self, mqttc, obj, msg):
    self.__logger.debug(f'Message Received')
    self.__logger.debug(f'Topic: {msg.topic}')
    self.__logger.debug(f'Message Payload: {msg.payload}')
