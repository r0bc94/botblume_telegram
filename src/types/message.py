from dataclasses import dataclass

@dataclass
class Message():
  sensorNumber: int
  aggregatedValue: int
  rawValue: int
  requested: bool
