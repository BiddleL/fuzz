import random
from typing import Optional

class MutatorBase:
    """
    Base class for all Mutators. Provides mutation methods at the byte/bit level.
    Implements a generator pattern to yield mutated output derived from a seed.
    
    For custom mutators:
    - Override `__init__` if needed.
    - Implement the `format_output` method.
    - Add new mutator methods starting with `_mutate_`.
    """

    def __init__(self):
        """
        Constructor. Initializes _mutate_methods.
        """
        self._mutate_methods = [
            getattr(self, name) for name in dir(self) if self.is_mutate_method(name)
        ] 

    @staticmethod
    def is_mutate_method(name: str) -> bool:
        """
        Checks if a given method name is a mutation method.
        
        Args:
            name (str): The method name.
            
        Returns:
            bool: True if it is a mutation method, False otherwise.
        """
        return name.startswith("_mutate_")

    def __iter__(self):
        return self

    def __next__(self) -> bytes:
        """
        Generates mutated inputs. It uses self._mutate_methods and then formats the output.
        
        Returns:
            bytes: The mutated input.
        """
        choice = random.choice(self._mutate_methods)
        new_content = choice()
        return self.format_output(new_content), choice.__name__[8:]
    
    @classmethod
    def _alter_random_byte(cls, sample: bytes) -> bytes:
        """
        Replacing a byte in sample with a random value
        Args:
            sample (bytes): bytes to be mutated

        Returns:
            mutated bytes
        """
        byte_list = list(sample)
        pos = random.randrange(len(byte_list))
        byte_list[pos] = random.randrange(256)
        return bytes(byte_list)


    @staticmethod
    def _pick_magic_value(magic_ints: dict) -> tuple:
        size = random.choice(list(magic_ints.keys()))
        value = random.choice(magic_ints[size])
        return size, value

    @classmethod
    def _delete_byte(cls, sample: bytes) -> bytes:
        """
        remove a byte in sample bytes
        Args:
            sample: bytes to be mutated

        Returns:
            mutated bytes
        """
        sample_array = bytearray(sample)
        del sample_array[random.randrange(len(sample_array))]
        return bytes(sample_array)

    @classmethod
    def _insert_multiple_bytes(cls,
                               sample: bytes,
                               n_bytes: Optional[int] = None,
                               pos: Optional[int] = None) -> bytes:
        """
        Inserts `n_bytes` random bytes into `sample` at `pos`.
        Warning: Performance slows with large `n_bytes`.

        Args:
            sample (bytes): Target for mutation.
            n_bytes (int): Number of bytes to insert.
            pos (int, optional): Insertion index. Default: None.

        Returns:
            bytes: Mutated sample.
        """

        n_bytes = n_bytes or random.randint(1, 0xFFFF)
        pos = pos or random.randint(0, len(sample))

        new_bytes = bytes(random.randint(0, 0xFF) for _ in range(n_bytes))
    
        return sample[:pos] + new_bytes + sample[pos:]


    def format_output(self, mutable_content: bytes) -> bytes:
        """
        formats the output, this method will be called before generating the mutated file

        Subtypes must override this method
        """
        raise NotImplementedError(
            "format_output(mutable_content: bytes) -> bytes not implemented")
