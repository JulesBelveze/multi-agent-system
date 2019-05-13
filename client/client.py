from __future__ import print_function
from argparse import ArgumentParser
from copy import deepcopy
import numpy as np
import sys
import smt

from agent import Agent
from state import State
from action import Action
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
                    msg_server_err("Error parsing goal level: unexpected character.")
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


def get_box_key_by_position(row, col, state: 'State'):
    '''Return the key of a box at a given position'''
    msg_server_comment("row: {} / col: {}".format(row, col))
    msg_server_comment(state.boxes)
    # msg_server_comment([key for key, value in state.boxes.items() if (value[0], value[1]) == (row, col)])
    return [key for key, value in state.boxes.items() if (value[0], value[1]) == (row, col)][0]


def check_action(actions, current_state: 'State', walls):
    '''Check if every agent's action is applicable in the current state and returns
    a list with the index of the agents' whose action are not applicable'''
    next_state = State(current_state)
    index_non_applicable = []
    is_applicable = True

    for i, action in enumerate(actions):
        i = str(i)
        row, col, color = current_state.agents[i]
        if action.action_type is ActionType.NoOp:
            continue
        else:
            new_agent_row = row + action.agent_dir.d_row
            new_agent_col = col + action.agent_dir.d_col

            if action.action_type is ActionType.Move:
                if current_state.is_free(walls, new_agent_row, new_agent_col):
                    next_state.agents[i] = new_agent_row, new_agent_col, color
                else:
                    index_non_applicable.append(i)
                    is_applicable = False
            elif action.action_type is ActionType.Push:
                box_key = get_box_key_by_position(new_agent_row, new_agent_col, current_state)
                new_box_row = new_agent_row + action.box_dir.d_row
                new_box_col = new_agent_col + action.box_dir.d_col
                if current_state.is_free(walls, new_box_row, new_box_col):
                    next_state.agents[i] = (new_agent_row, new_agent_col, color)
                    next_state.boxes[box_key] = (new_box_row, new_box_col, color)
                else:
                    index_non_applicable.append(i)
                    is_applicable = False
            elif action.action_type is ActionType.Pull:
                box_key = get_box_key_by_position(new_agent_row, new_agent_col, current_state)
                new_box_row = row + action.box_dir.d_row
                new_box_col = col + action.box_dir.d_col
                if current_state.is_free(walls, new_agent_row, new_agent_col):
                    next_state.agents[i] = (new_agent_row, new_agent_col, color)
                    next_state.boxes[box_key] = (new_box_row, new_box_col, color)
                else:
                    index_non_applicable.append(i)
                    is_applicable = False

    return index_non_applicable, next_state, is_applicable


def add_padding_actions(solution, nb_agents):
    '''adding NoOp action for agent that have already satisfied their goals'''
    max_len_sol = max(len(x) for x in solution)
    for i in range(nb_agents):
        padding_state = State(solution[i][-1])
        padding_state.action = ActionType.NoOp
        solution[i] += [padding_state] * (max_len_sol - len(solution[i]))

    return solution


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
    solution = starfish_client.solve_level()
    if solution is None:
        msg_server_err("Unable to solve level.")
    else:
        msg_server_comment("Found {} solution(s)".format(len(solution)))

        nb_agents = len(solution)
        solution = add_padding_actions(solution, nb_agents)

        # create the joint actions
        printer = ";".join(['{}'] * nb_agents)
        msg_server_comment(len(solution[0]))
        for i in range(len(solution[0])):
            state = [elt[i] for elt in solution]

            action = [agent.action for agent in state]
            msg_server_comment(action)
            index_non_applicable, current_state, is_applicable = check_action(action, current_state, walls)
            msg_server_comment(printer.format(*action) + " - applicable: {}".format(is_applicable))

            if not is_applicable:
                for key_agent in index_non_applicable:
                    action[int(key_agent)] = ActionType.NoOp

                new_solution = []
                for i, agent in enumerate(starfish_client.agents):
                    box_key = starfish_client.agents[i].box_key
                    starfish_client.agents[i] = Agent(current_state, agent.agent_key)
                    starfish_client.agents[i].assign_goal(starfish_client.goal_state, box_key)
                    new_solution.append(starfish_client.agents[i].find_path_to_goal(walls))

                msg_server_comment(new_solution)
                sys.exit()
                # new_solution = starfish_client.solve_level()

                sys.exit()
                new_solution = add_padding_actions(new_solution, nb_agents)

                hack_state = current_state
                hack_state.action = Action(ActionType.NoOp, None, None)

                for i in range(len(solution)):
                    solution[i] = [hack_state] * len(solution[i])
                    solution[i].append(new_solution[i])

                msg_server_comment("HEYYYYY: {}".format(len(solution[0])))
                msg_server_comment("Switching to action: " + printer.format(*action))

            msg_server_action(printer.format(*action))

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
