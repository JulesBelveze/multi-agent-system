from __future__ import print_function
from argparse import ArgumentParser
from copy import deepcopy
import numpy as np
import sys

from agent import Agent
from state import State
from action import Action
from action import ActionType
from conflict import Conflict
from cooperation import Cooperation

from message import msg_server_err
from message import msg_server_comment
from message import msg_server_action

from action import Direction, get_direction_moving_coord
from client_functions import add_padding_actions, get_box_key_by_position, check_action, get_missing_goals, getLen, \
    reassign_goals, isListEmpty, get_noop


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

    def queries_to_action(self, queries, state: 'State'):
        '''transforming users' queries to actions'''
        joint_action = [[]] * len(self.agents)

        for query in queries:
            acting_query, waiting_query = query.split("|")
            acting_query = acting_query.strip().split(" ")

            waiting_agent = waiting_query.strip().split(" ")[1]
            acting_agent = acting_query[1]

            try:
                if waiting_agent == "*":
                    freeing_directions = state.get_freeing_actions(acting_agent, self.walls)

                    for dir in freeing_directions:
                        padding_state = deepcopy(state)
                        joint_action[int(acting_agent)].append(padding_state)
                        joint_action[int(acting_agent)][-1].action = Action(ActionType.Move, dir, None)

                    for key, agent in state.agents.items():
                        if key != acting_agent:
                            self.agents[int(key)].forget_goal()
                            joint_action[int(key)] = get_noop(state, len(freeing_directions) + 1)

            except (ValueError, IndexError):
                pass

            try:
                # meaning an agent has to move
                if acting_query[2] == "-":
                    row, col = state.agents[acting_agent][0], state.agents[acting_agent][1]
                    new_row, new_col = state.get_free_neighbouring_cell(self.walls, row, col)
                    moving_dir = get_direction_moving_coord(tuple(np.subtract((new_row, new_col), (row, col))))

                    padding_state = deepcopy(state)
                    joint_action[int(acting_agent)].append(padding_state)
                    joint_action[int(acting_agent)][-1].action = Action(ActionType.Move, moving_dir, None)

                    self.agents[int(waiting_agent)].forget_goal()
                    joint_action[int(waiting_agent)] = get_noop(state, 2)
            except (ValueError, IndexError):
                pass

            try:
                # meaning a box has to be moved
                if acting_query[2] == "box":
                    box_to_move = tuple(acting_query[3].split(','))
                    new_row, new_col = state.get_random_free_cell(self.max_row, self.max_col, self.walls)

                    # defining a fictive goal state for the acting agent
                    hacked_goal = deepcopy(self.goal_state)
                    try:
                        hacked_goal.boxes[box_to_move[0]][int(box_to_move[1])].append(
                            (new_row, new_col, box_to_move[2]))
                    except KeyError:
                        hacked_goal.boxes[box_to_move[0]] = [(new_row, new_col, box_to_move[2])]

                    self.agents[int(acting_agent)].assign_goal(hacked_goal, (box_to_move[0], int(box_to_move[1])))
                    result = self.agents[int(acting_agent)].find_path_to_goal(self.walls)
                    joint_action[int(acting_agent)] = result

                    self.agents[int(waiting_agent)].forget_goal()
                    joint_action[int(waiting_agent)] = get_noop(state, len(result))
            except (ValueError, IndexError):
                pass

        return joint_action


def main(args):
    level_data = None

    # Read server messages from stdin.
    msg_server_action("Starfish")
    level_data = sys.stdin

    # Create client using server messages
    starfish_client = Client(level_data)
    current_state = starfish_client.initial_state
    walls = starfish_client.walls

    # Solve and print
    # TODO: configuration when an agent is blocking all the others
    solution = starfish_client.solve_level()
    if isListEmpty(solution):
        coop = Cooperation(current_state, starfish_client.goal_state, starfish_client.walls)
        queries = coop.get_needed_coop()
        solution = starfish_client.queries_to_action(queries, current_state)

    nb_agents = len(solution)
    printer = ";".join(['{}'] * nb_agents)

    verified = False
    while (not isListEmpty(solution)) or (verified == False):
        missing_goals = get_missing_goals(current_state, starfish_client.goal_state)

        if len(missing_goals) == 0:
            verified = True

        for i, elt in enumerate(solution):
            if len(elt) == 0 and str(i) not in missing_goals:
                padding_state = current_state
                solution[i].append(padding_state)
                solution[i][-1].action = Action(ActionType.NoOp, None, None)

            elif len(elt) == 0 and str(i) in missing_goals:  # and not starfish_client.agents[i].has_goal():
                starfish_client.agents[i].current_state = current_state
                starfish_client.agents[i].assign_goal(starfish_client.goal_state, (missing_goals[str(i)][0], 0))
                new_path = starfish_client.agents[i].find_path_to_goal(starfish_client.walls)

                if new_path is not None and len(new_path) > 0:
                    solution[i].extend(new_path)
                else:
                    padding_state = current_state
                    solution[i].append(padding_state)
                    solution[i][-1].action = Action(ActionType.NoOp, None, None)

        # grabbing state for each agent
        state = [elt[0] for elt in solution]

        joint_action = [agent.action for agent in state]

        index_non_applicable, current_state, is_applicable = check_action(joint_action, current_state, walls)
        msg_server_comment(printer.format(*joint_action) + " - applicable: {}".format(is_applicable))

        # if there is a conflict between agents
        if not is_applicable:
            conflict = Conflict(current_state, index_non_applicable, joint_action, solution, walls)
            agents, actions = conflict.handle_conflicts()

            joint_action = [Action(ActionType.NoOp, None, None)] * nb_agents
            for (agent, action) in zip(agents, actions):
                joint_action[int(agent)] = action

                # forgetting goal in order to help fix the conflict
                padding_state = current_state
                solution[int(agent)] = [padding_state]
                solution[int(agent)][-1].action = Action(ActionType.NoOp, None, None)
                solution[int(agent)].append(solution[int(agent)][-1])
                starfish_client.agents[int(agent)].forget_goal()

            _, current_state, _ = check_action(joint_action, current_state, walls)
            msg_server_comment("New action: " + printer.format(*joint_action))

        msg_server_action(printer.format(*joint_action))

        if is_applicable:
            for i, elt in enumerate(solution):
                elt.pop(0)

        response = level_data.readline().rstrip()
        if 'false' in response:
            msg_server_err("Server answered with error to the action " + printer.format(*joint_action))


if __name__ == "__main__":
    # Process arguments
    parser = ArgumentParser(description='Starfish client for solving transportation tasks.')
    parser.add_argument('--debugLevel', default=None,
                        help='Provide the name of a level for client to run in debug mode')

    args = parser.parse_args()

    # Run client
    main(args)
