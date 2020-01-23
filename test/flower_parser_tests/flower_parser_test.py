import pytest
from yaml import safe_load

from src.flower_handler import FlowerHandler
from src.user_message import UserMessage

class TestFlowerHandler():
  @pytest.fixture(scope = "session")
  def flowerHandler(self):
    return FlowerHandler()

  def testValid(self, flowerHandler):
    parsed = flowerHandler.parse('test/flower_parser_tests/valid_flowerfile.yaml')
    should = [{'name': 'flower1', 'mqtt_id': 1, 'messages': [{'percentage_min': 0, 'percentage_max': 15, 'message': 'Please give me some water.', 'include_photo': True, 'photo_path': 'water.png'}, {'percentage_min': 16, 'percentage_max': 30, 'message': 'Im okay but you should water me in the near future'}]}]
    self.__compareResults(should, parsed)
    self.__compareResults(should, parsed)

  def testIntersectingRanges(self, flowerHandler):
    try:
      flowerHandler.parse('test/flower_parser_tests/range_intersection.yaml')
    
      assert False, 'There was no exception thrown.'
    except ValueError:
      assert True

    except AssertionError:
      raise

    except Exception:
      assert False, 'An unexcepted exception was thrown while parsing the yaml file.'

  def testDublicateId(self, flowerHandler):
    expected = [{'name': 'flower1', 'mqtt_id': 1, 'messages': [{'percentage_min': 0, 'percentage_max': 15, 'message': 'Please water me soon.', 'include_photo': True, 'photo_path': 'water.png'}, {'percentage_min': 16, 'percentage_max': 30, 'message': 'Im okay but you should water me in the near future'}]}]
    result = flowerHandler.parse('test/flower_parser_tests/dublicate_id.yaml')
    
    self.__compareResults(expected, result) 

  def testNoPhotoPath(self, flowerHandler):
    try:
      flowerHandler.parse('test/flower_parser_tests/no_photo_path_given.yaml')
    
      assert False, 'There was no exception thrown.'
    except ValueError:
      assert True

    except AssertionError:
      raise

    except Exception:
      assert False, 'An unexcepted exception was thrown while parsing the yaml file.'

  def testGetMessage(self, flowerHandler):
    flowerHandler.parse('test/flower_parser_tests/valid_flowerfile.yaml')
    expectedMessage = UserMessage(text='Please give me some water.')
    expectedMessage.includePhoto = True
    expectedMessage.photoPath = 'water.png'

    actualMessage = flowerHandler.getMessage('flower1', 0)
    self.__compareMessages(expectedMessage, actualMessage)

  def __compareResults(self, should, result):
    for curShouldDict, curResultDict in zip(should, result):
      # Compare the keys
      assert curShouldDict.keys() == curResultDict.keys(), 'The Dictionary does not contain all expected keys.'

      # Compare the values:
      for shKey, resKey in zip(curShouldDict.keys(), curResultDict.keys()):
        assert curShouldDict[shKey] == curResultDict[resKey], f'Wrong Value for Key "{shKey}"'

  def __compareMessages(self, expected, actual):
    assert type(expected) == type(actual), 'The passed objects are not from the same type.'
    assert expected.text == actual.text
    
    if expected.includePhoto:
      assert expected.includePhoto == actual.includePhoto
      assert expected.photoPath == actual.photoPath
