from dataclasses import dataclass
from typing import List

from .user_message import UserMessage

@dataclass
class Flower():
  """
  This class represents a parsed flower.
  """
  name: str
  mqttId: int
  messages: List[UserMessage]
