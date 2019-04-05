

class Agent:
    def __init__(self, initial_state: 'State', goal_state: 'State', agent_key: 'str'):
        self.agent_key = agent_key
        self.initial_state = initial_state

        #self.find_path_to_goal(goal_state)

    def find_path_to_goal(self, walls, goal_state):
        explored = []
        frontier = []
        frontier.append(self.initial_state)
        
        leaf = frontier.pop()
        #for child_state in leaf.get_children(self.agent_key)
        # fill "states" list
        #pick goal

