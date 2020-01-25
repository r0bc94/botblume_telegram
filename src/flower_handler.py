import logging
from yaml import safe_load, YAMLError

from src.types.flower import Flower
from src.types.user_message import UserMessage

class FlowerHandler():
  def __init__(self):
    self.__logger = logging.getLogger().getChild('flower_handler')
    self.__flowers = []

  @property
  def flowers(self):
    return self.__flowers

  def parse(self, flowerFilePath):
    try:
      parsedFlowers = safe_load(open(flowerFilePath))
      validFlowers = self.__sanityCheck(parsedFlowers)

      if not validFlowers:
        raise ValueError('Failed to parse all flowers from the FlowerFile.')
      
      self.__flowers = self.__createObjectsFromDicts(validFlowers)

    except FileNotFoundError:
      self.__logger.error('The flower file flowers.yaml was not found in the root directory of this application.')
      self.__logger.error('Please make sure, this file exists.')
    
    except YAMLError as ymerr:
      self.__logger.error('Failed to parse the flower file.')
      self.__logger.error('Please check the format of the given file.')
      self.__logger.exception(ymerr)

    return self.__flowers

  def getMessage(self, mqttId, percentage):
    for currentFlower in self.__flowers:
      if currentFlower.mqttId == mqttId:
        return self.__findMessage(currentFlower, percentage)

  def getFlower(self, flowerName):
    for currentFlower in self.__flowers:
      if currentFlower.name == flowerName:
        return currentFlower

  def getFlowerByMqttId(self, mqttId):
    for currentFlower in self.__flowers:
      if currentFlower.mqttId == mqttId:
        return currentFlower

  def __findMessage(self, flower, percentage):
    for curMessage in flower.messages:
      if curMessage.percentageMin <= percentage and curMessage.percentageMax >= percentage:
        return curMessage

    return None
  
  def __sanityCheck(self, parsedYaml):
    """
    Sanity checks each given flower object, if all needed properties exists.
    Also the range of each message is checked for collisions.

    Warning: This is probably one of the most ugly methods I've ever written.
    """
    validFlowers = []

    neededKeys = ['name', 'mqtt_id', 'messages']

    for currentFlower in parsedYaml:
      missingKeys = []
      nameInvalid = False
      idInvalid = False
      rangeInvalid = False
      noPhotoPath = False

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
                
                rangeInvalid |= currentMessage['percentage_min'] <= curMax and currentMessage['percentage_min'] >= curMin
                rangeInvalid |= currentMessage['percentage_max'] >= curMin and currentMessage['percentage_max'] <= curMax

                if rangeInvalid:
                  break

              if not rangeInvalid:
                lastRanges.append([currentMessage['percentage_min'], currentMessage['percentage_max']])

            # Check if the path to a photo is provided, when the 
            # include_photo property is set to True.
            if 'include_photo' in currentMessage and currentMessage['include_photo']:
              noPhotoPath = 'photo_path' not in currentMessage.keys()

          if rangeInvalid:
            self.__logger.warning(f"Invalid Message Range {currentMessage['percentage_min']} - {currentMessage['percentage_max']}")
            self.__logger.warning('This Flower will be ignored.')
            self.__logger.warning('Hint: Check for any intersections in your message definitions.')
            break

          if noPhotoPath:
            self.__logger.warning('A photo should be included, but no path was specified.')
            self.__logger.warning('Please specify the path to the photo by using the "photo_path" property.')
            break

      if missingKeys:
        self.__logger.warning('There are some keys missing')
        self.__logger.warning(f'Missing Keys: {missingKeys}')
        continue

      if not nameInvalid and not idInvalid and not rangeInvalid and not noPhotoPath:
        validFlowers.append(currentFlower)
  
    return validFlowers

  def __createObjectsFromDicts(self, dicts):
    objects = []
    for currentDict in dicts:
      name = currentDict['name']
      mqttId = currentDict['mqtt_id']
      messages = self.__createUserMessagesFromDicts(currentDict['messages'])

      flowerObject = Flower(name=name, mqttId=mqttId, messages=messages)
      objects.append(flowerObject)

    return objects

  def __createUserMessagesFromDicts(self, dicts):
    userMessageObjects = []
    
    for currentUserMessage in dicts:

      try:
        percentageMin = currentUserMessage['percentage_min']
        percentageMax = currentUserMessage['percentage_max']
        message = currentUserMessage['message']
      
        userMessage = UserMessage(percentageMin=percentageMin, percentageMax=percentageMax, message=message)
      
        if 'include_photo' in currentUserMessage.keys(): 
          userMessage.includePhoto = currentUserMessage['include_photo']
          userMessage.photoPath = currentUserMessage['photo_path']
      except KeyError as ke:
        self.__logger.warning(f'Missing Key in Message: "{ke}"')
        self.__logger.warning(f'The Message will be skipped.')
        continue

      userMessageObjects.append(userMessage)
    
    return userMessageObjects
