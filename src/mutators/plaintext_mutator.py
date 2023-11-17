from copy import deepcopy

from .mutator_base import MutatorBase
import random


class PLAINTEXT_Mutator(MutatorBase):
    """
        A fuzzer randomly generates inputs based on mutation of the seeds
        It implements python's generator
        
        Attributes:
            _content: lines of strings seperated by newline
    """

    def __init__(self, seed: bytes):
        """
        Args:
            seed: a line of string or strings seperated by newline
        """
        super().__init__()
        lines = seed.splitlines()
        self._content = [line for line in lines]
        self._header = lines[0]
        self.numLines = len(lines)
        self.badBytes = self.getBadBytes()

    # Append character padding
    def _mutate_add_chars1(self):
        return [item + b'A' * 5000 for item in self._content]

    def _mutate_add_chars2(self):
        # start from the second character
        return [self._content[0]] + [item + b'B' * 5000 for item in self._content[1:]]
        
    # Append null characters
    def _mutate_nulls1(self):
        return [item + b'0' * 5000 for item in self._content]

    def _mutate_nulls2(self):
        return [self._content[0]] + [item + b'0' * 5000 for item in self._content[1:]]

    # Append newlines
    def _mutate_newlines1(self):
        return [item + b'\n' * 5000 for item in self._content]

    def _mutate_newlines2(self):
        return [self._content[0]] + [item + b'\n' * 5000 for item in self._content[1:]] 

    # Append format string
    def _mutate_format_string1(self):
        return [item + b'%s' * 5000 for item in self._content] 

    def _mutate_format_string2(self):
        return [self._content[0]] + [item + b'%s' * 5000 for item in self._content[1:]]
 

    # Append ascii characters
    def _mutate_ascii1(self):
        return [item + b''.join(bytes(chr(count), encoding="utf-8") for count in range(128)) for item in self._content]

    def _mutate_ascii2(self):
        ascii_bytes = [bytes(chr(count), encoding="utf-8") for count in range(128)]
        return [self._content[0]] + [item + b''.join(ascii_bytes) for item in self._content[1:]]

    # Change seed to a large negative number
    def _mutate_large_negNum1(self):
        return [b'-99999999' for _ in self._content]

    def _mutate_large_negNum2(self):
        return [self._content[0]] + [b'-99999999' for _ in self._content[1:]]

    # same as negNum1 but with positive num
    def _mutate_large_num1(self):
        return [b'99999999' for _ in self._content]

    def _mutate_large_num2(self):
        return [self._content[0]] + [b'99999999' for _ in self._content[1:]]

    # # mutate into zero
    def _mutate_zero1(self):
        return [b'0' for _ in self._content]

    def _mutate_zero2(self):
        return [self._content[0]] + [b'0' for _ in self._content[1:]]

    def _mutate_null(self):
        return [b'\0' for _ in self._content] 

    def _mutate_test(self):
        return [item + b'\x04' for item in self._content] 

    # helper function
    def getBadBytes(self):
        l = [chr(count) for count in range(128) if count < 48 or count > 122]
        l += ["a", "%s", "-99999999", "99999999"]
        return l

    # mutate a random byte in a list of string
    def _mutate_randomChar(self):
        content = deepcopy(self._content)
        if content:
            pickLine = random.randint(0, len(content) - 1)
            if content[pickLine]:
                pickChar = random.randint(0, len(content[pickLine]) - 1)
                pickRandomChar = self.badBytes[random.randint(0, len(self.badBytes) - 1)]
                content[pickLine] = (
                    content[pickLine][:pickChar] +
                    bytes(pickRandomChar, encoding="utf-8") +
                    content[pickLine][pickChar + 1:]
                )
        return content


    def format_output(self, raw):
        # Construct the plaintext file body by joining rows with newline
        all_bytes = b'\n'.join(raw)

        # Generate a random non-null byte
        random_byte = random.randint(0x1, 0xff).to_bytes(1, 'little')

        # Replace null bytes with the random non-null byte
        return all_bytes.replace(b'\x00', random_byte) 