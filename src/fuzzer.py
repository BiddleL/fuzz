#!/usr/bin/python3

from argparse import ArgumentParser
import sys
from process import Manager

def main(binary, seed, times: int = 5000):
    """
    Initialize a harness with the given binary and seed, and then start it with a specified timeout.
    """
    runner = Manager(binary, seed, times)
    runner.run() 
    
if __name__ == "__main__":
    if len(sys.arv) != 3:
        print("Usage: ./fuzzer program sampleinput.txt")
        sys.exit()

    
    parser = ArgumentParser(description="A simple fuzzer")
    parser.add_argument("binary", help="Path to the binary to be fuzzing tested")
    parser.add_argument("seed", help="Seed value to be mutated")
    parser.add_argument("--times", type=int, default=5000, help="Maximum testing times for the runner. Defaults to 5000.")
    
    args = parser.parse_args()
    main(args.binary, args.seed, args.times)

