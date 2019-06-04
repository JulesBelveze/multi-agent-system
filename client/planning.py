import copy
from collections import defaultdict
from state import State
from operator import itemgetter

from message import msg_server_err
from message import msg_server_comment
from message import msg_server_action

class Plan:
    def __init__(self, initial_state: 'State', goal_state: 'State'):
        self.action_orders = defaultdict(list)
        self.unique_action_count = 0
        self.actions = {}
        self.subgoals = []
        self.links = []

        self.create_action_blueprints(initial_state, goal_state)

        # Instantiate start and end actions
        end_action = self.actions.get("End").instantiate_from_blueprint(self.unique_action_count)
        box_keys = list(goal_state.boxes.keys())
        agent_keys = list(goal_state.agents.keys())
        b_curr = 0
        b_key = 0
        a_key = 0
        for precon in end_action.preconditions:
            context_entity = None
            for arg in precon.arguments:
                if arg.name == "box":
                    arg.value = (box_keys[b_key], b_curr)
                    context_entity = goal_state.boxes.get(box_keys[b_key])[b_curr]
                    if b_curr < len(goal_state.boxes.get(box_keys[b_key])) - 1:
                        b_curr += 1
                    else:
                        b_key += 1
                        b_curr = 0
                elif arg.name == "agent":
                    arg.value = agent_keys[a_key]
                    context_entity = goal_state.agents.get(agent_keys[a_key])
                    a_key += 1
                elif arg.name == "row":
                    arg.value = context_entity[0]
                elif arg.name == "col":
                    arg.value = context_entity[1]
            self.subgoals.append(PlanSubGoal(precon, end_action))

        self.unique_action_count += 1
        start_action = self.actions.get("Start").instantiate_from_blueprint(self.unique_action_count)
        box_keys = list(initial_state.boxes.keys())
        agent_keys = list(initial_state.agents.keys())
        b_curr = 0
        b_key = 0
        a_key = 0
        a_pair_count = 0
        for eff in start_action.effects:
            context_entity = None
            for arg in eff.arguments:
                if arg.name == "box":
                    arg.value = (box_keys[b_key], b_curr)
                    context_entity = initial_state.boxes.get(box_keys[b_key])[b_curr]
                    if b_curr < len(initial_state.boxes.get(box_keys[b_key])) - 1:
                        b_curr += 1
                    else:
                        b_key += 1
                        b_curr = 0
                elif arg.name == "agent":
                    arg.value = agent_keys[a_key]
                    context_entity = initial_state.agents.get(agent_keys[a_key])
                    a_pair_count += 1
                    if a_pair_count % 2 == 0:
                        a_pair_count = 0
                        a_key += 1
                elif arg.name == "row":
                    arg.value = context_entity[0]
                elif arg.name == "col":
                    arg.value = context_entity[1]

        # Create ordering constraint
        ordering = PlanActionOrdering(start_action, end_action)
        self.action_orders[start_action.action_id].append((end_action.action_id, ordering))
        self.unique_action_count += 1

        msg_server_comment("Starting subgoals:")
        for subgoal in self.subgoals:
            msg_server_comment(subgoal.state)

    '''
    State blueprints are created in pairs (positive, negative).
    Fetching pair of states can be done by name. Index of list corresponds to whether state is true or not: 0 - False, 1 - True
    '''
    def create_plan_state_blueprints(self):
        state_blueprints = {}
        state_blueprints["Detached"] = [PlanState("Detached", False, False, ["agent"])]
        state_blueprints["Detached"].append(PlanState("Detached", True, False, ["agent"]))

        state_blueprints["AttachedTo"] = [PlanState("AttachedTo", False, False, ["agent", "box"])]
        state_blueprints["AttachedTo"].append(PlanState("AttachedTo", True, False, ["agent", "box"]))

        state_blueprints["NextTo"] = [PlanState("NextTo", False, False, ["agent", "box"])]
        state_blueprints["NextTo"].append(PlanState("NextTo", True, False, ["agent", "box"]))

        state_blueprints["BoxAtLocation"] = [PlanState("BoxAtLocation", False, True, ["box", "row", "col"])]
        state_blueprints["BoxAtLocation"].append(PlanState("BoxAtLocation", True, True, ["box", "row", "col"]))

        state_blueprints["AgentAtLocation"] = [PlanState("AgentAtLocation", False, True, ["agent", "row", "col"])]
        state_blueprints["AgentAtLocation"].append(PlanState("AgentAtLocation", True, True, ["agent", "row", "col"]))

        state_blueprints["BoxInGoal"] = [PlanState("BoxInGoal", False, False, ["box", "goal"])]
        state_blueprints["BoxInGoal"].append(PlanState("BoxInGoal", True, False, ["box", "goal"]))

        return state_blueprints

    def create_action_blueprints(self, initial_state: 'State', goal_state: 'State'):
        # States
        plan_states = self.create_plan_state_blueprints()

        # Attach / Detach
        new_action = PlanAction("AttachTo")
        new_action.define_blueprint_arguments(["agent", "box"])
        new_action.define_blueprint_preconditions([plan_states.get("Detached")[1], plan_states.get("NextTo")[0]])
        new_action.define_blueprint_effects([plan_states.get("AttachedTo")[1]])
        self.actions["AttachTo"] = new_action

        new_action = PlanAction("DetachFrom")
        new_action.define_blueprint_arguments(["agent", "box"])
        new_action.define_blueprint_preconditions([plan_states.get("AttachedTo")[1]])
        new_action.define_blueprint_effects([plan_states.get("Detached")[1]])
        self.actions["DetachFrom"] = new_action

        # Agent movement actions
        new_action = PlanAction("MoveAgentNextTo")
        new_action.define_blueprint_arguments(["agent", "box"])
        new_action.define_blueprint_preconditions([plan_states.get("Detached")[1], plan_states.get("NextTo")[0]])
        new_action.define_blueprint_effects([plan_states.get("NextTo")[1]])
        self.actions["MoveAgentNextTo"] = new_action

        new_action = PlanAction("MoveAgentTo")
        new_action.define_blueprint_arguments(["agent", "row", "col"])
        new_action.define_blueprint_preconditions([plan_states.get("Detached")[1]])
        new_action.define_blueprint_effects([plan_states.get("AgentAtLocation")[1]])
        self.actions["MoveAgentTo"] = new_action

        # Box movement
        new_action = PlanAction("MoveBoxTo")
        new_action.define_blueprint_arguments(["agent", "box", "row", "col"])
        new_action.define_blueprint_preconditions([plan_states.get("AttachedTo")[1]])
        new_action.define_blueprint_effects([plan_states.get("BoxAtLocation")[1]])
        self.actions["MoveBoxTo"] = new_action

        # Start
        new_action = PlanAction("Start")
        effect_list = []
        for agent in initial_state.agents.items():
            effect_list.append(plan_states.get("Detached")[1])
            effect_list.append(plan_states.get("AgentAtLocation")[1])
        for boxes in initial_state.boxes.items():
            for box in boxes[1]:
                effect_list.append(plan_states.get("BoxAtLocation")[1])
        new_action.define_blueprint_effects(effect_list)
        self.actions["Start"] = new_action

        # End
        new_action = PlanAction("End")
        precon_list = []
        for agent in goal_state.agents.items():
            precon_list.append(plan_states.get("AgentAtLocation")[1])
        for boxes in goal_state.boxes.items():
            for box in boxes[1]:
                precon_list.append(plan_states.get("BoxAtLocation")[1])
        new_action.define_blueprint_preconditions(precon_list)
        self.actions["End"] = new_action

    def complete_plan(self, current_state: 'State', agent_key):
        open_subgoals = self.subgoals
        while(len(open_subgoals) > 0):
            subgoal = open_subgoals.pop(0)

            # Find action that satisfies subgoal
            possible_actions = []
            for act in self.actions.items():
                if not act[0] == "Start" and not act[0] == "End":
                    if act[1].find_effect(subgoal.state):
                        possible_actions.append(act)

            if len(possible_actions) == 0:
                msg_server_err("Could not find action satisfying subgoal: {}".format(subgoal.state.__repr__()))
                break

            for sat_action in possible_actions:

                # Instantiate new action
                sat_action = sat_action[1].instantiate_from_blueprint(self.unique_action_count)
                box_key = [it for it in subgoal.state.arguments if it.name == "box"]
                if len(box_key) > 0:
                    box_key = box_key[0].value
                else:
                    box_key = [it for it in subgoal.action.arguments if it.name == "box"][0].value
                sat_action.define_arguments(sat_action.arguments, current_state, agent_key, box_key)
                for precon in sat_action.preconditions:
                    sat_action.define_arguments(precon.arguments, current_state, agent_key, box_key)
                for eff in sat_action.effects:
                    sat_action.define_arguments(eff.arguments, current_state, agent_key, box_key)

                # Add open preconditions and establish ordering
                for precon in sat_action.preconditions:
                    if not precon.is_positional:
                        open_subgoals.append(PlanSubGoal(precon, sat_action))

                if not self.action_orders.get(sat_action):
                    ordering = PlanActionOrdering(sat_action, subgoal.action)
                    self.action_orders[sat_action.action_id].append((subgoal.action.action_id, ordering))
                    self.unique_action_count += 1

        self.topological_sort()

    def topological_sort(self):
        #TODO: Doesn't behave correctly
        visited = [False] * self.unique_action_count
        stack = []

        for i in range(self.unique_action_count):
            if visited[i] == False:
                self.topological_helper(i, visited, stack)

        # Print result
        while len(stack) > 0:
            index = stack.pop()
            values = self.action_orders[index]
            if len(values) > 0:
                print(values[0][1].before.__repr__())


    def topological_helper(self, index, visited, stack):
        visited[index] = True

        for i in self.action_orders[index]:
            if visited[i[0]] == False:
                self.topological_helper(i[0], visited, stack)

        stack.insert(0, index)

