import logging
from yaml import safe_load, YAMLError

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
      
      if missingKeys:
        self.__logger.error('There are some keys missing')
        self.__logger.error(f'Missing Keys: {missingKeys}')
        continue

      if not nameInvalid and not idInvalid and not rangeInvalid:
        validFlowers.append(currentFlower)
  
    return validFlowers
      
