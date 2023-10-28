import subprocess
from typing import Tuple, Iterator
from file_types import whichType
import pwn
import mutators

FUZZERS_BY_TYPE = {
    "csv": mutators.CsvMutator,
    "json": mutators.JSONMutator,
}

EXITCODES = {
    1: "SIGHUP",
    2: "SIGINT",
    3: "SIGQUIT",
    4: "SIGILL",
    5: "SIGTRAP",
    6: "SIGABRT",
    7: "SIGBUS",
    8: "SIGFPE",
    9: "SIGKILL",
    10: "SIGUSR1",
    11: "SIGEGV (Segmentation fault)",
    12: "SIGUSR2",
    13: "SIGPIPE",
    14: "SIGALRM",
    15: "SIGTERM",
    16: "SIGSTKFLT",
    17: "SIGCHLD",
    18: "SIGCONT",
    19: "SIGSTOP",
    20: "SIGTSTP",
    21: "SIGTTIN",
    22: "SIGTTOU",
    23: "SIGURG",
    24: "SIGXCPU",
    25: "SIGXFSZ",
    26: "SIGVTALRM",
    27: "SIGPROF",
    28: "SIGWINCH",
    29: "SIGIO",
    30: "SIGPWR",
    31: "SIGSYS",
}

class Harness(object):

    def __init__(self, binary, seed):
        self._binary_path = self._format_binary_path(binary)
        self._current_checkpoint = 0
        seed_content = self._read_file(seed)
        file_type = whichType(seed_content)
        pwn.log.info(f"File type detected: '{file_type}'")

        self._binary_process = self._init_process()
        self._fuzzer = FUZZERS_BY_TYPE[file_type](seed_content)

    def _format_binary_path(self, binary: str) -> str:
        """Ensure the binary path is correctly formatted."""
        return binary if '/' in binary else f'./{binary}'

    @staticmethod
    def _read_file(file_path: str) -> bytes:
        """Read and return content of a file."""
        with open(file_path, 'rb') as f:
            return f.read()

    def _init_process(self):
        """Initialize a subprocess for the binary."""
        return subprocess.Popen(
            self._binary_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def _reset(self):
        """Reinitialize the subprocess for the binary."""
        self._binary_process = self._init_process()

    def _process_input(self, input_bytes: bytes) -> Tuple[bytes, bytes, int]:
        """Send input to the binary process and return output, error, and exit code."""
        outs, err = self._binary_process.communicate(input_bytes, timeout=0.5)
        return outs, err, self._binary_process.returncode

    def _log_result(self, idx: int, name: str, input_bytes: bytes, outs: bytes, err: bytes, exitcode: int):
        """Print and log the result of the processing."""
        status = 'PASSED' if exitcode >= 0 else 'CRASHED'
        print(f"{idx+1} {status} | exitcode: {exitcode}")
        print(f"\t{'method:':<12}{name}")
        print(f"\t{'input_length:':<12}{len(input_bytes)}")
        print("=" * 50)

    def start(self, n_runs=500):
        txt_name = self._binary_path.split('/')[-1].split('.')[0]
        for idx, (input_bytes, name) in enumerate(self._fuzzer, 1):
            if idx > n_runs:
                break
            try:
                outs, err, exitcode = self._process_input(input_bytes)
                self._log_result(idx, name, input_bytes, outs, err, exitcode)

                if exitcode < 0:  # Handle SIGFAULT
                    print(f"Program Crashed: exitcode = {exitcode}")
                    print(f"\tReason: {EXITCODES[-exitcode]}")
                    print(f"Dumped badinput to /tmp/{txt_name}_crashed.txt")
                    with open(f'/tmp/{txt_name}_crash.txt', 'wb') as f:
                        f.write(input_bytes)
                    break
            except subprocess.TimeoutExpired:
                print(f"{idx}: Timeout")
                print(f"Dumped timeout report to /tmp/{txt_name}_timeout.txt")
                with open(f'/tmp/{txt_name}_timeout.txt', 'wb') as f:
                    f.write(input_bytes)
                break
            self._reset()

