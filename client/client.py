import sys
from argparse import ArgumentParser

def msg_server(message):
    print(message, file=sys.stderr, flush=True)

def msg_local(message):
    print(message, file=sys.stdout, flush=True)

class Client:
    def __init__(self, server_args):
        msg_local(server_args)

    def solve_level(self):
        msg_local("Solving level...")

    def print_solution(self):
        msg_local("42")


def main(args):
    # Read server messages from stdin.
    server_messages = sys.stdin

    # Use stderr to print to console through server.
    msg_local("Poking starfish to life...")
    starfish = Client(server_messages)

    starfish.solve_level()
    starfish.print_solution()

if __name__ == "__main__":
    # Process arguments
    parser = ArgumentParser(description='Starfish client for solving transportation tasks.')

    args = parser.parse_args()

    # Run client
    main(args)
