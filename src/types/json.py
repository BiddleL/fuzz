import json

from type import Type

class JSONFuzz(Type):
    def __init__(self, inputStr):
        super().__init__(inputStr)

        try:
            self.obj = json.loads(self.inputStr)
        except:
            self.obj = {}

    def isType(self) -> bool:
        try:
            json.loads(self.inputStr)
        except:
            return False
        
        return True