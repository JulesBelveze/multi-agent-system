from action import DIR_LOOKUP, ALL_ACTIONS, ActionType
import copy


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
        agent_dir = DIR_LOOKUP.get(agent_dir_key)
        box_dir = DIR_LOOKUP.get(box_dir_key)
        if agent_dir is None:
            return None

        # Find valid action based on supplied directions
        valid_action = None
        for action in ALL_ACTIONS:
            if action.agent_dir is agent_dir and action.box_dir is box_dir:
                valid_action = action
                break

        # Update agent and box positions based on action
        if valid_action is not None:
            child = self.create_child_state(valid_action)

            # Update box pos
            if box_dir is not None:
                c_box = self.boxes.get(box_key[0])[box_key[1]]
                n_box = c_box
                if action.action_type is ActionType.Push:
                    n_box = (c_box[0] + action.box_dir.d_row, c_box[1] + action.box_dir.d_col, c_box[2])

                elif action.action_type is ActionType.Pull:
                    n_box = (c_box[0] + action.box_dir.d_row * -1, c_box[1] + action.box_dir.d_col * -1, c_box[2])

                child.boxes[box_key[0]][box_key[1]] = n_box

            # Update agent pos
            c_agent = self.agents.get(agent_key)
            n_agent = (c_agent[0] + action.agent_dir.d_row, c_agent[1] + action.agent_dir.d_col, c_agent[2])
            if self.is_free(walls, n_agent[0], n_agent[1]):
                child.agents[agent_key] = n_agent

            return child
        return None

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