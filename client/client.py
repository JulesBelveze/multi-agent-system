import sys
import fileinput
import numpy as np
from argparse import ArgumentParser

from state import State

def msg_server(message):
    print(message, file=sys.stdout, flush=True)


def msg_error(message):
    print(message, file=sys.stderr, flush=True)


class Client:
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
            line = server_args.readline.rstrip()

            self.max_row = row + 1
            self.max_col = max_col + 1

            goal_level = []
            while line != "#end":
                goal_level.append(line)
                line = server_args.readline.rstrip()

        except Exception:
            sys.exit()

        # Find agents and subgoals
        '''#todo'''

        #create initial and goal state
        self.initial_state = State()
        self.goal_state = State()

        # update values of initial and goal states (boxes, agents)
        '''#todo'''

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
                    msg_error("Error: unexpected character.")
                    sys.exit(1)

        # looping through the goal level
        self.goal_level = {}  # goal level is a dictionary containing boxes informations
        for row, line in enumerate(goal_level):
            for col, char in enumerate(row):
                if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    self.goal_level[char] = (row, col, color_dict[char])
                elif char == "+" or char == " ":
                    continue
                else:
                    msg_error("Error: unexepected character in goal state.")
                    sys.exit(1)

    def solve_level(self, strategy):
        msg_error("Solving level...")
        strategy.add_to_frontier(self.initial_state)

        iterations = 0
        while True:
            if iterations == 1000:
                msg_error(strategy.search_status())
                iterations = 0

            if strategy.frontier_empty():
                return None

            leaf = strategy.get_and_remove_leaf()
            if leaf.is_goal_state(self.goal_level):
                return leaf.extract_plan()

            strategy.add_to_explored(leaf)
            for child_state in leaf.get_children(self.walls):
                if not strategy.is_explored(child_state) and not strategy.in_frontier(child_state):
                    strategy.add_to_frontier(child_state)

            iterations += 1


def main(args):
    msg_server("Starfish")

    # Read server messages from stdin.
    server_messages = sys.stdin

    # Create client using server messages
    starfish_client = Client(server_messages)

    strategy = None

    # Solve and print
    solution = starfish_client.solve_level(strategy)
    if solution is None:
        msg_error("{}".format(strategy.search_status()))
        msg_error("Unable to solve level.")

    else:
        msg_error("Found solution of length {}.".format(len(solution)))
        msg_error("{}".format(strategy.search_status()))

        # printing solution
        for state in solution:
            msg_error("{}".format(state.action))


if __name__ == "__main__":
    # Process arguments
    parser = ArgumentParser(description='Starfish client for solving transportation tasks.')

    args = parser.parse_args()

    # Run client
    main(args)
