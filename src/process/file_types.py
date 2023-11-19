import csv
from io import BytesIO
import json
import xml.etree.ElementTree as ET


def isCSV(input_raw: bytes) -> bool:
    """
    Determine if the given bytes represent a valid CSV format with
    at least two columns and more than one line.
    """
    
    sample_file = BytesIO(input_raw)

    try:
        reader = csv.reader(sample_file.read().decode().splitlines())
        header = next(reader)
        if len(header) < 2:
            return False
        
        next_line = next(reader)  
        if len(next_line) != len(header): 
            return False

    except:  
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
    except:
        return False

def isJPEG(input_raw: bytes) -> bool:
    """
    Determines if the given  bytes represents a valid JPEG file
    """
    SOI = b'\xff\xd8'
    EOI = b'\xff\xd9'
    if input_raw.startswith(SOI) and input_raw.endswith(EOI):
        return True
    
    return False


def isPDF(input_raw: bytes) -> bool:
    if input_raw.startswith("25504446"):
        return True
    return False    
# other matchers jpeg, xml, elf, pdf...

def isXML(input_raw: bytes) -> bool:
    """
    Check if the given bytes represent an XML file.

    :param data: bytes to check.
    :return: True if data is an XML file, False otherwise.
    """
    try:
        ET.fromstring(input_raw)
        return True
    except ET.ParseError:
        return False
    except Exception as e:
        # Handle other potential exceptions, e.g., encoding issues
        print(f"An error occurred: {e}")
        return False


def whichType(input):
    """
    Infer the file type of a given sample based on a series of matching functions.
    """
    
    def checkers():
        yield ("csv", isCSV)
        yield ("json", isJSON)
        # for later implementation
        yield ("xml", isXML)
        yield ("jpeg", isJPEG)
        # yield ("xml", xml_checker)
        # yield ("elf", elf_checker)
        yield ("pdf", isPDF)
        
    # default value set to 'plaintext' because all seeds end with '.txt'
    return next((filetype for filetype, matcher in checkers() if matcher(input)), 'plaintext')
