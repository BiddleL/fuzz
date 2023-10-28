from argparse import ArgumentParser
from harness import Harness

def main(binary, seed, times: int = 5000):
    """
    Initialize a harness with the given binary and seed, and then start it with a specified timeout.
    """
    runner = Harness(binary, seed)
    runner.start(times) 
    
if __name__ == "__main__":
    parser = ArgumentParser(description="A simple fuzzer")
    parser.add_argument("binary", help="Path to the binary to be fuzzing tested")
    parser.add_argument("seed", help="Seed value to be mutated")
    parser.add_argument("--times", type=int, default=5000, help="Maximum testing times for the runner. Defaults to 5000.")
    
    args = parser.parse_args()
    main(args.binary, args.seed, args.times)
