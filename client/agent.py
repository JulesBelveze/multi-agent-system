

class Agent:
    def __init__(self, initial_state: 'State', agent_key: 'str'):
        self.agent_key = agent_key
        self.initial_state = initial_state
        self.goal_state = None
        self.box_key = None

    def assign_goal(self, goal_state: 'State', box_key: 'str'):
        self.goal_state = goal_state
        self.box_key = box_key

    def has_goal(self):
        if self.goal_state is None or self.box_key is None:
            return False

        return True

    def find_path_to_goal(self, walls, goal_state):
        explored = []
        frontier = []
        frontier.append(self.initial_state)
        
        leaf = frontier.pop()
        #for child_state in leaf.get_children(self.agent_key)
        # fill "states" list
        #pick goal

