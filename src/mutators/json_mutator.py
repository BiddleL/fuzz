from .mutator_base import MutatorBase
from random import randint, choice

import json
import string

def helper_rand_obj(idx, obj_len, key_type):
    temp_obj = {}
    for i in range(idx):
        if key_type == "int":
            temp_obj[str(i)] = i
        elif key_type == "str":
            rand_str_len = randint(0, 50)
            temp_obj[str(i)] = ''.join(choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(rand_str_len))
    
    rand_key = str(randint(0, obj_len - 1))
    rand_value = json.dumps(temp_obj) * idx
    return rand_key, rand_value

class JSON_Mutator(MutatorBase):
    """
    Mutator that uses a provided sample JSON input to create and return altered inputs
    """

    def __init__(self, sample_input):
        """
        Initialise class
        sample_input: sample json input str read in from file, this is converted to json obj
        """
        super().__init__()
        self._input_json_obj = json.loads(sample_input)

    def format_output(self, output):
        """Methods already return in byte format"""
        return output

    def _mutate_json_obj_int(self):
        """
        Creates JSON inputs of various sizes and returns it as a byte array
        Returned JSON obj of key: str, value: int
        """
        mutated_json_obj = {}
        obj_len = 10
        for i in range(obj_len):
            rand_key, rand_value = helper_rand_obj(i, obj_len, "int")
            mutated_json_obj[rand_key] = rand_value
        
        replaced_slash_json_str = json.dumps(mutated_json_obj).replace('\\"', "\"")
        mutated_json_obj_input = bytearray(replaced_slash_json_str, "UTF-8")
        
        return mutated_json_obj_input
    
    def _mutate_json_obj_str(self):
        """
        Creates JSON inputs of various sizes and returns it as a byte array
        Returned JSON obj of key: str, value: str
        """
        mutated_json_obj = {}
        obj_len = 10
        for i in range(obj_len):
            rand_key, rand_value = helper_rand_obj(i, obj_len, "str")
            mutated_json_obj[rand_key] = rand_value
        
        replaced_slash_json_str = json.dumps(mutated_json_obj).replace('\\"', "\"")
        mutated_json_obj_input = bytearray(replaced_slash_json_str, "UTF-8")
        
        return mutated_json_obj_input
    
    def _mutate_json_obj_bits(self):
        """
        Mutates random bits in the sample input and returns mutated bits
        """
        json_str = json.dumps(self._input_json_obj)

        random_factor = 10

        for i in range(500):
            json_byte_array = bytearray(json_str, "UTF-8")
            for j in range(len(json_byte_array)):
                rand_n = randint(0, random_factor)
                if rand_n == 0:
                    json_byte_array[j] ^= randint(0, 200)

        
        return json_byte_array
