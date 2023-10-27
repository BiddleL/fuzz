from type import Type

class CSVFuzz(Type):
    def __init__(self, inputStr):
        super().__init__(inputStr)
        self.lines = self.inputStr.split("\n")
        self.values = self.lines[0].count(",") + 1

    def isType(self):
        num_rows = self.inputStr.count('\n')
        num_cols = self.values
        total_entries = self.inputStr.count(',')

        
        if ((num_rows + 1) * num_cols == total_entries):
            if (num_rows > 1):
                return True
            
        return False

