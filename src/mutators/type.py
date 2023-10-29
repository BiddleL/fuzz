class Type:
    def __init__(self, inputStr):
            self.inputStr = inputStr

    # Returns if the inputStr can be parsed
    def isType(self) -> bool:
        return True
    
    def fuzz(self, mutation):
        return True;

