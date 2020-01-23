from dataclasses import dataclass

@dataclass
class UserMessage():
  """
  Represents a message which is send to the user via the telegram bot.
  """
  text: str
  __includePhoto: bool = False
  __photoPath: str = ''

  @property
  def includePhoto(self):
    return self.__includePhoto

  @includePhoto.setter
  def includePhoto(self, newValue):
    self.__includePhoto = newValue
  
  @property
  def photoPath(self):
    return self.__photoPath

  @photoPath.setter
  def photoPath(self, newValue):
    self.__photoPath = newValue