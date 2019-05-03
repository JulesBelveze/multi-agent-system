from message import msg_server_err
from message import msg_server_comment
from message import msg_server_action

from pathing import Path
from pathing import Navigate

class Agent:
    def __init__(self, initial_state: 'State', agent_key: 'str'):
        self.agent_key = agent_key
        self.current_state = initial_state
        self.path_finder = Path()
        self.navigator = Navigate()

    def assign_goal(self, goal_state: 'State', box_key: 'str'):
        self.goal_state = goal_state
        self.box_key = box_key
        #self.path_finder.set_path_objective(goal_state, box_key, self.agent_key)

    def has_goal(self):
        if self.goal_state is None or self.box_key is None:
            return False
        return True

    def find_path_to_goal(self, walls):
        agent = self.current_state.agents.get(self.agent_key)
        c_box = self.current_state.boxes.get(self.box_key)
        g_box = self.goal_state.boxes.get(self.box_key)
        final_plan = []

        # Find path to current box
        path = self.path_finder.calc_route(walls, (agent[0], agent[1]), (c_box[0], c_box[1]), self.current_state)
        if path is not None:
            msg_server_comment("Found path from agent to box:")
            msg_server_comment(path)

            # Navigate
            self.navigator.add_to_frontier(self.current_state, self.navigator.h_calculate(agent, path))
            iterations = 0  #TODO: temp hack
            while iterations < 16000:
                if self.navigator.frontier_count() == 0:
                    msg_server_err("Failed to navigate agent to box!")
                    return None

                current = self.navigator.get_from_frontier()
                agent = current.agents.get(self.agent_key)

                # Is the agent next to the box that needs to be moved?
                if abs(self.navigator.h_calculate(agent, path) - self.navigator.h_calculate(c_box, path)) == 1:
                    final_plan.extend(current.extract_plan())
                    self.current_state = current
                    break

                self.navigator.add_to_explored(current)
                for child_state in current.get_children(walls, self.agent_key, self.box_key):
                    if not self.navigator.is_explored(child_state) and not self.navigator.in_frontier(child_state):
                        self.navigator.add_to_frontier(child_state, self.navigator.h_calculate(agent, path))
  
                iterations += 1

            # Find path to goal box
            path = self.path_finder.calc_route(walls, (c_box[0], c_box[1]), (g_box[0], g_box[1]), self.current_state)
            if self.path_finder.is_path_found((c_box[0], c_box[1])):
                msg_server_comment("Found path from box to goal box:")
                self.path_finder.print_path()

                # Start fresh navigation task
                self.navigator = Navigate() # This line was so painful to type as a C++ guy

                #TODO: fix code duplication
                self.navigator.add_to_frontier(self.current_state, self.navigator.h_calculate(c_box, path))
                iterations = 0  #TODO: temp hack
                while iterations < 16000:
                    if self.navigator.frontier_count() == 0:
                        msg_server_err("Failed to navigate box to goal!")
                        return None

                    current = self.navigator.get_from_frontier()
                    c_box = current.boxes.get(self.box_key)

                    if self.navigator.h_calculate(c_box, path) - self.navigator.h_calculate(g_box, path) == 0:
                        final_plan.extend(current.extract_plan())
                        break

                    self.navigator.add_to_explored(current)
                    for child_state in current.get_children(walls, self.agent_key, self.box_key):
                        if not self.navigator.is_explored(child_state) and not self.navigator.in_frontier(child_state):
                            self.navigator.add_to_frontier(child_state, self.navigator.h_calculate(c_box, path))
    
                    iterations += 1

            return final_plan
        return None