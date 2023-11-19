from .mutator_base import MutatorBase
import random
from copy import deepcopy

class PDF_Mutator(MutatorBase):
    """
    Mutator that uses a provided sample PDF input to create and return altered inputs
    """

    def __init__(self, sample_input):
        """
        Initialise class
        """
        super().__init__()

    def format_output(self, output):
        """Methods already return in byte format"""
        return output

#PDF Specific
    def _mutate_pdf_specific_chars(self):
        """
        Mutates pdf bytes with specific char set
        """
        char_set = {b'%', b'(', b')', b'<', b'>', b'/'}
        byte_list = list(self)
        pos = random.randrange(len(byte_list))
        byte_list[pos] = random.choice(char_set)
        return bytes(byte_list)
    
    def _mutate_pdf_remove_eof(self):
        """
        Removes eof
        """
        mutated = self[0: -4]
        return mutated
    
    def _mutate_pdf_alter_version(self):
        """
        Alters stated pdf version
        """
        mutated = self
        mutated[7] = random.randint(0, 9)
        return mutated

#Generic
    def _mutate_pdf_bytes(self):
        """
        Mutates pdf bytes randomly
        """
        mutated_content = self._alter_random_byte(mutated_content)
        return mutated_content
    
    def _mutate_pdf_delete_bytes(self):
        """
        Deletes pdf bytes randomly
        """
        mutated_content = self._delete_byte(mutated_content)
        return mutated_content
    
    def _mutate_pdf_insert_bytes(self):
        """
        Inserts random bytes into PDF
        """
        for i in range(100):
            mutated_content = self._insert_multiple_bytes(mutated_content, i)
        return mutated_content
