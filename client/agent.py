from operator import itemgetter
from collections import Counter

from message import msg_server_err
from message import msg_server_comment
from message import msg_server_action

from pathing import Path
from pathing import Navigate
from state import State

from action import ALL_DIRECTIONS, DIR_MIRROR

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

                # Second complete main goal - move box to goal
                while not self.is_goal_reached():
                    agent_dir_values = self.get_direction_values(agent, path)
                    box_dir_value = self.get_direction_values(c_box, path)[0]

                    # When a box should be pulled, the direction needs to be flipped because e.g. Pull(S,S) is invalid
                    agent_dir_value = agent_dir_values[0]
                    if agent_dir_value[1] > box_dir_value[1]:
                        zero_count = Counter(elem[1] for elem in agent_dir_values)[0]
                        if zero_count < 2:
                            box_val = path[c_box[0]][c_box[1]]
                            if DIR_MIRROR.get(agent_dir_values[1][0]) is not box_dir_value[0]:
                                agent_dir_value = agent_dir_values[1]
                                box_dir_value = (DIR_MIRROR.get(box_dir_value[0]), box_dir_value[1])
                            elif DIR_MIRROR.get(agent_dir_values[2][0]) is not box_dir_value[0]:
                                agent_dir_value = agent_dir_values[2]
                                box_dir_value = (DIR_MIRROR.get(box_dir_value[0]), box_dir_value[1])
                        else:
                            box_dir_value = (DIR_MIRROR.get(box_dir_value[0]), box_dir_value[1])

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

    def get_direction_values(self, current_pos, path):
        dir_values = []

        for key, value in ALL_DIRECTIONS.items():
            new_pos = (current_pos[0] + value[0], current_pos[1] + value[1])
            new_val = path[new_pos[0]][new_pos[1]]
            dir_values.append((key, new_val))
        return sorted(dir_values, key=itemgetter(1), reverse=True)

    def pick_direction(self, current_pos, path, is_agent):
        # Keep track of the top 2 highest values
        current_max = ('', 0)
        second_max = ('', 0)

        for key, value in ALL_DIRECTIONS.items():
            new_pos = (current_pos[0] + value[0], current_pos[1] + value[1])
            new_val = path[new_pos[0]][new_pos[1]]
            if new_val > current_max[1]:
                second_max = current_max
                current_max = (key, new_val)
            elif new_val > second_max[1]:
                second_max = (key, new_val)
        return current_max if not is_agent else second_max

#     def pick_h_target(self, agent, box, nav_step):
#         return agent if nav_step == 0 else box

#     def find_path_to_goal(self, walls):
#         agent = self.current_state.agents.get(self.agent_key)
#         c_box = self.current_state.boxes.get(self.box_key[0])[self.box_key[1]]
#         g_box = self.goal_state.boxes.get(self.box_key[0])[self.box_key[1]]
#         final_plan = []

#         # Find path to current box
#         path = self.path_finder.calc_route(walls, (agent[0], agent[1]), (c_box[0], c_box[1]), self.current_state)
#         if path is not None:
#             msg_server_comment("Found path from agent {} to box {}".format(self.agent_key, self.box_key))

#             iterations = 0
#             h_target = agent
#             for nav_step in range(0, 2):
#                 self.navigator.add_to_frontier(self.current_state, h_target, path)
#                 while iterations < 16000:
#                     if self.navigator.frontier_count() == 0:
#                         msg_server_err("Failed to navigate agent {} to box {}!".format(self.agent_key, self.box_key))
#                         return None

#                     current = self.navigator.get_from_frontier()
#                     agent = current.agents.get(self.agent_key)

#                     # Goal checking
#                     if nav_step == 0:
#                         is_sub_goal = abs(c_box[0] - agent[0]) + abs(c_box[1] - agent[1]) == 1
#                         h_target = agent
#                     else:
#                         c_box = current.boxes.get(self.box_key[0])[self.box_key[1]]
#                         is_sub_goal = path[c_box[0]][c_box[1]] - path[g_box[0]][g_box[1]] == 0

#                     if is_sub_goal:
#                         is_sub_goal = False
#                         final_plan = current.extract_plan()
#                         self.current_state = current
#                         self.navigator = Navigate()
#                         iterations = 0
#                         break

#                     # Explore child states
#                     self.navigator.add_to_explored(current)
#                     for child_state in current.get_children(walls, self.agent_key, self.box_key):
#                         if not self.navigator.is_explored(child_state) and not self.navigator.in_frontier(child_state):
#                             if nav_step > 0:
#                                 h_target = child_state.boxes.get(self.box_key[0])[self.box_key[1]]
#                             self.navigator.add_to_frontier(child_state, h_target, path)

#                     iterations += 1

#                 if iterations >= 100000:
#                     msg_server_err("Max iterations when looking for states exceeded!")
#                     return None

#                 if nav_step == 0:
#                     path = self.path_finder.calc_route(walls, (c_box[0], c_box[1]), (g_box[0], g_box[1]),
#                                                        self.current_state)
#                     if path is None:
#                         return None

#                     msg_server_comment("Found path from box {} to goal box".format(self.box_key))

#         return final_plan
