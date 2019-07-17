from __future__ import print_function
from argparse import ArgumentParser
from copy import deepcopy
import numpy as np
import random
import sys
import smt

from agent import Agent
from state import State
from action import Action
from action import ActionType
from conflict import Conflict

from message import msg_server_err
from message import msg_server_comment
from message import msg_server_action

from action import Direction
from client_functions import add_padding_actions, get_box_key_by_position, check_action, missing_goals, getLen, \
    reassign_goals, isListEmpty


class Client:
    def __init__(self, server_args):
        # TODO: Consider adding input checks to verify level is correct, example: agent 0 not allowed to be red and green
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
                    msg_server_err(
                        "Error parsing initial level: unexpected character: {}({},{})".format(char, row, col))
                    sys.exit(1)

        # looping through the goal level
        for row, line in enumerate(goal_level):
            for col, char in enumerate(line):
                # looking for boxes
                if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    if not self.goal_state.boxes.get(char):
                        self.goal_state.boxes[char] = []
                    self.goal_state.boxes[char].append((row, col, color_dict[char]))
                # looking for agents
                elif char in "0123456789":
                    self.goal_state.agents[char] = (row, col, color_dict[char])
                elif char not in "+ ":
                    msg_server_err("Error parsing goal level: unexpected character: {}({},{})".format(char, row, col))
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

                # catch exception for box without agent of the same color
                try:
                    key_agent = [x for x, y in self.initial_state.agents.items() if y[2] == box_color][0]
                    key_agent = int(key_agent)

                    # assigning a goal to the agent if he doesn't have any
                    if self.agents[key_agent].has_goal():
                        msg_server_comment("Agent {} has already a goal".format(key_agent))
                    else:
                        self.agents[key_agent].assign_goal(self.goal_state, (char, values.index(value)))
                        result = self.agents[key_agent].find_path_to_goal(self.walls)
                        if result is not None and len(result) > 0:
                            steps.extend(result)
                        solutions.append(steps)
                except IndexError:
                    continue

        # handling the fact that some agents might have no goal by adding an empty
        # list to their corresponding position that will be padded with NoOp actions
        if len(solutions) != len(self.agents):
            for i, agent in enumerate(self.agents):
                if not agent.has_goal():
                    solutions.insert(i, [])

        return solutions


def main(args):
    level_data = None

    if args.debugLevel is not None:
        level_name = args.debugLevel
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
    current_state = deepcopy(starfish_client.initial_state)
    walls = starfish_client.walls

    # Solve and print
    # TODO: configuration when an agent is blocking all the others
    solution = starfish_client.solve_level()
    if sum([len(sol) for sol in solution]) == 0:
        for i, agent in enumerate(starfish_client.agents):
            if not agent.has_goal():
                random_direct = random.choice([Direction.N, Direction.E, Direction.W, Direction.S])
                move = State(current_state)
                move.action = Action(ActionType.Move, random_direct, None)
                solution[i] = [move]
    else:
        msg_server_comment("Found {} solution(s)".format(len(solution)))

    nb_agents = len(solution)
    printer = ";".join(['{}'] * nb_agents)

    while not isListEmpty(solution):
        for i, elt in enumerate(solution):
            if len(elt) == 0:
                padding_state = current_state
                solution[i].append(padding_state)
                solution[i][-1].action = Action(ActionType.NoOp, None, None)

        # grabbing state for each agent
        state = [elt[0] for elt in solution]

        action = [agent.action for agent in state]
        index_non_applicable, current_state, is_applicable = check_action(action, current_state, walls)
        msg_server_comment(printer.format(*action) + " - applicable: {}".format(is_applicable))

        # if there is a conflict between agents then we solve it
        if not is_applicable:
            len_paths_to_goal = [len(path) for path in solution]
            conflict = Conflict(current_state, index_non_applicable, action, len_paths_to_goal)
            conflict.solve_conflicts()

        msg_server_action(printer.format(*action))

        for i, elt in enumerate(solution):
            elt.pop(0)

        response = level_data.readline().rstrip()
        if 'false' in response:
            msg_server_err("Server answered with error to the action " + printer.format(*action))


if __name__ == "__main__":
    # Process arguments
    parser = ArgumentParser(description='Starfish client for solving transportation tasks.')
    parser.add_argument('--debugLevel', default=None,
                        help='Provide the name of a level for client to run in debug mode')

    args = parser.parse_args()

    # Run client
    main(args)
