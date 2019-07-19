from state import State
from client_functions import get_box_color_by_box_letter, get_agent_key_by_color
import operator

class Cooperation:
    def __init__(self, current_state: 'State', goal_state: 'State', walls):
        self.sender = None
        self.receiver = None
        self.queries = []
        self.state = current_state
        self.goal_state = goal_state
        self.walls = walls

    def get_needed_coop(self):
        boxes_on_goal, screwed_boxes1 = self.is_any_box_on_goal()
        agents_on_goal, screwed_boxes2 = self.is_any_agent_on_goal()
        blocking_agents = self.is_any_agent_blocking()

        # is any box on goal
        for (key_box, index_box), key_box_screwed in zip(boxes_on_goal, screwed_boxes1):
            box_color = get_box_color_by_box_letter(self.state.boxes, key_box)
            agent_in_charge = get_agent_key_by_color(box_color, self.state.agents)

            box_color_screwed = get_box_color_by_box_letter(self.state.boxes, key_box_screwed)
            agent_screwed = get_agent_key_by_color(box_color_screwed, self.state.agents)

            query = "agent " + agent_in_charge[0] + " box " + key_box + "," + str(
                index_box) + "," + box_color + " | agent " + agent_screwed[0] + " wait"
            self.queries.append(query)

        # is any agent on goal
        for key_agent, key_box_screwed in zip(agents_on_goal, screwed_boxes2):
            box_color_screwed = get_box_color_by_box_letter(self.state.boxes, key_box_screwed)
            agent_screwed = get_agent_key_by_color(box_color_screwed, self.state.agents)

            query = "agent " + key_agent + " - | agent " + agent_screwed[0]
            self.queries.append(query)

        # is any agent blocking
        for key_agent in blocking_agents:
            query = "agent " + key_agent + " blocking | agent *"
            self.queries.append(query)

        return self.queries

    def is_any_agent_blocking(self):
        '''checking if any agent is blocking the way'''
        posible_dir = [(1,0), (-1,0), (0,1), (0,-1)] # S, N, E, W
        blocking_agents = []
        positions_agents = {key: (elt[0], elt[1]) for key, elt in self.state.agents.items()}

        for key_agent, pos in positions_agents.items():
            is_free_neighbouring_cells = []
            for dir in posible_dir:
                new_row, new_col = tuple(map(operator.add, pos, dir))
                is_free_neighbouring_cells.append(self.state.is_free(self.walls, new_row, new_col))

            # meaning the agent cannot move
            if sum(is_free_neighbouring_cells) == 0:
                continue
            # meaning the agent is either vertically or horizontally trapped
            elif sum(is_free_neighbouring_cells[:2]) == 0 or sum(is_free_neighbouring_cells) == 0:
                blocking_agents.append(key_agent)

        return blocking_agents



    def is_any_box_blocking(self):
        raise NotImplementedError

    def is_any_box_on_goal(self):
        '''checking if any box is on a goal cell'''
        state_boxes = self.state.boxes
        goal_state_boxes = self.goal_state.boxes

        boxes_on_goal, screwed_boxes = [], []
        for key_goal, item_goal in goal_state_boxes.items():
            positions_goal = [(elt[0], elt[1]) for elt in item_goal]  # getting rid of the color

            for key_state, item_state in state_boxes.items():
                positions_boxes = [(elt[0], elt[1]) for elt in item_state]  # getting rid of the color

                # checking if there is an unwanted box on a goal cell
                if len(set(positions_goal) & set(positions_boxes)) > 0 and key_goal != key_state:
                    intersection = list(set(positions_boxes) & set(positions_goal))
                    boxes_on_goal.extend([(key_state, positions_boxes.index(elt)) for elt in intersection])
                    screwed_boxes.append(key_goal)

        return boxes_on_goal, screwed_boxes

    def is_any_agent_on_goal(self):
        '''checking if any agent is on a goal cell'''
        state_agents = self.state.agents
        goal_state_boxes = self.goal_state.boxes

        agents_on_goal, screwed_boxes = [], []
        for key_goal, item_goal in goal_state_boxes.items():
            positions_goal = [(elt[0], elt[1]) for elt in item_goal]  # getting rid of the color

            for key_agent, agent in state_agents.items():
                position_agent = (agent[0], agent[1])  # getting rid of the color

                if position_agent in positions_goal:
                    agents_on_goal.append(key_agent)
                    screwed_boxes.append(key_goal)

        return agents_on_goal, screwed_boxes
