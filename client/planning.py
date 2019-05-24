from state import State
from operator import itemgetter

# Human-computed order of completing goals - will come from path computing algorithm
cheat_map = {}
cheat_map['A'] = ['C','B']
cheat_map['B'] = ['C']
cheat_map['C'] = []
cheat_map['M'] = []
cheat_map['H'] = []

class Plan():
    def __init__(self, initial_state: 'State', goal_state: 'State'):
        self.ordered_goal_plan = []
        self.goal_preconditions = {}

        for char, values in goal_state.boxes.items():
            self.goal_preconditions[char] = self.find_preconditions(initial_state, goal_state, char)
            self.ordered_goal_plan.append((char, len(self.goal_preconditions.get(char))))
        self.ordered_goal_plan = sorted(self.ordered_goal_plan, key=itemgetter(1), reverse=True)

    def find_preconditions(self, initial_state, goal_state, goal_key):
        # Do some pathing to the box and note all intersecting goal cells along the path
        return cheat_map.get(goal_key)