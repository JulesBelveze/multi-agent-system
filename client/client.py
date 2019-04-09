from argparse import ArgumentParser
import fileinput
import io
import numpy as np
import sys
import smt

from agent import Agent
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

        #create initial and goal state
        self.initial_state = State()
        self.goal_state = State()

        self.walls = np.zeros((self.max_row, self.max_col), dtype=bool)

        # looping through the initial level
        for row, line in enumerate(level):
            for col, char in enumerate(row):
                # looking for walls
                if char == "+":
                    self.walls[row][col] = True
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
        for row, line in enumerate(goal_level):
            for col, char in enumerate(row):
                # looking for boxes
                if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    self.goal_state.boxes[char] = (row, col, color_dict[char])
                elif char == "+" or char == " ":
                    continue
                else:
                    msg_error("Error: unexepected character in goal state.")
                    sys.exit(1)

    def solve_level(self):
        # Create agents
        self.agents = []
        for char in self.initial_state.agents.keys():
            self.agents.append(Agent(self.initial_state, char))

        # Assign goal to agents
        '''#todo: this part needs extensive overhaul to account for several agents'''

        solutions = []
        for char in self.goal_state.boxes.keys():
            self.agents[0].assign_goal(self.initial_state, char)

            result = self.agents[0].find_path_to_goal(self.walls, self.goal_state)
            if result is None:
                return None
            solutions.append(result)

        return solutions


def main(args):
    msg_server("Starfish")

    # Read server messages from stdin.
    server_messages = sys.stdin

     #Testing
    if args.debug == True:
        levelname = "MAExample" 
        print("PYTHON DEBUG MODE: ACTIVATED\nDo not run together w/ java server\nLoading level through client...")
        print("Level name:", levelname)
        server_messages = smt.sim_load_lvl(levelname)
        print("Level loaded successfully!")
    
    # Create client using server messages
    starfish_client = Client(server_messages)

    # Solve and print
    solution = starfish_client.solve_level()
    if solution is None:
        msg_error("Unable to solve level.")

    else:
        msg_error("Found solution with {} steps.".format(len(solution)))

        # printing solution
        for steps in solution:
            for state in steps:
                msg_error("{}".format(state.action))


if __name__ == "__main__":
    # Process arguments
    parser = ArgumentParser(description='Starfish client for solving transportation tasks.')
    parser.add_argument('--debug', type=bool, default=False, help='Setting to true will allow to run client without server')
    
    args = parser.parse_args()

    # Run client
    main(args)
