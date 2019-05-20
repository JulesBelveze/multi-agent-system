from operator import itemgetter
from collections import Counter

from message import msg_server_err
from message import msg_server_comment
from message import msg_server_action

from pathing import Path
from pathing import Navigate
from state import State

from action import ALL_DIRECTIONS, DIR_MIRROR, ActionType

class Agent:
    def __init__(self, initial_state: 'State', agent_key: 'str'):
        self.navigator = Navigate()
        self.agent_key = agent_key
        self.current_state = State(initial_state)

    def assign_goal(self, goal_state: 'State', box_key):
        self.goal_state = goal_state
        self.box_key = box_key
        self.path_finder = Path(self.agent_key, box_key)

    def has_goal(self):
        if self.goal_state is None or self.box_key is None:
            return False
        return True

    def is_goal_reached(self):
        if not self.has_goal():
            msg_server_comment("Agent {} has no goal!".format(self.agent_key))
            return False

        c_box = self.current_state.boxes.get(self.box_key[0])[self.box_key[1]]
        g_box = self.goal_state.boxes.get(self.box_key[0])[self.box_key[1]]
        return c_box[0] == g_box[0] and c_box[1] == g_box[1]

    def is_sub_goal_reached(self):
        if not self.has_goal():
            msg_server_comment("Agent {} has no goal!".format(self.agent_key))
            return False

        c_box = self.current_state.boxes.get(self.box_key[0])[self.box_key[1]]
        agent = self.current_state.agents.get(self.agent_key)
        return abs(c_box[0] - agent[0]) + abs(c_box[1] - agent[1]) == 1

    def find_path_to_goal(self, walls):
        if not self.has_goal():
            return None

        agent = self.current_state.agents.get(self.agent_key)
        c_box = self.current_state.boxes.get(self.box_key[0])[self.box_key[1]]
        g_box = self.goal_state.boxes.get(self.box_key[0])[self.box_key[1]]
        final_actions = []

        # Find path to current box
        path = self.path_finder.calc_route(walls, (agent[0], agent[1]), (c_box[0], c_box[1]), self.current_state)
        if path is not None:
            msg_server_comment("Found path from agent {} to box {}".format(self.agent_key, self.box_key))

            # First complete the sub goal - getting agent to box
            while not self.is_sub_goal_reached():
                dir_values = self.get_direction_values(agent, path)

                child_state = self.current_state.get_child(walls, dir_values[0], self.agent_key, None, None)
                if child_state is not None:
                    self.current_state = child_state
                    agent = self.current_state.agents.get(self.agent_key)
                else:
                    msg_server_err("Could not create child state from: {}".format(self.current_state))
                    break

            # Find path to goal box
            path = self.path_finder.calc_route(walls, (c_box[0], c_box[1]), (g_box[0], g_box[1]), self.current_state)
            if path is not None:
                msg_server_comment("Found path from box {} to goal box".format(self.box_key))
                flip_transition = False

                # Second complete main goal - move box to goal
                while not self.is_goal_reached():
                    agent_dir_values = self.get_direction_values(agent, path)
                    agent_dir_value = agent_dir_values[0]
                    box_dir_values = self.get_direction_values(c_box, path)
                    box_dir_value = box_dir_values[0]

                    #msg_server_comment("{}, {}".format(path[agent[0]][agent[1]], path[c_box[0]][c_box[1]]))
                    # When a box should be pulled, the direction needs to be mirrored because e.g. Pull(S,S) is invalid
                    if agent_dir_value[1] > box_dir_value[1] and not flip_transition:
                        # Check for possibility of flipping to push
                        zero_count = Counter(elem[1] for elem in agent_dir_values)[0]
                        if zero_count < 2:
                            # Make sure the chosen direction will not be in the direction of the box
                            for i in range(1, len(agent_dir_values)):
                                item = agent_dir_values[i]
                                if DIR_MIRROR.get(item[0]) is not box_dir_value[0]:
                                    agent_dir_value = item
                                    flip_transition = True

                                    # Make sure box direction is to agent's current pos
                                    if box_dir_value[2][0] != agent_dir_value[2][0] and box_dir_value[2][1] != agent_dir_value[2][1]:
                                        for j in range(1, len(box_dir_values)):
                                            box = box_dir_values[j]
                                            if box[2][0] == agent[0] and box[2][1] == agent[1]:
                                                box_dir_value = box
                                                break
                                    break
                        box_dir_value = (DIR_MIRROR.get(box_dir_value[0]), box_dir_value[1])
                    else:
                        if flip_transition:
                            flip_transition = False

                        # Force the agent's direction to current pos of box, making it push the box
                        if agent_dir_value[2][0] != c_box[0] and agent_dir_value[2][1] != c_box[1]:
                            for i in range(1, len(agent_dir_values)):
                                item = agent_dir_values[i]
                                if item[2][0] == c_box[0] and item[2][1] == c_box[1]:
                                    agent_dir_value = item
                                    break

                    child_state = self.current_state.get_child(walls, agent_dir_value, self.agent_key, box_dir_value, self.box_key)
                    if child_state is not None:
                        self.current_state = child_state
                        agent = self.current_state.agents.get(self.agent_key)
                        c_box = self.current_state.boxes.get(self.box_key[0])[self.box_key[1]]
                    else:
                        msg_server_err("Could not create child state from: {}".format(self.current_state))
                        break

                final_actions = self.current_state.extract_plan()

        return final_actions

    # Returns a tuple in the form: Direction name, grid value, new_pos(x,y)
    def get_direction_values(self, current_pos, path):
        dir_values = []

        for key, value in ALL_DIRECTIONS.items():
            new_pos = (current_pos[0] + value[0], current_pos[1] + value[1])
            new_val = path[new_pos[0]][new_pos[1]]
            dir_values.append((key, new_val, new_pos))
        return sorted(dir_values, key=itemgetter(1), reverse=True)
