import random
import operator
import copy
from action import DIR_LOOKUP, OPPOSITE_DIR, ALL_ACTIONS, ActionType, get_direction_moving_coord, Direction


class State:
    def __init__(self, duplicate: 'State' = None, **kwargs):
        '''
        If duplicate is None: Creates an empty State.
        If duplicate is not None: Creates a copy of the duplicate state.
        ...
        The dictionaries of agents and boxes are of the form key: char, value:(row, col, color)
        '''
        self._hash = None
        if duplicate is None:
            self.agents = {}
            self.boxes = {}

            self.parent = None
            self.action = None

            self.depth = 0
        else:
            self.agents = dict(duplicate.agents)
            self.boxes = dict(copy.deepcopy(duplicate.boxes))

            self.parent = duplicate.parent
            self.action = duplicate.action

            self.depth = duplicate.depth

    def get_child(self, walls, agent_dir_key, agent_key, box_dir_key, box_key):
        agent_dir = None if agent_dir_key is None else DIR_LOOKUP.get(agent_dir_key[0])
        box_dir = None if box_dir_key is None else DIR_LOOKUP.get(box_dir_key[0])
        c_agent = self.agents.get(agent_key)
        child = None

        # Find valid action based on supplied directions
        valid_action = None
        for action in ALL_ACTIONS.get(agent_dir):
            if action.agent_dir is agent_dir and action.box_dir is box_dir:
                n_agent = (c_agent[0] + action.agent_dir.d_row, c_agent[1] + action.agent_dir.d_col, c_agent[2])

                if action.action_type is ActionType.Move and box_dir is None:
                    if self.is_free(walls, n_agent[0], n_agent[1]):
                        child = self.create_child_state(action)
                        child.agents[agent_key] = n_agent
                        break
                else:
                    c_box = self.boxes.get(box_key[0])[box_key[1]]
                    if action.action_type is ActionType.Push:
                        n_box = (c_box[0] + action.box_dir.d_row, c_box[1] + action.box_dir.d_col, c_box[2])

                        if self.can_agent_push_box(n_agent, c_box) and self.is_free(walls, n_box[0], n_box[1]):
                            child = self.create_child_state(action)
                            child.agents[agent_key] = n_agent
                            child.boxes[box_key[0]][box_key[1]] = n_box
                            break
                    elif action.action_type is ActionType.Pull:
                        n_box = (c_box[0] + action.box_dir.d_row * -1, c_box[1] + action.box_dir.d_col * -1, c_box[2])

                        if self.can_agent_pull_box(c_agent, n_box) and self.is_free(walls, n_agent[0], n_agent[1]):
                            child = self.create_child_state(action)
                            child.agents[agent_key] = n_agent
                            child.boxes[box_key[0]][box_key[1]] = n_box
                            break

        return child

    def get_children(self, walls, agent_key, box_key):
        '''
        Returns a list of child states attained from applying every applicable action in the current state
        '''
        children = []
        agent = self.agents.get(agent_key)
        box = self.boxes.get(box_key[0])[box_key[1]]

        for action in ALL_ACTIONS:
            child = None

            if action.action_type is ActionType.NoOp:
                child = self.create_child_state(action)
            else:
                new_agent = (agent[0] + action.agent_dir.d_row, agent[1] + action.agent_dir.d_col, agent[2])

                if action.action_type is ActionType.Move:
                    if self.is_free(walls, new_agent[0], new_agent[1]):
                        child = self.create_child_state(action)
                        child.agents[agent_key] = new_agent
                else:
                    if action.action_type is ActionType.Push:
                        new_box = (box[0] + action.box_dir.d_row, box[1] + action.box_dir.d_col, box[2])

                        if self.can_agent_push_box(new_agent, box) and self.is_free(walls, new_box[0], new_box[1]):
                            child = self.create_child_state(action)
                            child.agents[agent_key] = new_agent
                            child.boxes[box_key[0]][box_key[1]] = new_box
                    elif action.action_type is ActionType.Pull:
                        new_box = (box[0] + action.box_dir.d_row * -1, box[1] + action.box_dir.d_col * -1, box[2])

                        if self.can_agent_pull_box(agent, new_box) and self.is_free(walls, new_agent[0], new_agent[1]):
                            child = self.create_child_state(action)
                            child.agents[agent_key] = new_agent
                            child.boxes[box_key[0]][box_key[1]] = new_box

            if child is not None:
                children.append(child)
        return children

    def create_child_state(self, action):
        child = State(self)
        child.parent = self
        child.depth += 1
        child.action = action
        return child

    def get_random_free_cell(self, max_row, max_col, walls, max_len=5):
        '''function returning a random free cell in the map'''
        is_free = False
        while not is_free:
            random_row, random_col = random.randint(1, max_row - 1), random.randint(1, max_col - 1)
            is_free = self.is_free(walls, random_row, random_col)
        return random_row, random_col

    def get_free_neighbouring_cell(self, walls, row, col):
        '''get a free neighbouring cell from a given one'''
        moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for move in moves:
            new_row, new_col = tuple(map(operator.add, move, (row, col)))
            # no need to check the if the value is inside the map because it will be
            # a wall if so
            if self.is_free(walls, new_row, new_col):
                return new_row, new_col

        return None

    def is_free(self, walls, row, col):
        '''Function checking if a given position is free'''
        # checking if any wall is present
        if walls[row][col]:
            return False
        # checking if any agent is present
        for key, agent in self.agents.items():
            if row == agent[0] and col == agent[1]:
                return False
        # checking if any box is present
        for key, boxes in self.boxes.items():
            for box in boxes:
                if row == box[0] and col == box[1]:
                    return False
        return True

    def is_no_object(self, row, col):
        '''same without checking the presence of walls'''
        # checking if any agent is present
        for key, agent in self.agents.items():
            if row == agent[0] and col == agent[1]:
                return False, "agent", self._get_agent_key_by_color(agent[2])
        # checking if any box is present
        for key, boxes in self.boxes.items():
            for box in boxes:
                if row == box[0] and col == box[1]:
                    return False, "box", self._get_box_key_by_position(box[0], box[1])
        return True, None, None

    def get_freeing_actions(self, agent_key, walls):
        '''finding actions to free others agents.
        Agents will be free as soon as the blocking has three empty cells around him'''
        moves, list_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)], []
        agent_row, agent_col, agent_color = self.agents[agent_key]

        lambda_is_free = lambda x: self.is_free(walls, x[0], x[1])
        is_blocking = True
        previous_direction = (1, 0)  # used to try the same direction at first
        while is_blocking:

            next_pos = [(elt[0] + agent_row, elt[1] + agent_col) for elt in moves]
            free_positions = list(map(lambda_is_free, next_pos))

            vertically_free, horizontally_free = free_positions[:2], free_positions[2:]

            if sum(horizontally_free) == 1 and sum(vertically_free) == 1:
                move = moves[2 + horizontally_free.index(True)]
                dir = get_direction_moving_coord(move)
                previous_dir = get_direction_moving_coord(previous_direction)
                if dir == OPPOSITE_DIR[previous_dir]:
                    move = moves[vertically_free.index(True)]
                # print(DIR_MIRROR[previous_direction.name])
            elif sum(horizontally_free) == 1:
                move = moves[2 + horizontally_free.index(True)]
            elif sum(horizontally_free) == 2:
                move = moves[2] if previous_direction == moves[2] else moves[3]
            elif sum(vertically_free) == 1:
                move = moves[vertically_free.index(True)]
            elif sum(vertically_free) == 2:
                move = moves[0] if previous_direction == moves[0] else moves[1]
            # print(move)
            previous_direction = move
            agent_row, agent_col = move[0] + agent_row, move[1] + agent_col
            list_directions.append(get_direction_moving_coord(move))

            if sum(vertically_free) + sum(horizontally_free) > 2:
                is_blocking = False
        return list_directions

    def _get_box_key_by_position(self, row, col):
        '''Return the key of a box at a given position'''
        for key, boxes in self.boxes.items():
            for i, box in enumerate(boxes):
                row_box, col_box, _ = box
                if row == row_box and col == col_box:
                    return key, i
        return None

    def _get_agent_key_by_color(self, color):
        for key, item in self.agents.items():
            if item[2] == color:
                return key, item

    def can_agent_push_box(self, new_agent, box):
        return box[0] == new_agent[0] and box[1] == new_agent[1]

    def can_agent_pull_box(self, agent, new_box):
        return new_box[0] == agent[0] and new_box[1] == agent[1]

    def is_agent_at_box(self, agent_row: 'int', agent_col: 'int', box_key: 'str'):
        box = self.boxes.get(box_key[0])[box_key[1]]
        return box[0] == agent_row and box[1] == agent_col

    def is_initial_state(self):
        '''Checking if state is the initial one by checking if it has a parent state'''
        return self.parent is None

    def is_goal_state(self, goal_state, box_key: 'str' = None):
        '''Check if current box dictionary (or individual box) matches goal box dictionary'''
        if box_key is not None:
            return self.boxes.get(box_key[0])[box_key[1]] == goal_state.boxes.get(box_key[0])[box_key[1]]
        return self.boxes == goal_state.boxes

    def extract_plan(self):
        plan = []
        state = self
        while not state.is_initial_state():
            plan.append(state)
            state = state.parent
        plan.reverse()
        return plan

    def __repr__(self):
        lines = []
        for i, agent in self.agents.items():
            line = []
            line.append("Agent {} [{}, {}, {}]: ".format(i, agent[0], agent[1], agent[2]))

            for j, boxes in self.boxes.items():
                for box in boxes:
                    # Make sure boxes are grouped by colour
                    if box[2] == agent[2]:
                        line.append("{} [{}, {}] ".format(j, box[0], box[1]))

            lines.append(''.join(line))
        lines.append("Action: {}, Depth: {}".format(self.action, self.depth))
        return ' '.join(lines)
