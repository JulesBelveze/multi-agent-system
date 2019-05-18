class Direction:
    N = E = S = W = None
    '''
    Do not instantiate outside this file
    '''
    def __init__(self, name: 'str', d_row: 'int', d_col: 'int'):
        self.name = name
        self.d_row = d_row
        self.d_col = d_col

    def __repr__(self):
        return self.name

Direction.N = Direction('N', -1, 0)
Direction.E = Direction('E', 0, 1)
Direction.S = Direction('S', 1, 0)
Direction.W = Direction('W', 0, -1)

class ActionType:
    Move = Push = Pull = None
    '''
    Do not instantiate outside this file
    '''
    def __init__(self, name: 'str'):
        self.name = name

    def __repr__(self):
        return self.name

ActionType.Move = ActionType("Move")
ActionType.Push = ActionType("Push")
ActionType.Pull = ActionType("Pull")
ActionType.NoOp = ActionType("NoOp")

class Action:
    '''
    Do not instantiate outside this file
    '''
    def __init__(self, action_type: 'ActionType', agent_dir: 'Direction', box_dir: 'Direction'):
        self.action_type = action_type
        self.agent_dir = agent_dir
        self.box_dir = box_dir
        if self.action_type == ActionType.Move:
            self._repr = '{}({})'.format(self.action_type, self.agent_dir)
        elif self.action_type == ActionType.NoOp:
            self._repr = '{}'.format(self.action_type)
        else:
            self._repr = '{}({},{})'.format(self.action_type, self.agent_dir, self.box_dir)

    def __repr__(self):
        return self._repr


# All possible directions
ALL_DIRECTIONS = {}
ALL_DIRECTIONS[Direction.N.name] = (Direction.N.d_row, Direction.N.d_col)
ALL_DIRECTIONS[Direction.E.name] = (Direction.E.d_row, Direction.E.d_col)
ALL_DIRECTIONS[Direction.S.name] = (Direction.S.d_row, Direction.S.d_col)
ALL_DIRECTIONS[Direction.W.name] = (Direction.W.d_row, Direction.W.d_col)

# Get direction class based on name of direction
DIR_LOOKUP = {}
DIR_LOOKUP[Direction.N.name] = Direction.N
DIR_LOOKUP[Direction.E.name] = Direction.E
DIR_LOOKUP[Direction.S.name] = Direction.S
DIR_LOOKUP[Direction.W.name] = Direction.W

# Map opposite directions for quick lookup
DIR_MIRROR = {}
DIR_MIRROR[Direction.N.name] = Direction.S.name
DIR_MIRROR[Direction.E.name] = Direction.W.name
DIR_MIRROR[Direction.S.name] = Direction.N.name
DIR_MIRROR[Direction.W.name] = Direction.E.name

# All possible actions
ALL_ACTIONS = []

# Populate
for agent_dir in (Direction.N, Direction.E, Direction.S, Direction.W):
    ALL_ACTIONS.append(Action(ActionType.Move, agent_dir, None))

    for action in (ActionType.Push, ActionType.Pull):
        for box_dir in (Direction.N, Direction.E, Direction.S, Direction.W):
            if action is ActionType.Push:
                # If not opposite directions
                if agent_dir.d_row + box_dir.d_row != 0 or agent_dir.d_col + box_dir.d_col != 0:
                    ALL_ACTIONS.append(Action(action, agent_dir, box_dir))
            else:
                # If not the same directions
                if agent_dir is not box_dir:
                    ALL_ACTIONS.append(Action(action, agent_dir, box_dir))
ALL_ACTIONS.append(Action(ActionType.NoOp, None, None))