import sys
import numpy as np

from argparse import ArgumentParser


def msg_server(message):
    print("{}".format(message), file=sys.stderr, flush=True)


def msg_local(message):
    print("{}".format(message), file=sys.stderr, flush=True)


class SearchClient:
    def __init__(self, server_args):
        try:
            line = server_args.readline().rstrip()

            # catching level colors meta-data that are wrapped between #colors and #initial lines
            while line != "#colors":
                line = server_args.readline.rstrip()
            line = server_args.readline.rstrip()

            color_dict = {}
            while line != "#inital":
                color = line.split(":")[0]
                agent = line.split(":")[1].split(",")[0].strip()
                goal = line.split(":")[1].split(",")[1].strip()
                color_dict[agent] = color
                color_dict[goal] = color
                line = server_args.readline.rstrip()
            line = server_args.readline.rstrip()

            level = []
            row, max_col = 0, 0
            while line != "#goal":
                nb_col = len(line)
                if nb_col > max_col:
                    max_col = nb_col

                level.append(line)
                row += 1
                line = server_args.readline.rstrip()

            self.max_row = row + 1
            self.max_col = max_col + 1

        except Exception:
            sys.exit()

        self.initial_state = State() # TO BE CREATED
        self.walls = np.zeros((self.max_row, self.max_col), dtype=bool)
        self.goals = np.zeros((self.max_row, self.max_col), dtype=bool)

        # looping through the level
        for row, line in enumerate(level):
            for col, char in enumerate(row):
                # looking for walls
                if char == "+":
                    self.walls[row][col] = True
                # looking for goal cells
                elif char in "abcdefghijklmnopqrstuvwxyz":
                    self.goals[row][col] = True
                # looking for boxes
                elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    self.initial_state.boxes[char] = (row, col, color_dict[char])
                # looking for agents
                elif char in "0123456789":
                    self.initial_state.agents[char] = (row, col, color_dict[char])
                # looking for empty cell
                elif char == " ":
                    continue
                else:
                    msg_local("Error: unexpected character.")


    def solve_level(self):
        msg_local("Solving level...")

    def print_solution(self):
        msg_local("42")


def main(args):
    # Read server messages from stdin.
    server_messages = sys.stdin

    # Use stderr to print to console through server.
    msg_local("Poking starfish to life...")
    starfish = SearchClient(server_messages)

    starfish.solve_level()
    starfish.print_solution()


if __name__ == "__main__":
    # Process arguments
    parser = ArgumentParser(description='Starfish client for solving transportation tasks.')

    args = parser.parse_args()

    # Run client
    main(args)