class PlanAction:
    def __init__(self, action_name):
        self.name = action_name
        self.arguments = []
        self.preconditions = []
        self.effects = []
        self.is_blueprint = True
        self.action_id = 0

    def define_blueprint_arguments(self, argument_names):
        if self.is_blueprint:
            for arg in argument_names:
                self.arguments.append(Argument(arg, None))

    def define_blueprint_preconditions(self, preconditions):
        if self.is_blueprint:
            for precon in preconditions:
                self.preconditions.append(precon)

    def define_blueprint_effects(self, effects):
        if self.is_blueprint:
            for eff in effects:
                self.effects.append(eff)

    def instantiate_from_blueprint(self, action_id):
        if self.is_blueprint:
            action = PlanAction(self.name)
            for arg in self.arguments:
                action.arguments.append(copy.deepcopy(arg))
            for precon in self.preconditions:
                action.preconditions.append(copy.deepcopy(precon))
            for eff in self.effects:
                action.effects.append(copy.deepcopy(eff))

            action.is_blueprint = False
            action.action_id = action_id
            return action

    def define_arguments(self, target_list, current_state, agent_key, box_key):
        context = None
        for arg in target_list:
            if arg.name == "agent":
                context = current_state.agents.get(agent_key)
                arg.value = agent_key
            elif arg.name == "box":
                context = current_state.boxes.get(box_key[0])[box_key[1]]
                arg.value = box_key
            elif arg.name == "row":
                arg.value = context[0]
            elif arg.name == "col":
                arg.value = context[1]

    def find_effect(self, plan_state: 'PlanState'):
        for eff in self.effects:
            if eff == plan_state:
                return True
        return False

    def __repr__(self):
        arguments = []
        for arg in self.arguments:
            arguments.append(arg.name)
        action_line = "{}({})".format(self.name, ",".join(arguments))
        arguments.clear()

        for precon in self.preconditions:
            arguments.append(precon.__repr__())
        precon_line = ",".join(arguments)
        arguments.clear()

        for eff in self.effects:
            arguments.append(eff.__repr__())
        eff_line = ",".join(arguments)

        out_line = "{}".format(action_line)
        if precon_line != "":
            precon_line = " pre: {}".format(precon_line)
        if eff_line != "":
            eff_line = " eff: {}".format(eff_line)

        return "{} [{}{} ]".format(action_line, precon_line, eff_line)

