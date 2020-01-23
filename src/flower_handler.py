import logging
from yaml import safe_load, YAMLError

from src.user_message import UserMessage

class FlowerHandler():
  def __init__(self):
    self.__logger = logging.getLogger().getChild('flower_handler')
    self.__parsedFlowers = []

  def parse(self, flowerFilePath):
    try:
      parsedFlowers = safe_load(open(flowerFilePath))
      validFlowers = self.__sanityCheck(parsedFlowers)

      if not validFlowers:
        raise ValueError('Failed to parse all flowers from the FlowerFile.')
      
      self.__parsedFlowers = validFlowers

    except FileNotFoundError:
      self.__logger.error('The flower file flowers.yaml was not found in the root directory of this application.')
      self.__logger.error('Please make sure, this file exists.')
    
    except YAMLError as ymerr:
      self.__logger.error('Failed to parse the flower file.')
      self.__logger.error('Please check the format of the given file.')
      self.__logger.exception(ymerr)

    return self.__parsedFlowers

  def getMessage(self, flowerName, percentage):
    message = None
    userMessage = None

    for currentFlower in self.__parsedFlowers:
      if currentFlower['name'] == flowerName:
        message = self.__findMessage(currentFlower, percentage)

    if message:
      userMessage = UserMessage(text=message['message'])

      if message['include_photo'] and message['photo_path']:
        userMessage.includePhoto = True
        userMessage.photoPath = message['photo_path']

    return userMessage

  def getFlower(self, flowerName):
    for currentFlower in self.__parsedFlowers:
      if currentFlower['name'] == flowerName:
        return currentFlower

  def getFlowerByMqttId(self, mqttId):
    for currentFlower in self.__parsedFlowers:
      if currentFlower['mqtt_id'] == mqttId:
        return currentFlower

  def __findMessage(self, flower, percentage):
    for curMessage in flower['messages']:
      if curMessage['percentage_min'] <= percentage and curMessage['percentage_max'] >= percentage:
        return curMessage

    return None
  
  def __sanityCheck(self, parsedYaml):
    """
    Sanity checks each given flower object, if all needed properties exists.
    Also the range of each message is checked for collisions.
    """
    validFlowers = []

    neededKeys = ['name', 'mqtt_id', 'messages']

    for currentFlower in parsedYaml:
      missingKeys = []
      nameInvalid = False
      idInvalid = False
      rangeInvalid = False

      for key, value in currentFlower.items():
        if key not in neededKeys:
          missingKeys.append(key)
          continue
      
        # Check for dublicate names:
        if key == 'name':
          for validFlower in validFlowers:
            if validFlower[key] == value:
              self.__logger.warning(f'Dublicate Flower with name {value}')
              self.__logger.warning('This flower will be ignored!')
              nameInvalid = True

        if key == 'mqtt_id':
          for validFlower in validFlowers:
            if validFlower[key] == value:
              self.__logger.warning(f'Dublicate Flower with mqtt_id "{value}"')
              self.__logger.warning('This flower will be ignored!')
              idInvalid = True

        # Check the message ranges
        if key == 'messages':
          lastRanges = []
          for currentMessage in value:
            if not lastRanges:
              lastRanges.append([currentMessage['percentage_min'], currentMessage['percentage_max']])
            else:
              for curMin, curMax in lastRanges:
                rangeInvalid |= currentMessage['percentage_min'] >= currentMessage['percentage_max']
                rangeInvalid |= currentMessage['percentage_min'] <= curMax

          if rangeInvalid:
            self.__logger.warning(f'Invalid Message Range {curMin} - {curMax}')
            self.__logger.warning('This Flower will be ignored.')
            break

      # Check if the path to a photo is provided, when the 
      # include_photo property is set to True.
      if key == 'include_photo' and value == True:
        if 'photo_path' not in currentFlower.keys():
          self.__logger.warning('A photo should be included, but no path was specified.')
          self.__logger.warning('Please specify the path to the photo by using the "photo_path" property.')
      
      if missingKeys:
        self.__logger.warning('There are some keys missing')
        self.__logger.warning(f'Missing Keys: {missingKeys}')
        continue

      if not nameInvalid and not idInvalid and not rangeInvalid:
        validFlowers.append(currentFlower)
  
    return validFlowers
      
