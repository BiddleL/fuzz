from copy import deepcopy
from .mutator_base import MutatorBase
import random
import pwnlib.util.fiddling as bits



class CSV_Mutator(MutatorBase):
    """
    Fuzzer generates inputs by mutating seeds using a generator pattern.

    Attributes:
        _content: 2D array for csv cells.
        shape: Dimensions (rows x cols) of the csv.
    """


    def __init__(self, seed: bytes):
        super().__init__()
        lines = seed.splitlines()
        self._header = lines[0]
        self._content = [line.split(b',') for line in lines[1:]]
        self.shape = (len(self._content), len(self._header.split(b',')))

    def _select_random_cell(self):
        """
        Select and return a random cell's coordinates (row, col) from the content.

        Returns:
            tuple: (row, col) coordinates of the selected cell
        """
        all_rows = range(self.shape[0])
        all_cols = range(self.shape[1])

        row = random.choice(all_rows)
        col = random.choice(all_cols)

        return row, col

    def _mutate_replace_random_byte(self):
        """
        Mutate a byte in a random cell
        """
        mutated_content = deepcopy(self._content)
        row, col = self._select_random_cell()
        mutated_content[row][col] = self._alter_random_byte(mutated_content[row][col])
        return mutated_content

    def _mutate_insert_random_bytes(self):
        """
        Insert random bytes into a randomly selected cell.
        """
        mutated_content = deepcopy(self._content)
        row, col = self._select_random_cell()
        mutated_content[row][col] = self._insert_multiple_bytes(mutated_content[row][col])
    
        return mutated_content

    def _mutate_delete_random_byte(self):
        """
        Delete a byte from a random selected cell
        """
        mutated_content = deepcopy(self._content)
        row, col = self._select_random_cell()
        mutated_content[row][col] = self._delete_byte(mutated_content[row][col])
        return mutated_content

    # more fuzzing methods
    def _mutate_insert_multiple_rows(self):
        """attempt to overflow with large lines of input"""
        return [[
            random.randint(0, 0xFFFFFFFF).to_bytes(4, 'little')
            for _ in range(self.shape[1])
        ] for _ in range(4096)]

    def _convert_to_csv(self, raw):
        """Convert the raw data to CSV string."""
        return b'\n'.join(b','.join(row) for row in raw)

    def _replace_null_bytes(self, content):
        """Replace null bytes with random non-null bytes."""
        replacement_byte = random.randint(0x1, 0xff).to_bytes(1, 'little')
        return content.replace(b'\x00', replacement_byte)

    def _ensure_newline_ending(self, content):
        """Ensure the content ends with a newline."""
        return content if content.endswith(b'\n') else content + b'\n'
    
    def format_output(self, raw):
        """
        Construct a CSV file from the given raw data. 
    
        This function will first concatenate the header and the rows, then 
        replace any null bytes to avoid format issues, and finally ensure 
        that the resulting bytes end with a newline.
    
        Args:
            raw (List[bytes]): The raw data rows to be formatted into CSV.

        Returns:
            bytes: A well-formatted CSV in byte form.
        """

        csv_content = self._header + b'\n' + self._convert_to_csv(raw)
        formatted_content = self._replace_null_bytes(csv_content)
        
        return self._ensure_newline_ending(formatted_content)
