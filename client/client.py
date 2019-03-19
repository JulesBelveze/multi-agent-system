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


def main(args):
    if args.level_name:
        msg_local(args.level_name)
        
    # Read server messages from stdin.
    server_messages = sys.stdin

    # Use stderr to print to console through server.
    msg_local("Poking starfish to life...")
    startfish_client = Client(server_messages)


if __name__ == "__main__":
    # Process arguments
    parser = ArgumentParser(description='Starfish client for solving transportation tasks.')
    parser.add_argument('--level', dest="level_name", help='Provide path to level to run client locally', metavar="FILE")

    args = parser.parse_args()

    # Run client
    main(args)
