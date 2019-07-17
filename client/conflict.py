import sys

from state import State
from action import ActionType
from client_functions import get_box_key_by_position

object_of_conflict = ['box', 'agent']
cause_of_conflict = ['on_goal', 'block_road']


class Conflict:
    def __init__(self, current_state, agents_blocked, actions):
        self.current_state = current_state
        self.next_state = None
        self.agents_blocked = agents_blocked
        self.actions = actions
        self.agents = range(len(actions))

    # def get_conflicts(self):
    #     for agent_blocked in self.agents_blocked:
    #         position = self.current_state.agents[agent_blocked]
    #         action = self.actions(int(agent_blocked))
    #         self._get_object_by_position(position, action)
    #
    #     sys.exit()
    def solve_conflicts(self):
        print(self.get_conflicts())
        sys.exit()

    def get_conflicts(self):
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
