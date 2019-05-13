from __future__ import print_function
from argparse import ArgumentParser
import numpy as np
import sys
import smt

from agent import Agent
from state import State
from action import ActionType

from message import msg_server_err
from message import msg_server_comment
from message import msg_server_action


class Client:
    def __init__(self, server_args):
        #TODO: Consider adding input checks to verify level is correct, example: agent 0 not allowed to be red and green
        try:
            line = server_args.readline().rstrip()
            # catching level colors meta-data that are wrapped between #colors and #initial lines
            while line != "#colors":
                line = server_args.readline().rstrip()
            line = server_args.readline().rstrip()

            color_dict = {}
            while line != "#initial":
                color = line.split(":")[0]
                for i, char in enumerate(line.split(":")[1].split(",")):
                    color_dict[char.strip()] = color

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
                    if not self.initial_state.boxes.get(char):
                        self.initial_state.boxes[char] = []
                    self.initial_state.boxes[char].append((row, col, color_dict[char]))
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
                    if not self.goal_state.boxes.get(char):
                        self.goal_state.boxes[char] = []
                    self.goal_state.boxes[char].append((row, col, color_dict[char]))
                elif char not in "+ ":
                    msg_server_err("Error parsing goal level: unexepected character.")
                    sys.exit(1)

    def solve_level(self):
        # Create agents
        self.agents = []

        # need to be sorted because of the format of the joint actions the server can read
        for char in sorted(self.initial_state.agents.keys()):
            self.agents.append(Agent(self.initial_state, char))

        # Assign goal to agents
        solutions = []

        for char, values in self.goal_state.boxes.items():
            steps = []
            for value in values:
                # assigning goals to an agent for all boxes in a colour
                _, _, box_color = value
                key_agent = [x for x, y in self.initial_state.agents.items() if y[2] == box_color][0]
                key_agent = int(key_agent)

                self.agents[key_agent].assign_goal(self.goal_state, (char, values.index(value)))
                result = self.agents[key_agent].find_path_to_goal(self.walls)
                if result is not None or len(result) > 0:
                    steps.extend(result)
            solutions.append(steps)
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

        # adding NoOp action for agent that have already satisfied their goals
        nb_agents = len(solution)
        max_len_sol = max(len(x) for x in solution)
        for i in range(nb_agents):
            padding_state = State(solution[i][-1])
            padding_state.action = ActionType.NoOp
            solution[i] += [padding_state] * (max_len_sol - len(solution[i]))

        solution = zip(*solution)
        printer = ";".join(['{}'] * nb_agents)
        for state in solution:
            action = [agent.action for agent in state]
            msg_server_comment(printer.format(*action))
            msg_server_action(printer.format(*action))


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
