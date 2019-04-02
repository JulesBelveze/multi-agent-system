class Dir:
    N = S = E = W = None

    def __init__(self, name, d_row, d_col):
        self.name = name
        self.d_row = d_row
        self.d_col = d_col

    def __repr__(self):
        return self.name


Dir.N = Dir('N', -1, 0)
Dir.S = Dir('S', 1, 0)
Dir.E = Dir('E', 0, 1)
Dir.W = Dir('W', 0, -1)


class ActionType:
    Move = Push = Pull = Wait = None

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


ActionType.Move = ActionType('Move')
ActionType.Push = ActionType('Push')
ActionType.Pull = ActionType('Pull')
ActionType.Wait = ActionType('Wait')


class Action:
    def __init__(self, action_type, agent_dir, box_dir):
        self.action_type = action_type
        self.agent_dir = agent_dir
        self.box_dir = box_dir

        if box_dir is not None:
            self._repr = '[{}({},{})]'.format(action_type, agent_dir, box_dir)
        elif action_type == 'Wait':
            self._repr = '[Wait]'
        else:
            self._repr = '[{}({})]'.format(action_type, agent_dir)

    def __repr__(self):
        return self._repr


ALL_ACTIONS = []
for agent_dir in (Dir.N, Dir.S, Dir.E, Dir.W):
    ALL_ACTIONS.append(Action(ActionType.Move, agent_dir, None))
    # ALL_ACTIONS.append(Action(ActionType.Wait))
    for box_dir in (Dir.N, Dir.S, Dir.E, Dir.W):
        if agent_dir.d_row + box_dir.d_row != 0 or agent_dir.d_col + box_dir.d_col != 0:
            # If not opposite directions.
            ALL_ACTIONS.append(Action(ActionType.Push, agent_dir, box_dir))
        if agent_dir is not box_dir:
            # If not same directions.
            ALL_ACTIONS.append(Action(ActionType.Pull, agent_dir, box_dir))
