from __future__ import print_function
from argparse import ArgumentParser
import numpy as np
import sys
import smt

from agent import Agent
from state import State

from message import msg_server_err
from message import msg_server_comment
from message import msg_server_action

class Client:
    def __init__(self, server_args):
        try:
            line = server_args.readline().rstrip()
            # catching level colors meta-data that are wrapped between #colors and #initial lines
            while line != "#colors":
                line = server_args.readline().rstrip()
            line = server_args.readline().rstrip()

            color_dict = {}
            while line != "#initial":
                color = line.split(":")[0]
                agent = line.split(":")[1].split(",")[0].strip()
                goal = line.split(":")[1].split(",")[1].strip()
                color_dict[agent] = color
                color_dict[goal] = color
                line = server_args.readline().rstrip()
            line = server_args.readline().rstrip()

            level = []
            row, max_col = 0, 0
            while line != "#goal":
                nb_col = len(line)
                if nb_col > max_col:
                    max_col = nb_col

                level.append(line)
                row += 1
                line = server_args.readline().rstrip()
            line = server_args.readline().rstrip()

            self.max_row = row
            self.max_col = max_col

            goal_level = []
            while line != "#end":
                goal_level.append(line)
                line = server_args.readline().rstrip()

        except:
            msg = "{}\n{}: {}".format("THERE WAS AN EXCEPTION LOL:", sys.exc_info()[0], sys.exc_info()[1])
            msg_server_err(msg)
            sys.exit()

        # create initial and goal state
        self.initial_state = State()
        self.goal_state = State()

        self.walls = np.zeros((self.max_row, self.max_col), dtype=bool)

        # looping through the initial level
        for row, line in enumerate(level):
            for col, char in enumerate(line):
                # looking for walls
                if char == "+":
                    self.walls[row][col] = True
                # looking for boxes
                elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    self.initial_state.boxes[char] = (row, col, color_dict[char])
                # looking for agents
                elif char in "0123456789":
                    self.initial_state.agents[char] = (row, col, color_dict[char])
                elif char not in " ":
                    msg_server_err("Error parsing initial level: unexpected character.")
                    sys.exit(1)

        # looping through the goal level
        for row, line in enumerate(goal_level):
            for col, char in enumerate(line):
                # looking for boxes
                if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    self.goal_state.boxes[char] = (row, col, color_dict[char])
                elif char not in "+ ":
                    msg_server_err("Error parsing goal level: unexepected character.")
                    sys.exit(1)

    def solve_level(self):
        # Create agents
        self.agents = []
        for char in self.initial_state.agents.keys():
            self.agents.append(Agent(self.initial_state, char))

        # Assign goal to agents
        # TODO: this part needs extensive overhaul to account for several agents

        solutions = []
        for char in self.goal_state.boxes.keys():
            self.agents[0].assign_goal(self.goal_state, char)

            result = self.agents[0].find_path_to_goal(self.walls)
            if result is None:
                return None
            solutions.append(result)

        return solutions


def main(args):
    level_data = None

    if args.debug == True:
        level_name = args.levelName
        print("PYTHON DEBUG MODE: ACTIVATED\nDo not run together w/ java server")
        print("Loading level:", level_name)

        level_data = smt.sim_load_lvl(level_name)
        if level_data is None:
            print("Failed to load level. Quitting...")
            return

        print("Level loaded successfully!")
    else:
        # Read server messages from stdin.
        msg_server_action("Starfish")
        level_data = sys.stdin

    # Create client using server messages
    starfish_client = Client(level_data)

    # Solve and print
    solution = starfish_client.solve_level()
    if solution is None:
        msg_server_err("Unable to solve level.")
    else:
        msg_server_comment("Found {} solution(s)".format(len(solution)))

        # printing solution
        for steps in solution:
            msg_server_comment("New solution:")
            for state in steps:
                msg_server_action("{}".format(state.action))


if __name__ == "__main__":
    # Process arguments
    parser = ArgumentParser(description='Starfish client for solving transportation tasks.')
    parser.add_argument('--debug', type=bool, default=False,
                        help='Setting to true will allow to run client without server')
    parser.add_argument('--levelName', default='MA_example',
                        help='Provide the name of a level for client to run (requires debug arg)')

    args = parser.parse_args()

    # Run client
    main(args)
