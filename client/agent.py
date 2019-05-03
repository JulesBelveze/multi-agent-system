from pathing import Pathing

class Agent:
    def __init__(self, initial_state: 'State', agent_key: 'str'):
        self.agent_key = agent_key
        self.current_state = initial_state
        self.path_finder = Pathing()

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

        self.path_finder.calc_route(walls, (agent[0], agent[1]), (g_box[0], g_box[1]), self.current_state)
        self.path_finder.print_path()


        
        # # Start with initial state
        # self.path_finder.add_to_frontier(self.current_state)

        # iterations = 0   #todo: this is a temp hack
        # while iterations < 15000:
        #     if self.path_finder.frontier_count() == 0:
        #         return None
            
        #     current = self.path_finder.get_from_frontier()

        #     if current.is_goal_state(self.goal_state, self.box_key):
        #         return current.extract_plan()
            
        #     self.path_finder.add_to_explored(current)
        #     for child_state in current.get_children(walls, self.agent_key, self.box_key):
        #         if not self.path_finder.is_explored(child_state) and not self.path_finder.in_frontier(child_state):
        #             self.path_finder.add_to_frontier(child_state)
        #     iterations += 1
        return None