class PlanState:
    def __init__(self, state_predicate, is_predicate_true, is_positional, argument_list):
        self.predicate = state_predicate
        self.is_true = is_predicate_true
        self.is_positional = is_positional
        self.arguments = []

        for arg in argument_list:
            self.arguments.append(Argument(arg, None))

    def check_in_world(self, current_state: 'State'):
        is_comparison = False
        if self.predicate == "BoxAtLocation":
            box_key = self.arguments[0].value
            box = current_state.boxes.get(box_key[0])[box_key[1]]
            is_comparison = box[0] == self.arguments[1].value and box[1] == self.arguments[2].value
        elif self.predicate == "AgentAtLocation":
            agent = current_state.agents.get(self.arguments[0].value)
            is_comparison = agent[0] == self.arguments[1].value and agent[1] == self.arguments[2].value

        return is_comparison if self.is_true else not is_comparison

    def __eq__(self, value):
        return self.predicate == value.predicate and self.is_true == value.is_true# and self.arguments == value.arguments

    def __repr__(self):
        arguments = []
        for arg in self.arguments:
            if arg.value is not None:
                arguments.append("{}:{}".format(arg.name, arg.value))
            else:
                arguments.append(arg.name)

        line = "{}({})".format(self.predicate, ",".join(arguments))
        if not self.is_true:
            line = "{} {}".format("NOT", line)
        return line

