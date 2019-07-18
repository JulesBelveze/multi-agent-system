import sys
import numpy as np
from state import State
from action import ActionType, Action, Direction, pull_possibilities, push_possibilities, move_possibilities
from client_functions import get_box_key_by_position, get_agent_key_by_color

object_of_conflict = ['box', 'agent']
cause_of_conflict = ['on_goal', 'block_road']


class Conflict:
    def __init__(self, current_state, agents_blocked, actions, solution, walls):
        self.current_state = current_state
        self.next_state = None
        self.agents_blocked = agents_blocked
        self.actions = actions
        self.solution = solution
        self.walls = walls

    def handle_conflicts(self):
        conflicts = self._get_conflicts()
        agents, actions = [], []
        for conflict in conflicts:
            # print(conflict)
            agent, new_action = self._solve_conflict(conflict)
            agents.append(agent)
            actions.append(new_action)
        return agent, new_action

    def _solve_conflict(self, conflict):
        '''changing actions of the agents conflicting by trying to remove them from
        the path'''
        agent, obj_type, obj = conflict[0], conflict[1], conflict[2]

        agent_states = self.solution[int(agent)]
        agent_positions = [state.agents[agent] for state in agent_states]

        if obj_type == "box":
            obj_row, obj_col, obj_color = self.current_state.boxes[obj[0]][obj[1]]
            key_agent_in_charge, agent_in_charge = get_agent_key_by_color(obj_color, self.current_state.agents)

            pr = tuple(np.subtract((agent_in_charge[0], agent_in_charge[1]), (obj_row, obj_col)))

            actions = pull_possibilities[pr] + push_possibilities[pr]
            for action in actions:
                is_applicable, next_pos_agent, next_pos_box, next_state = self.check_action(action, key_agent_in_charge)
                if is_applicable:
                    is_agent_on_path = self._is_on_path(agent_positions, next_pos_agent)
                    is_box_on_path = self._is_on_path(agent_positions, next_pos_box)

                    if not is_agent_on_path and not is_box_on_path:
                        return key_agent_in_charge, action

    def _get_conflicts(self):
        '''Check if every agent's action is applicable in the current state and returns
        a list with the index of the agents' whose action are not applicable'''
        self.next_state = State(self.current_state)
        conflicts = []

        # defining a server-like state where we'll create fictive agent to keep track
        # of the previous agent position
        server_state = State(self.current_state)

        for i, action in enumerate(self.actions):
            i = str(i)
            row, col, color = self.current_state.agents[i]
            if action.action_type is ActionType.NoOp:
                continue
            else:
                new_agent_row = row + action.agent_dir.d_row
                new_agent_col = col + action.agent_dir.d_col

                if action.action_type is ActionType.Move:
                    is_free, type_obj, obj = server_state.is_no_object(new_agent_row, new_agent_col)
                    if is_free:
                        server_state.agents[i + i] = (row, col, color)
                        server_state.agents[i] = (new_agent_row, new_agent_col, color)
                        self.next_state.agents[i] = (new_agent_row, new_agent_col, color)
                    else:
                        conflicts.append([i, type_obj, obj])

                elif action.action_type is ActionType.Push:
                    box_key = get_box_key_by_position(new_agent_row, new_agent_col, self.next_state)
                    new_box_row = new_agent_row + action.box_dir.d_row
                    new_box_col = new_agent_col + action.box_dir.d_col

                    is_free, type_obj, obj = server_state.is_no_object(new_box_row, new_box_col)
                    if is_free:
                        server_state.agents[i + i] = (row, col, color)
                        server_state.agents[i] = (new_agent_row, new_agent_col, color)
                        server_state.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, color)
                        self.next_state.agents[i] = (new_agent_row, new_agent_col, color)
                        self.next_state.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, color)
                    else:
                        conflicts.append([i, type_obj, obj])

                elif action.action_type is ActionType.Pull:
                    box_row = row + action.box_dir.d_row
                    box_col = col + action.box_dir.d_col
                    box_key = get_box_key_by_position(box_row, box_col, self.next_state)

                    new_box_row = box_row + action.box_dir.d_row * -1
                    new_box_col = box_col + action.box_dir.d_col * -1

                    is_free, type_obj, obj = server_state.is_no_object(new_agent_row, new_agent_col)
                    if is_free:
                        server_state.agents[i] = (new_agent_row, new_agent_col, color)
                        server_state.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, color)
                        self.next_state.agents[i] = (new_agent_row, new_agent_col, color)
                        self.next_state.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, color)
                    else:
                        conflicts.append([i, type_obj, obj])

        return conflicts

    def check_action(self, action, agent):
        '''Check if every agent's action is applicable in the current state and returns
        a list with the index of the agents' whose action are not applicable'''
        next_state = State(self.current_state)
        is_applicable = True
        box_next_pos = None  # next position of box if it is different, otherwise None

        # defining a server-like state where we'll create fictive agent to keep track
        # of the previous agent position
        server_state = State(self.current_state)

        i = str(agent)
        row, col, color = self.current_state.agents[i]

        new_agent_row = row + action.agent_dir.d_row
        new_agent_col = col + action.agent_dir.d_col

        if action.action_type is ActionType.Move:
            if server_state.is_free(self.walls, new_agent_row, new_agent_col):
                server_state.agents[i + i] = (row, col, color)
                server_state.agents[i] = (new_agent_row, new_agent_col, color)
                next_state.agents[i] = (new_agent_row, new_agent_col, color)
            else:
                is_applicable = False

        elif action.action_type is ActionType.Push:
            box_key = get_box_key_by_position(new_agent_row, new_agent_col, next_state)
            new_box_row = new_agent_row + action.box_dir.d_row
            new_box_col = new_agent_col + action.box_dir.d_col
            if server_state.is_free(self.walls, new_box_row, new_box_col):
                server_state.agents[i + i] = (row, col, color)
                server_state.agents[i] = (new_agent_row, new_agent_col, color)
                server_state.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, color)
                next_state.agents[i] = (new_agent_row, new_agent_col, color)
                next_state.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, color)
                box_next_pos = (new_box_row, new_box_col, color)
            else:
                is_applicable = False

        elif action.action_type is ActionType.Pull:
            box_row = row + action.box_dir.d_row
            box_col = col + action.box_dir.d_col
            box_key = get_box_key_by_position(box_row, box_col, next_state)

            new_box_row = box_row + action.box_dir.d_row * -1
            new_box_col = box_col + action.box_dir.d_col * -1
            if server_state.is_free(self.walls, new_agent_row, new_agent_col):
                server_state.agents[i] = (new_agent_row, new_agent_col, color)
                server_state.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, color)
                next_state.agents[i] = (new_agent_row, new_agent_col, color)
                next_state.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, color)
                box_next_pos = (new_box_row, new_box_col, color)
            else:
                is_applicable = False

        if not is_applicable:
            next_state = self.current_state

        return is_applicable, next_state.agents[i], box_next_pos, next_state

    def _is_on_path(self, path, pos):
        '''check if a position is on an agent path'''
        future_positions = [(elt[0], elt[1]) for elt in path]
        if (pos[0], pos[1]) in future_positions:
            return True
        return False
