from action import ALL_ACTIONS, ActionType
#from action import ALL_ACTIONS, ActionType


class State:
    def __init__(self, copy: 'State' = None, **kwargs):
        '''
        If copy is None: Creates an empty State.
        If copy is not None: Creates a copy of the copy state.

        The lists boxes, and goals are indexed from top-left of the level, row-major order (row, col).
               Col 0  Col 1  Col 2  Col 3
        Row 0: (0,0)  (0,1)  (0,2)  (0,3)  ...
        Row 1: (1,0)  (1,1)  (1,2)  (1,3)  ...
        Row 2: (2,0)  (2,1)  (2,2)  (2,3)  ...
        ...
        The dictionaries of agents and boxes are of the form key: char, value:(row, col, color)

        Note: The state should be considered immutable after it has been hashed, e.g. added to a dictionary!
        '''
        self._hash = None
        if copy is None:
            self.agents = {}
            self.boxes = {}

            self.parent = None
            self.action = None

            self.depth = 0
        else:
            self.agents = dict(copy.agents)
            self.boxes = dict(copy.boxes)

            self.parent = copy.parent
            self.action = copy.action

            self.depth = copy.depth

    def get_children(self, walls, agent_key, box_key):
        '''
        Returns a list of child states attained from applying every applicable action in the current state
        '''
        children = []

        agent = self.agents.get(agent_key)
        for action in ALL_ACTIONS:
            if action.action_type is ActionType.NoOp:
                child = State(self)
                child.parent = self
                child.action = action
                child.depth += 1
                children.append(child)
            else:
                new_agent_row = agent[0] + action.agent_dir.d_row
                new_agent_col = agent[1] + action.agent_dir.d_col

                if action.action_type is ActionType.Move:
                    if self.is_free(walls, new_agent_row, new_agent_col):
                        child = State(self)
                        child.agents[agent_key] = (new_agent_row, new_agent_col, agent[2])
                        child.parent = self
                        child.action = action
                        child.depth += 1
                        children.append(child)

                elif action.action_type is ActionType.Push and box_key is not None:
                    if self.is_agent_at_box(new_agent_row, new_agent_col, box_key):
                        new_box_row = new_agent_row + action.box_dir.d_row
                        new_box_col = new_agent_col + action.box_dir.d_col
                        if self.is_free(walls, new_box_row, new_box_col):
                            child = State(self)
                            child.agents[agent_key] = (new_agent_row, new_agent_col, agent[2])
                            child.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, (child.boxes.get(box_key[0])[box_key[1]])[2])
                            child.parent = self
                            child.action = action
                            child.depth += 1
                            children.append(child)

                elif action.action_type is ActionType.Pull and box_key is not None:
                    if self.is_free(walls, new_agent_row, new_agent_col):
                        new_box_row = agent[0] + action.box_dir.d_row
                        new_box_col = agent[1] + action.box_dir.d_col
                        if self.is_agent_at_box(new_box_row, new_box_col, box_key):
                            child = State(self)
                            child.agents[agent_key] = (new_agent_row, new_agent_col, agent[2])
                            child.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, (child.boxes.get(box_key[0])[box_key[1]])[2])
                            child.parent = self
                            child.action = action
                            child.depth += 1
                            children.append(child)
        return children

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

    def is_agent_at_box(self, agent_row: 'int', agent_col: 'int', box_key: 'str'):
        box = self.boxes.get(box_key[0])[box_key[1]]
        return box[0] == agent_row and box[1] == agent_col

    # def right_box_at(self, row, col, agent_color):
    #     '''Function checking if an agent can push a box and returning the right box if yes.
    #     Meaning checking the location and the color of the boxes'''
    #     for box, box_values in self.boxes.items():
    #         if row == box_values[0] and col == box_values[1] and agent_color == box_values[2]:
    #             return True, box
    #     return False, None

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
