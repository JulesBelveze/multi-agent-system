from message import msg_server_err
from message import msg_server_comment
from message import msg_server_action

from pathing import Path
from pathing import Navigate
from state import State

class Agent:
    def __init__(self, initial_state: 'State', agent_key: 'str'):
        self.agent_key = agent_key
        self.current_state = State(initial_state)
        self.path_finder = Path()
        self.navigator = Navigate()

    def assign_goal(self, goal_state: 'State', box_key):
        self.goal_state = goal_state
        self.box_key = box_key

    def has_goal(self):
        if self.goal_state is None or self.box_key is None:
            return False
        return True

    def is_agent_next_to_box(self, agent, box):
        return abs(box[0] - agent[0]) + abs(box[1] - agent[1]) == 1

    def pick_h_target(self, agent, box, nav_step):
        return agent if nav_step == 0 else box

    def find_path_to_goal(self, walls):
        agent = self.current_state.agents.get(self.agent_key)
        c_box = self.current_state.boxes.get(self.box_key[0])[self.box_key[1]]
        g_box = self.goal_state.boxes.get(self.box_key[0])[self.box_key[1]]
        final_plan = []

        # Find path to current box
        path = self.path_finder.calc_route(walls, (agent[0], agent[1]), (c_box[0], c_box[1]), self.current_state)
        if path is not None:
            msg_server_comment("Found path from agent {} to box {}".format(self.agent_key, self.box_key))

            iterations = 0
            for nav_step in range(0, 2):
                self.navigator.add_to_frontier(self.current_state, self.navigator.h_calculate(self.pick_h_target(agent, c_box, nav_step), path))
                while iterations < 16000:
                    if self.navigator.frontier_count() == 0:
                        msg_server_err("Failed to navigate agent {} to box {}!".format(self.agent_key, self.box_key))
                        return None

                    current = self.navigator.get_from_frontier()
                    agent = current.agents.get(self.agent_key)

                    # Goal checking
                    goal_check = False
                    if nav_step == 0:
                        goal_check = self.is_agent_next_to_box(agent, c_box)
                    else:
                        c_box = current.boxes.get(self.box_key[0])[self.box_key[1]]
                        goal_check = self.navigator.h_calculate(c_box, path) - self.navigator.h_calculate(g_box, path) == 0

                    if goal_check:
                        final_plan = current.extract_plan()
                        self.current_state = current
                        self.navigator = Navigate()
                        iterations = 0
                        break

                    # Explore child states
                    self.navigator.add_to_explored(current)
                    for child_state in current.get_children(walls, self.agent_key, self.box_key):
                        if not self.navigator.is_explored(child_state) and not self.navigator.in_frontier(child_state):
                            h_target = self.pick_h_target(agent, child_state.boxes.get(self.box_key[0])[self.box_key[1]], nav_step)
                            self.navigator.add_to_frontier(child_state, self.navigator.h_calculate(h_target, path))

                    iterations += 1

                if iterations >= 16000:
                    msg_server_err("Max iterations when looking for states exceeded!")
                    return None

                if nav_step == 0:
                    path = self.path_finder.calc_route(walls, (c_box[0], c_box[1]), (g_box[0], g_box[1]), self.current_state)
                    if path is None:
                        return None

                    msg_server_comment("Found path from box {} to goal box".format(self.box_key))

            # # Navigate
            # self.navigator.add_to_frontier(self.current_state, self.navigator.h_calculate(agent, path))
            # iterations = 0  #TODO: temp hack
            # while iterations < 16000:
            #     if self.navigator.frontier_count() == 0:
            #         msg_server_err("Failed to navigate agent {} to box {}!".format(self.agent_key, self.box_key))
            #         return None

            #     current = self.navigator.get_from_frontier()
            #     agent = current.agents.get(self.agent_key)

            #     # Is the agent next to the box that needs to be moved? (Manhattan dist)
            #     if abs(c_box[0] - agent[0]) + abs(c_box[1] - agent[1]) == 1:
            #         final_plan = current.extract_plan()
            #         self.current_state = current
            #         self.navigator = Navigate() # This line was so painful to type as a C++ guy
            #         break

            #     self.navigator.add_to_explored(current)
            #     for child_state in current.get_children(walls, self.agent_key, self.box_key):
            #         if not self.navigator.is_explored(child_state) and not self.navigator.in_frontier(child_state):
            #             self.navigator.add_to_frontier(child_state, self.navigator.h_calculate(agent, path))
  
            #     iterations += 1

            # # Find path to goal box
            # path = self.path_finder.calc_route(walls, (c_box[0], c_box[1]), (g_box[0], g_box[1]), self.current_state)
            # if path is not None:
            #     msg_server_comment("Found path from box {} to goal box".format(self.box_key))

            #     #TODO: fix code duplication
            #     self.navigator.add_to_frontier(self.current_state, self.navigator.h_calculate(c_box, path))
            #     iterations = 0  #TODO: temp hack
            #     while iterations < 16000:
            #         if self.navigator.frontier_count() == 0:
            #             msg_server_err("Failed to navigate box {} to goal!".format(self.box_key))
            #             return None

            #         current = self.navigator.get_from_frontier()
            #         c_box = current.boxes.get(self.box_key[0])[self.box_key[1]]

            #         if self.navigator.h_calculate(c_box, path) - self.navigator.h_calculate(g_box, path) == 0:
            #             final_plan = current.extract_plan()
            #             self.current_state = current
            #             self.navigator = Navigate() # Oh almighty garbage collector, forgive me for abandoning so much memory
            #             break

            #         self.navigator.add_to_explored(current)
            #         for child_state in current.get_children(walls, self.agent_key, self.box_key):
            #             if not self.navigator.is_explored(child_state) and not self.navigator.in_frontier(child_state):
            #                 n_box = child_state.boxes.get(self.box_key[0])[self.box_key[1]]
            #                 self.navigator.add_to_frontier(child_state, self.navigator.h_calculate(n_box, path))
    
            #         iterations += 1

            # return final_plan
        return final_plan