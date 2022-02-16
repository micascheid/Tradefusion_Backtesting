from enum import Enum
class Strategy(Enum):
    KC = 1
    OTHER = 2

    def stratInput(self):
        if self.name == self.KC.name:
            print("you chose krown cross")
        if self.name == self.OTHER.name:
            print("you chose other")