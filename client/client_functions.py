from __future__ import print_function

from state import State
from action import Action
from agent import Agent

from action import ActionType


def get_box_key_by_position(row, col, state: 'State'):
    '''Return the key of a box at a given position'''
    for key, boxes in state.boxes.items():
        for i, box in enumerate(boxes):
            row_box, col_box, _ = box
            if row == row_box and col == col_box:
                return (key, i)
    return None


def check_action(actions, current_state: 'State', walls):
    '''Check if every agent's action is applicable in the current state and returns
    a list with the index of the agents' whose action are not applicable'''
    next_state = State(current_state)
    index_non_applicable = []
    is_applicable = True

    # defining a server-like state where we'll create fictive agent to keep track
    # of the previous agent position
    server_state = State(current_state)

    for i, action in enumerate(actions):
        i = str(i)
        row, col, color = current_state.agents[i]
        if action.action_type is ActionType.NoOp:
            continue
        else:
            new_agent_row = row + action.agent_dir.d_row
            new_agent_col = col + action.agent_dir.d_col

            if action.action_type is ActionType.Move:
                if server_state.is_free(walls, new_agent_row, new_agent_col):
                    server_state.agents[i + i] = (row, col, color)
                    server_state.agents[i] = (new_agent_row, new_agent_col, color)
                    next_state.agents[i] = (new_agent_row, new_agent_col, color)
                else:
                    index_non_applicable.append(i)
                    is_applicable = False
            elif action.action_type is ActionType.Push:
                box_key = get_box_key_by_position(new_agent_row, new_agent_col, next_state)
                new_box_row = new_agent_row + action.box_dir.d_row
                new_box_col = new_agent_col + action.box_dir.d_col
                if server_state.is_free(walls, new_box_row, new_box_col):
                    server_state.agents[i + i] = (row, col, color)
                    server_state.agents[i] = (new_agent_row, new_agent_col, color)
                    server_state.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, color)
                    next_state.agents[i] = (new_agent_row, new_agent_col, color)
                    next_state.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, color)
                else:
                    index_non_applicable.append(i)
                    is_applicable = False
            elif action.action_type is ActionType.Pull:
                box_row = row + action.box_dir.d_row
                box_col = col + action.box_dir.d_col
                box_key = get_box_key_by_position(box_row, box_col, next_state)

                new_box_row = box_row + action.box_dir.d_row * -1
                new_box_col = box_col + action.box_dir.d_col * -1

                if server_state.is_free(walls, new_agent_row, new_agent_col):
                    server_state.agents[i] = (new_agent_row, new_agent_col, color)
                    server_state.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, color)
                    next_state.agents[i] = (new_agent_row, new_agent_col, color)
                    next_state.boxes[box_key[0]][box_key[1]] = (new_box_row, new_box_col, color)
                else:
                    index_non_applicable.append(i)
                    is_applicable = False

    return index_non_applicable, next_state, is_applicable


def missing_goals(current_state, goal_state):
    '''Return the index of the agents that haven't reached their goal and the
    corresponding box, ex: {'0': ('A', (3, 9, 'red'))}'''
    current_boxes = current_state.boxes
    goal_boxes = goal_state.boxes

    missing_boxes = []
    for box_key in goal_boxes:
        for i, box in enumerate(goal_boxes[box_key]):
            try:
                if box not in current_boxes[box_key]:
                    missing_boxes.append((box_key, i))
            except KeyError:
                pass

    boxes_to_solve = {}
    for box in reversed(missing_boxes):
        for agent_key, agent_info in current_state.agents.items():
            box_color = current_state.boxes[box[0]][box[1]][2]
            agent_color = agent_info[2]
            if box_color == agent_color:
                boxes_to_solve[agent_key] = box

    return boxes_to_solve


def add_padding_actions(solution, nb_agents, current_state):
    '''adding NoOp action for agent that have already satisfied their goals'''
    max_len_sol = max(getLen(x) for x in solution)
    for i in range(nb_agents):
        try:
            padding_state = State(solution[i][-1])
            solution[i] += [padding_state] * (max_len_sol - len(solution[i]))
        except:
            padding_state = current_state
            solution[i] = [padding_state] * max_len_sol

        padding_state.action = Action(ActionType.NoOp, None, None)
    return solution


def getLen(obj):
    if obj is None:
        return 0
    else:
        return len(obj)


def reassign_goals(agents, current_state: 'State', goal_state: 'State', walls, client: 'Client', goals_missing=None):
    new_solution = []
    if goals_missing is not None:
        for j, agent in enumerate(agents):
            if agent.agent_key in goals_missing.keys():
                box_key = goals_missing[agent.agent_key]
                client.agents[j] = Agent(current_state, agent.agent_key)
                client.agents[j].assign_goal(goal_state, box_key)
                new_solution.append(client.agents[j].find_path_to_goal(walls))
            else:
                new_solution.append([])

    else:
        for j, agent in enumerate(agents):
            if agent.has_goal():
                box_key = client.agents[j].box_key
                client.agents[j] = Agent(current_state, agent.agent_key)
                client.agents[j].assign_goal(goal_state, box_key)
                new_solution.append(client.agents[j].find_path_to_goal(walls))
            else:
                new_solution.append([])
    return new_solution
