from pathing import PathingBestFirst

class Agent:
    def __init__(self, initial_state: 'State', agent_key: 'str'):
        self.agent_key = agent_key
        self.current_state = initial_state
        self.goal_state = None
        self.box_key = None
        self.path_finder = PathingBestFirst()

    def assign_goal(self, goal_state: 'State', box_key: 'str'):
        self.goal_state = goal_state
        self.box_key = box_key
        self.path_finder.set_path_objective(goal_state, box_key, self.agent_key)

    def has_goal(self):
        if self.goal_state is None or self.box_key is None:
            return False
        return True

    def find_path_to_goal(self, walls, goal_state):
        # Start with initial state
        self.path_finder.add_to_frontier(self.current_state)

        iterations = 0   #todo: this is a temp hack
        while iterations < 15000:
            if self.path_finder.frontier_count() == 0:
                return None
            
            current = self.path_finder.get_from_frontier()

            if current.is_goal_state(self.goal_state, self.box_key):
                return current.extract_plan()
            
            self.path_finder.add_to_explored(current)
            for child_state in current.get_children(walls, self.agent_key, self.box_key):
                if not self.path_finder.is_explored(child_state) and not self.path_finder.in_frontier(child_state):
                    self.path_finder.add_to_frontier(child_state)
            iterations += 1
        return None