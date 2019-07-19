from state import State
from client_functions import get_box_color_by_box_letter, get_agent_key_by_color


class Cooperation:
    def __init__(self, current_state: 'State', goal_state: 'State'):
        self.sender = None
        self.receiver = None
        self.queries = []
        self.state = current_state
        self.goal_state = goal_state

    def get_needed_coop(self):
        boxes_on_goal, screwed_boxes1 = self.is_any_box_on_goal()
        agents_on_goal, screwed_boxes2 = self.is_any_agent_on_goal()

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

        return self.queries

    def is_any_agent_blocking(self):
        raise NotImplementedError

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
        states_agents = self.state.agents
        goal_state_boxes = self.goal_state.boxes

        agents_on_goal, screwed_boxes = [], []
        for key_goal, item_goal in goal_state_boxes.items():
            positions_goal = [(elt[0], elt[1]) for elt in item_goal]  # getting rid of the color

            for key_agent, agent in states_agents.items():
                position_agent = (agent[0], agent[1])  # getting rid of the color

                if position_agent in positions_goal:
                    agents_on_goal.append(key_agent)
                    screwed_boxes.append(key_goal)

        return agents_on_goal, screwed_boxes
