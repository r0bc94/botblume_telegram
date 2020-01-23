import pytest
from yaml import safe_load

from src.flower_handler import FlowerHandler
from src.types.flower import Flower
from src.types.user_message import UserMessage

class TestFlowerHandler():
  @pytest.fixture(scope = "session")
  def flowerHandler(self):
    return FlowerHandler()

  @pytest.fixture(scope = "session")
  def flowerFixture(self):
    shouldMessage1 = UserMessage(percentageMin=0, percentageMax=15, message='Please give me some water.')
    shouldMessage1.includePhoto = True
    shouldMessage1.photoPath = 'water.png'
    shouldMessage2 = UserMessage(percentageMin=16, percentageMax=30, message='Im okay but you should water me in the near future')
    
    return Flower(name='flower1', mqttId=1, messages=[shouldMessage1, shouldMessage2])

  def testValid(self, flowerHandler, flowerFixture):
    parsed = flowerHandler.parse('test/flower_parser_tests/valid_flowerfile.yaml')
    assert len(parsed) == 1, 'There where either not enough or too much parsed flowers.'
    assert parsed[0] == flowerFixture

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

  def testDublicateId(self, flowerHandler, flowerFixture):
    parsed = flowerHandler.parse('test/flower_parser_tests/dublicate_id.yaml')
    
    assert len(parsed) == 1, 'There where either not enough or too much parsed flowers.'
    assert parsed[0] == flowerFixture

  def testNoPhotoPath(self, flowerHandler):
    try:
      flowerHandler.parse('test/flower_parser_tests/no_photo_path_given.yaml')
    
      assert False, 'There was no exception thrown.'
    except ValueError:
      assert True

    except AssertionError:
      raise

    except Exception:
      assert False, 'An unexpected exception was thrown while parsing the yaml file.'

  def testGetMessage(self, flowerHandler):
    flowerHandler.parse('test/flower_parser_tests/valid_flowerfile.yaml')
    expectedMessage = UserMessage(percentageMin=0, percentageMax=15, message='Please give me some water.')
    expectedMessage.includePhoto = True
    expectedMessage.photoPath = 'water.png'

    actualMessage = flowerHandler.getMessage('flower1', 0)

    assert expectedMessage == actualMessage
