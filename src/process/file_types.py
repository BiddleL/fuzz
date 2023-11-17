import csv
from io import BytesIO
import json

def isCSV(input_raw: bytes) -> bool:
    """
    Determine if the given bytes represent a valid CSV format with
    at least two columns and more than one line.
    """
    
    sample_file = BytesIO(input_raw)
    reader = csv.reader(sample_file.read().decode().splitlines())

    try:
        header = next(reader)
        if len(header) < 2:
            return False
        
        next_line = next(reader)  
        if len(next_line) != len(header): 
            return False

    except StopIteration:  
        return False

    return True


def isJSON(input_raw: bytes) -> bool:
    """
    Determine if the given bytes represent a valid JSON format 
    which is either a list or an object.
    """
    
    try:
        # Attempt to decode the bytes into a Python object
        parsed = json.loads(input_raw)
        return isinstance(parsed, (list, dict))
    except json.JSONDecodeError:
        return False


def isPDF(input_raw: bytes) -> bool:
    if input_raw.startswith("255044462d"):
        return True
    return False    
# other matchers jpeg, xml, elf, pdf...

def whichType(input):
    """
    Infer the file type of a given sample based on a series of matching functions.
    """
    
    def checkers():
        yield ("csv", isCSV)
        yield ("json", isJSON)
        # for later implementation
        # yield ("jpeg", jepg_checker)
        # yield ("xml", xml_checker)
        # yield ("elf", elf_checker)
        yield ("pdf", isPDF)
        
    # default value set to 'plaintext' because all seeds end with '.txt'
    return next((filetype for filetype, matcher in checkers() if matcher(input)), 'plaintext')