class PlanActionOrdering:
    def __init__(self, before: 'PlanAction', after: 'PlanAction'):
        self.before = before
        self.after = after

    def __repr__(self):
        return "before: {} after: {}".format(self.before.__repr__(), self.after.__repr__())

class PlanSubGoal:
    def __init__(self, plan_state: 'PlanState', plan_action: 'PlanAction'):
        self.state = plan_state
        self.action = plan_action

class PlanLink:
    def __init__(self, provider: 'PlanAction', receiver: 'PlanAction', condition: 'PlanState'):
        self.provider = provider
        self.receiver = receiver
        self.condition = condition

class PlanThreat:
    def __init__(self, plan_link: 'PlanLink', plan_action: 'PlanAction', plan_state: 'PlanState'):
        self.link = plan_link
        self.action = plan_action
        self.state = plan_state

class Argument:
    def __init__(self, arg_name, arg_value):
        self.name = arg_name
        self.value = arg_value

    def __eq__(self, value):
        return self.name == value.name and self.value == value.value

    def __repr__(self):
        return "{}:{}".format(self.name, self.value)




# # Human-computed order of completing goals - will come from path computing algorithm
# cheat_map = {}
# cheat_map['A'] = ['C','B']
# cheat_map['B'] = ['C']
# cheat_map['C'] = []
# cheat_map['M'] = []
# cheat_map['H'] = []

# class GoalPriority():
#     def __init__(self, initial_state: 'State', goal_state: 'State'):
#         self.ordered_goal_plan = []
#         self.goal_preconditions = {}

#         for char, values in goal_state.boxes.items():
#             self.goal_preconditions[char] = self.find_preconditions(initial_state, goal_state, char)
#             self.ordered_goal_plan.append((char, len(self.goal_preconditions.get(char))))
#         self.ordered_goal_plan = sorted(self.ordered_goal_plan, key=itemgetter(1), reverse=True)

#     def find_preconditions(self, initial_state, goal_state, goal_key):
#         # Do some pathing to the box and note all intersecting goal cells along the path
#         return cheat_map.get(goal_key)