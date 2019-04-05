from state import State

class Agent:
    def __init__(self, initial_state: State, goal_state: 'State', agent_key):
        self.agent_key = agent_key
        self.initial_state = initial_state
        self.currentState = 0
        

        find_path_to_goal(goal_state)

    def find_path_to_goal(self, goal_state):
        explored = []
        frontier = []
        frontier.append(self.initial_state)
        
        leaf = frontier.pop()
        #for child_state in leaf.get_children(self.agent_key)
        # fill "states" list
        #pick goal

