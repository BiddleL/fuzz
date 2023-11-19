from .mutator_base import MutatorBase
import random

class PDF_Mutator(MutatorBase):
    """
    Mutator that uses a provided sample PDF input to create and return altered inputs
    """

    def __init__(self, sample_input):
        """
        Initialise class
        sample_input: sample pdf input str read in from file, this is converted to pdf obj
        """
        super().__init__()
        self._input_pdf_obj = pdf.loads(sample_input)

    def format_output(self, output):
        """Methods already return in byte format"""
        return output

    def _mutate_pdf_obj_int(self):
        """
        Creates PDF inputs of various sizes and returns it as a byte array
        Returned PDF obj of key: str, value: int
        """
        mutated_pdf_obj = {}
        obj_len = 10
        for i in range(obj_len):
            rand_key, rand_value = helper_rand_obj(i, obj_len, "int")
            mutated_pdf_obj[rand_key] = rand_value
        
        replaced_slash_pdf_str = pdf.dumps(mutated_pdf_obj).replace('\\"', "\"")
        mutated_pdf_obj_input = bytearray(replaced_slash_pdf_str, "UTF-8")
        
        return mutated_pdf_obj_input
    
    def _mutate_pdf_obj_str(self):
        """
        Creates PDF inputs of various sizes and returns it as a byte array
        Returned PDF obj of key: str, value: str
        """
        mutated_pdf_obj = {}
        obj_len = 10
        for i in range(obj_len):
            rand_key, rand_value = helper_rand_obj(i, obj_len, "str")
            mutated_pdf_obj[rand_key] = rand_value
        
        replaced_slash_pdf_str = pdf.dumps(mutated_pdf_obj).replace('\\"', "\"")
        mutated_pdf_obj_input = bytearray(replaced_slash_pdf_str, "UTF-8")
        
        return mutated_pdf_obj_input
    
    def _mutate_pdf_obj_bits(self):
        """
        Mutates random bits in the sample input and returns mutated bits
        """
        pdf_str = pdf.dumps(self._input_pdf_obj)

        random_factor = 10

        for i in range(500):
            pdf_byte_array = bytearray(pdf_str, "UTF-8")
            for j in range(len(pdf_byte_array)):
                rand_n = randint(0, random_factor)
                if rand_n == 0:
                    pdf_byte_array[j] ^= randint(0, 200)

        
        return pdf_byte_array