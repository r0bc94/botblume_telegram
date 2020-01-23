import logging
import paho.mqtt.client as mqtt

from src.types.message import Message

class MqttClient(mqtt.Client):
  """
  This Class represents the MQTT - Client which handles each mqtt - message.
  """
  def __init__(self, mqttAddress, mqttPort, mqttTopicName, callback, delimiter=';', **kwargs):
    # self.__client = mqtt.Client(client_id=clientId)
    self.__callback = callback
    self.__logger = logging.getLogger().getChild('mqtt_client')

    self.__mqttAddress = mqttAddress
    self.__mqttPort = mqttPort
    self.__mqttTopicName = mqttTopicName

    self.__delimiter = delimiter

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
  
  def querySensor(self, sensorNumber):
    #todo: Also make the parameter for the water level optional.
    self.publish(f'{self.__mqttTopicName}/{sensorNumber}/wasserstand')

  def shutdown(self):
    self.__logger.debug('Stopping MQTT - Listener Loop')
    self.loop_stop()

  def on_connect(self, mqttc, obj, flags, rc):
    self.__logger.info('Connected to the MQTT - Server.')
    self.subscribe(f'{self.__mqttTopicName}/+/status')

  def on_message(self, mqttc, obj, msg):
    self.__logger.debug(f'Message Received')
    self.__logger.debug(f'Topic: {msg.topic}')
    self.__logger.debug(f'Message Payload: {msg.payload}')

    # Since the main loop is running in a dedicated thread, 
    # all exceptions are kinda swallowed. 
    # Therefore, we have to catch them again manually.
    message = None
    try:
      message = self.__processMessage(msg.topic, msg.payload)

      if message is not None:
        self.__callback(message)

    except Exception as ex:
      self.__logger.error('An Exception was thrown on the MQTT Listener Thread')
      self.__logger.exception(ex)
      raise ex

  def __processMessage(self, topic, message):
    msgObj = None
    try:
      aggregated, raw, requested = message.decode().split(self.__delimiter)
      sensorNumber = topic.split('/')[1]

      requestedAsBool = requested.lower() in ['1', 'true']

      msgObj = Message(sensorNumber=sensorNumber,
        aggregatedValue=int(aggregated),
        rawValue=int(raw),
        requested=requestedAsBool)
    
    except ValueError:
      self.__logger.error(f'Could not parse the message f{message} for topic f{topic}')
      self.__logger.error('Check the format of your message!')

    return msgObj
