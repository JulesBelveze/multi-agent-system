import sys
import fileinput
from argparse import ArgumentParser

def msg_server(message):
    print(message, file=sys.stdout, flush=True)

def msg_error(message):
    print(message, file=sys.stderr, flush=True)

class Client:
    def __init__(self, server_messages):
        data = []
        try:
            line = server_messages.readline().rstrip()

            while line:
                if "#end" in line:
                    break

                data.append(line)
                line = server_messages.readline().rstrip()

            # DEBUG: Print input into file
            file = open("output.txt","w")
            for i in data:
                file.write(i)
                file.write("\n")
            file.close()
            # /DEBUG

            self.domain = data[1]
            self.level_name = data[3]
            
            #todo: add colours, initial and goal vars

        except Exception as ex:
            print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
            file.close()
            sys.exit(1)

    def solve_level(self):
        msg_error("Solving level...")

    def print_solution(self):
        msg_error("42")

def main(args):
    msg_server("Starfish")
    
    # Read server messages from stdin.
    server_messages = sys.stdin

    # Create client using server messages
    starfish_client = Client(server_messages)
    
    # Solve and print
    starfish_client.solve_level()
    starfish_client.print_solution()

if __name__ == "__main__":
    # Process arguments
    parser = ArgumentParser(description='Starfish client for solving transportation tasks.')

    args = parser.parse_args()

    # Run client
    main(args)
