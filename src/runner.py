import subprocess
import sys
from typing import Tuple, Iterator

import mutators
import process

class Manager:

    _MUTATORS = {
        "csv" : mutators.CSV_Mutator,
        "json" : mutators.JSON_Mutator,
        "plaintext": mutators.PLAINTEXT_Mutator,
        "xml": mutators.XML_Mutator
    }
    
    def __init__(self, binary, seed, times: int = 5000):
        self._num_runs = times
        self._current_checkpoint = 0
        
        if "./"  != binary[1:2]:
            self._process_name = f"./{binary}"
        else:
            self._process_name = f"{binary}"
        
        self._stop_flag = False
        
        try:
            self._input_file = self._read_file(seed)

        except OSError:
            print(f"Couldn't open input file: {seed}")
            sys.exit()


        self._file_type = process.whichType(self._input_file)
        self._fuzz = self._MUTATORS[self._file_type](self._input_file)
        self._init_process()


    def _format_binary_path(self, binary: str) -> str:
        """Ensure the binary path is correctly formatted."""
        return binary if '/' in binary else f'./{binary}'

    @staticmethod
    def _read_file(file_path: str) -> bytes:
        """Read and return content of a file."""
        with open(file_path, 'rb') as f:
            return f.read()

    @staticmethod
    def _read_file(file_path: str) -> bytes:
        """Read and return content of a file."""
        with open(file_path, 'rb') as f:
            return f.read()

    def _init_process(self):
        self._process = subprocess.Popen(
            self._process_name,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def _reset(self):
        self._init_process()

    def _log_result(self, idx: int, name: str, input_bytes: bytes, outs: bytes, err: bytes, exitcode: int):
        """Print and log the result of the processing."""
        status = 'PASSED' if exitcode >= 0 else 'CRASHED'
        print(f"{idx+1} {status} | exitcode: {exitcode}")
        print(f"\t{'method:':<12}{name}")
        print(f"\t{'input_length:':<12}{len(input_bytes)}")
        print("=" * 50)

    def _result_dump(self, input):
        with open(f"{self._txt_name}_dump.txt", "wb") as fp:
            fp.write(input)
            fp.close()
    
    def _process_input(self, input_bytes: bytes) -> Tuple[bytes, bytes, int]:
        """Send input to the binary process and return output, error, and exit code."""
        outs, err = self._process.communicate(input_bytes, timeout=0.5)
        return outs, err, self._process.returncode
    
    def run(self):
        self._txt_name = self._process_name.split('/')[-1].split('.')[0]
        for idx, (input_bytes, name) in enumerate(self._fuzz, 1):
            if idx > self._num_runs:
                break
            try:
                outs, err, exitcode = self._process_input(input_bytes)
                self._log_result(idx, name, input_bytes, outs, err, exitcode)

                if exitcode < 0:  # Handle SIGFAULT
                    print(f"Program Crashed: exitcode = {exitcode}")
                    print(f"\tReason: {process.ExitCodes(-exitcode).name}")
                    print(f"Dumped badinput to {self._txt_name}_dump.txt")

                    self._result_dump(input_bytes)
                    break
            except subprocess.TimeoutExpired:
                print(f"{idx}: Timeout")
                print(f"Dumped timeout report to {self._txt_name}_dump.txt")
                self._result_dump(input_bytes)
                break        
            self._reset()
        

    



    
        
        