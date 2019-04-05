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
            self.agents = copy.agents
            self.boxes = copy.boxes

            self.parent = copy.parent
            self.action = copy.action

            self.depth = copy.depth

    def get_children(self, walls, agent_key):
        '''
        Returns a list of child states attained from applying every applicable action in the current state.
        The order of the actions is random.
        '''
        children = []

        agent = self.agents.get(agent_key)
        for action in ALL_ACTIONS:
            new_row = agent[0] + action.agent_dir.d_row
            new_col = agent[1] + action.agent_dir.d_col

            if self.is_free(walls, new_row, new_col):
                child = State(self)

                if action.action_type is ActionType.Move:
                    child.agents.get(agent_key)[0] = new_row
                    child.agents.get(agent_key)[1] = new_col
                    child.parent = self
                    child.action = action
                    child.depth += 1
                    children.append(child)

                elif action.action_type is ActionType.Push:
                    child.agents.get(agent_key)[0] = new_row
                    child.agents.get(agent_key)[1] = new_col
                    child.parent = self
                    child.action = action
                    child.depth += 1

                elif action.action_type is ActionType.Pull:
                    child.agents.get(agent_key)[0] = new_row
                    child.agents.get(agent_key)[1] = new_col
                    child.parent = self
                    child.action = action
                    child.depth += 1

                elif action.action_type is ActionType.Wait:
                    child.parent = self
                    child.action = action
                    child.depth += 1

                children.append(child)

        '''
                elif action.action_type is ActionType.Push:
                    is_right_box_at, right_box = self.right_box_at(new_row_ag, new_col_ag, agent_color)
                    if is_right_box_at:
                        new_box_row = new_row_ag + action.box_dir.d_row
                        new_box_col = new_col_ag + action.box.dir.d_col
                        if self.is_free(walls, new_box_row, new_box_col):
                            child = State(self)
                            child.agents = new_agents
                            child.boxes[right_box][0] = new_box_row
                            child.boxes[right_box][1] = new_box_col
                            child.parent = self
                            child.action = action
                            child.g += 1
                            children.append(child)

                # checks for action Pull
                elif action.action_type is ActionType.Pull:
                    is_right_box_at, right_box = self.right_box_at(new_box_row + action.box_dir.d_row,
                                                                   new_box_col + action.box_dir.d_col)
                    if is_right_box_at:
                        new_box_row = self.agents[agent][0]
                        new_box_col = self.agents[agent][1]
                        if self.is_free(walls, new_row_ag, new_row_ag):
                            child = State(self)
                            child.agents = new_agents
                            child.boxes[right_box][0] = new_box_row
                            child.boxes[right_box][1] = new_box_col
                            child.parent = self
                            child.action = action
                            child.g += 1
                            children.append(child)
                elif action.action_type is ActionType.Wait:
                    child = State(self)
                    child.parent = self
                    child.action = action
                    child.g += 1
                    children.append(child)

        return children'''

    def is_free(self, walls, row, col):
        '''Function checking if a given position is free'''
        # checking if any wall is present
        if walls[row][col]:
            return False
        # checking if any agent is present
        for agent in self.agents:
            if row == agent[0] and col == agent[1]:
                return False
        # checking if any box is present
        for box in self.boxes:
            if row == box[0] and col == box[1]:
                return False
        return True

    def right_box_at(self, row, col, agent_color):
        '''Function checking if an agent can push a box and returning the right box if yes.
        Meaning checking the location and the color of the boxes'''
        for box, box_values in self.boxes.items():
            if row == box_values[0] and col == box_values[1] and agent_color == box_values[2]:
                return True, box
        return False, None

    def is_initial_state(self):
        '''Checking if state is the initial one by checking if it has a parent state'''
        return self.parent is None

    def is_goal_state(self, boxes_goal):
        '''Checking if state is goal by checking if the box dictionary is the same than
        the one of the goal state'''
        return self.boxes == boxes_goal

    def extract_plan(self):
        plan = []
        state = self
        while not state.is_initial_state():
            plan.append(state)
            state = state.parent
        plan.reverse()
        return plan

