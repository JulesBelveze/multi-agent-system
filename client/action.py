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
ActionType.Wait = ActionType("Wait")

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
        else:
            self._repr = '{}({},{})'.format(self.action_type, self.agent_dir, self.box_dir)

    def __repr__(self):
        return self._repr

# All possible actions
ALL_ACTIONS = []

# Populate
for agent_dir in (Direction.N, Direction.E, Direction.S, Direction.W):
    ALL_ACTIONS.append(Action(ActionType.Move, agent_dir, None))

    for action in (ActionType.Push, ActionType.Pull):
        for box_dir in (Direction.N, Direction.E, Direction.S, Direction.W):
            if agent_dir.d_row + box_dir.d_row != 0 or agent_dir.d_col + box_dir.d_col != 0:
                ALL_ACTIONS.append(Action(action, agent_dir, box_dir))
ALL_ACTIONS.append(Action(ActionType.Wait, None, None))