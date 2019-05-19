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
                if self.agents[key_agent].has_goal():
                    print("AGENT HAS ALREADY A GOAL")
                else:
                    self.agents[key_agent].assign_goal(self.goal_state, (char, values.index(value)))
                    result = self.agents[key_agent].find_path_to_goal(self.walls)
                    if result is not None and len(result) > 0:
                        steps.extend(result)
                    solutions.append(steps)

        return solutions


def get_box_key_by_position(row, col, state: 'State'):
    '''Return the key of a box at a given position'''
    # msg_server_comment(state.boxes)
    for key, boxes in state.boxes.items():
        for i, box in enumerate(boxes):
            row_box, col_box, _ = box
            if row == row_box and col == col_box:
                return (key, i)
    return None


def check_action(actions, current_state: 'State', walls):
    '''Check if every agent's action is applicable in the current state and returns
    a list with the index of the agents' whose action are not applicable'''
    next_state = State(current_state)
    index_non_applicable = []
    is_applicable = True

    # defining a server-like state where we'll create fictive agent to keep track
    # of the previous agent position
    server_state = State(current_state)

    for i, action in enumerate(actions):
        i = str(i)
        row, col, color = current_state.agents[i]
        if action.action_type is ActionType.NoOp:
            continue
        else:
            new_agent_row = row + action.agent_dir.d_row
            new_agent_col = col + action.agent_dir.d_col

            if action.action_type is ActionType.Move:
                if server_state.is_free(walls, new_agent_row, new_agent_col):
                    server_state.agents[i + i] = (row, col, color)
                    server_state.agents[i] = (new_agent_row, new_agent_col, color)
                    next_state.agents[i] = (new_agent_row, new_agent_col, color)
                else:
                    index_non_applicable.append(i)
                    is_applicable = False
            elif action.action_type is ActionType.Push:
                box_key = get_box_key_by_position(new_agent_row, new_agent_col, next_state)
                new_box_row = new_agent_row + action.box_dir.d_row
                new_box_col = new_agent_col + action.box_dir.d_col
                if server_state.is_free(walls, new_box_row, new_box_col):
                    server_state.agents[i + i] = (row, col, color)
                    server_state.agents[i] = (new_agent_row, new_agent_col, color)
                    server_state.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, color)
                    next_state.agents[i] = (new_agent_row, new_agent_col, color)
                    next_state.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, color)
                else:
                    index_non_applicable.append(i)
                    is_applicable = False
            elif action.action_type is ActionType.Pull:
                box_row = row + action.box_dir.d_row
                box_col = col + action.box_dir.d_col
                box_key = get_box_key_by_position(box_row, box_col, next_state)

                new_box_row = box_row + action.box_dir.d_row * -1
                new_box_col = box_col + action.box_dir.d_col * -1

                if server_state.is_free(walls, new_agent_row, new_agent_col):
                    server_state.agents[i] = (new_agent_row, new_agent_col, color)
                    server_state.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, color)
                    next_state.agents[i] = (new_agent_row, new_agent_col, color)
                    next_state.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, color)
                else:
                    index_non_applicable.append(i)
                    is_applicable = False

    return index_non_applicable, next_state, is_applicable


def missing_goals(current_state, goal_state):
    '''Return the index of the agents that haven't reached their goal and the
    corresponding box, ex: {'0': ('A', (3, 9, 'red'))}'''
    current_boxes = current_state.boxes
    goal_boxes = goal_state.boxes

    missing_boxes = []
    for box_key in goal_boxes:
        for i, box in enumerate(goal_boxes[box_key]):
            try:
                if box not in current_boxes[box_key]:
                    missing_boxes.append((box_key, i))
            except KeyError:
                pass

    boxes_to_solve = {}

    for box in missing_boxes:
        for agent_key, agent_info in current_state.agents.items():
            box_color = current_state.boxes[box[0]][box[1]][2]
            agent_color = agent_info[2]
            if box_color == agent_color:
                boxes_to_solve[agent_key] = box

    return boxes_to_solve


def add_padding_actions(solution, nb_agents, current_state):
    '''adding NoOp action for agent that have already satisfied their goals'''
    max_len_sol = max(getLen(x) for x in solution)
    for i in range(nb_agents):
        try:
            padding_state = State(solution[i][-1])
        except:
            padding_state = current_state

        padding_state.action = Action(ActionType.NoOp, None, None)
        try:
            solution[i] += [padding_state] * (max_len_sol - len(solution[i]))
        except:
            solution[i] = [padding_state] * max_len_sol
    return solution


def getLen(obj):
    if obj is None:
        return 0
    else:
        return len(obj)


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

        solution = add_padding_actions(solution, nb_agents, current_state)
        printer = ";".join(['{}'] * nb_agents)

        while len(solution[0]) > 0:
            # grabbing state for each agent
            state = [elt[0] for elt in solution]

            action = [agent.action for agent in state]

            index_non_applicable, current_state, is_applicable = check_action(action, current_state, walls)
            msg_server_comment(printer.format(*action) + " - applicable: {}".format(is_applicable))

            # if there is a conflict between agents then we recompute a new goal for each agent
            if not is_applicable:
                for key_agent in index_non_applicable:
                    action[int(key_agent)] = ActionType.NoOp
                msg_server_comment("Switching to action: " + printer.format(*action))

                new_solution = []
                for j, agent in enumerate(starfish_client.agents):
                    box_key = starfish_client.agents[j].box_key
                    starfish_client.agents[j] = Agent(current_state, agent.agent_key)
                    starfish_client.agents[j].assign_goal(starfish_client.goal_state, box_key)
                    new_solution.append(deepcopy(starfish_client).agents[j].find_path_to_goal(walls))
                new_solution = add_padding_actions(new_solution, nb_agents, current_state)

                # removing the actions from previous goal and adding the ones from the new goal
                for i in range(len(solution)):
                    solution[i].clear()
                    solution[i].extend(new_solution[i])
            else:
                # removing the accomplished actions of each agent
                for elt in solution:
                    elt.pop(0)

            msg_server_action(printer.format(*action))

            if len(solution[0]) == 0 and not current_state.is_goal_state(starfish_client.goal_state):
                goals_missing = missing_goals(current_state, starfish_client.goal_state)
                new_solution = []
                for j, agent in enumerate(starfish_client.agents):
                    if agent.agent_key in goals_missing.keys():
                        box_key = goals_missing[agent.agent_key]
                        starfish_client.agents[j] = Agent(current_state, agent.agent_key)
                        starfish_client.agents[j].assign_goal(starfish_client.goal_state, box_key)
                        new_solution.append(starfish_client.agents[j].find_path_to_goal(walls))
                    else:
                        new_solution.append([])

                new_solution = add_padding_actions(new_solution, nb_agents, current_state)
                for i in range(len(solution)):
                    solution[i].extend(new_solution[i])

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
