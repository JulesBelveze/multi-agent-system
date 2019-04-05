from abc import ABCMeta, abstractmethod

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

    def get_from_frontier(self):
        leaf = self.frontier.pop(0)
        self.frontier_set.remove(leaf)
        return leaf

    def add_to_frontier(self, state):
        #todo: add heuristic and finish pathing algorithm
        self.frontier.append(state)
        self.frontier_set.add(state)

    def in_frontier(self, state):
        return state in self.frontier

    def frontier_count(self):
        return len(self.frontier)
        