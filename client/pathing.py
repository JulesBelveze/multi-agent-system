from abc import ABCMeta, abstractmethod
import heapq

class Heuristic:
    def __init__(self, goal_state: 'State', box_key: 'str', agent_key: 'str'):
        self.goal_state = goal_state
        self.box_key = box_key
        self.agent_key = agent_key

    '''Moving boxes, uses manhattan distance between goal and current box'''
    def h_box_distance(self, state: 'State') -> 'int':
        goal_box = self.goal_state.get(self.box_key)
        current_box = state.boxes.get(self.box_key)

        #Manhattan distance
        return abs(goal_box[0] - current_box[0]) + abs(goal_box[1] - current_box[1])

    '''Moving agents, uses manhattan distance between goal and current agent'''
    def h_agent_distance(self, state: 'State') -> 'int':
        current_agent = state.agents.get(self.agent_key)
        goal_agent = self.goal_state.agents.get(self.agent_key)

        return abs(goal_agent[0] - current_agent[0]) + abs(goal_agent[1] - current_agent[1])

    '''Potential heuristic for moving through 1 wide corridors'''
    def h_tunnel(self, state: 'State') -> 'int':
        return 0


class Pathing(metaclass=ABCMeta):
    def __init__(self):
        self.explored = set()

    def add_to_explored(self, state: 'State'):
        self.explored.add(state)
    
    def is_explored(self, state: 'State') -> 'bool':
        return state in self.explored

    def explored_count(self) ->'int':
        return len(self.explored)

    @abstractmethod
    def get_from_frontier(self) -> 'State': raise NotImplementedError
    
    @abstractmethod
    def add_to_frontier(self, state: 'State'): raise NotImplementedError

    @abstractmethod
    def in_frontier(self, state: 'State') -> 'bool': raise NotImplementedError

    @abstractmethod
    def frontier_count(self) -> 'int': raise NotImplementedError


class PathingBestFirst(Pathing):
    def __init__(self):
        super().__init__()
        self.frontier = []
        self.frontier_set = set()
        self.heuristic = None
        heapq.heapify(self.frontier)

    def set_path_objective(self, goal_state: 'State', box_key: 'str', agent_key: 'str'):
        self.heuristic = Heuristic(goal_state, box_key, agent_key)

    def get_from_frontier(self):
        leaf = heapq.heappop(self.frontier)[1]
        self.frontier_set.remove(leaf)
        return leaf

    def add_to_frontier(self, state):
        heapq.heappush(self.frontier, (self.heuristic.h_box_distance(state), state))
        self.frontier_set.add(state)

    def in_frontier(self, state):
        return state in self.frontier

    def frontier_count(self):
        return len(self.frontier)

    # Printing functions for debug purposes
    #todo
        
