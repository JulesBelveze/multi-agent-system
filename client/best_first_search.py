import heapq
import memory
from time import perf_counter


class BestFirst():
    def __init__(self, heuristic):
        self.explored = set()
        self.start_time = perf_counter()
        self.heuristic = heuristic
        self.frontier = []
        self.frontier_set = set()
        heapq.heapify(self.frontier)

    def add_to_explored(self, state: 'State'):
        self.explored.add(state)

    def is_explored(self, state: 'State') -> 'bool':
        return state in self.explored

    def explored_count(self) -> 'int':
        return len(self.explored)

    def time_spent(self) -> 'float':
        return perf_counter() - self.start_time

    def search_status(self) -> 'str':
        return '#Explored: {:6}, #Frontier: {:6}, #Generated: {:6}, Time: {:3.2f} s, Alloc: {:4.2f} MB, MaxAlloc: {:4.2f} MB'.format(
            self.explored_count(), self.frontier_count(), self.explored_count() + self.frontier_count(),
            self.time_spent(), memory.get_usage(), memory.max_usage)

    def get_and_remove_leaf(self):
        leaf = heapq.heappop(self.frontier)[1]
        self.frontier_set.remove(leaf)
        return leaf

    def add_to_frontier(self, state):
        heapq.heappush(self.frontier, (self.heuristic.f(state), state))
        self.frontier_set.add(state)
        pass

    def in_frontier(self, state):
        return state in self.frontier_set

    def frontier_count(self):
        return len(self.frontier)

    def frontier_empty(self):
        return self.frontier_count() == 0

    def __repr__(self):
        return 'Best-frist using {}'.format(self.heuristic)
    