import copy
from state import State
from operator import itemgetter

class Plan:
    def __init__(self, initial_state: 'State', goal_state: 'State'):
        self.orderings = []
        self.actions = []
        self.subgoals = []
        self.links = []

        self.create_action_blueprints()

    def create_plan_state_blueprints(self):
        state_blueprints = []
        state_blueprints.append(PlanState("Detached", True, ["agent"]))
        state_blueprints.append(PlanState("Detached", False, ["agent"]))
        state_blueprints.append(PlanState("nextTo", True, ["agent", "box"]))
        state_blueprints.append(PlanState("nextTo", False, ["agent", "box"]))
        state_blueprints.append(PlanState("AttachedTo", True, ["agent", "box"]))
        state_blueprints.append(PlanState("AttachedTo", False, ["agent", "box"]))
        state_blueprints.append(PlanState("BoxInGoal", True, ["box", "goal"]))
        state_blueprints.append(PlanState("BoxInGoal", False, ["box", "goal"]))
        state_blueprints.append(PlanState("AtLocation", True, ["entity", "x", "y"]))
        state_blueprints.append(PlanState("AtLocation", False, ["entity", "x", "y"]))

        return state_blueprints

    def create_action_blueprints(self):
        # States
        plan_states = self.create_plan_state_blueprints()

        # Attach / Detach
        new_action = PlanAction("AttachTo")
        new_action.define_blueprint(["agent", "box"], [plan_states[0], plan_states[2]], [plan_states[2], plan_states[1], plan_states[4]])
        self.actions.append(new_action)

        new_action = PlanAction("DetachFrom")
        new_action.define_blueprint(["agent", "box"], [plan_states[4]], [plan_states[0], plan_states[5]])
        self.actions.append(new_action)

        # Agent movement actions
        new_action = PlanAction("MoveAgentNextTo")
        new_action.define_blueprint(["agent", "box"], [plan_states[0], plan_states[3]], [plan_states[2], plan_states[0]])
        self.actions.append(new_action)

        new_action = PlanAction("MoveAgentTo")
        new_action.define_blueprint(["agent", "x", "y"], [plan_states[0], plan_states[9]], [plan_states[0], plan_states[8]])
        self.actions.append(new_action)

        # Box movement
        new_action = PlanAction("MoveBoxTo")
        new_action.define_blueprint(["agent", "box", "x", "y"], [plan_states[4], plan_states[9]], [plan_states[4], plan_states[8]])
        self.actions.append(new_action)

class PlanAction:
    def __init__(self, action_name):
        self.name = action_name
        self.arguments = []
        self.preconditions = []
        self.effects = []
        self.is_blueprint = True

    def define_blueprint(self, argument_names, preconditions, effects):
        if self.is_blueprint:
            for arg in argument_names:
                self.arguments.append(Argument(arg, None))

            for precon in preconditions:
                self.preconditions.append(precon)

            for eff in effects:
                self.effects.append(eff)

    def instantiate_from_blueprint(self, argument_list):
        if self.is_blueprint:
            action = PlanAction(self.name)
            action.arguments = copy.deepcopy(self.arguments)
            action.preconditions = copy.deepcopy(self.preconditions)
            action.effects = copy.deepcopy(self.effects)
            action.is_blueprint = False

            # Bind argument list to arguments in template
            for i in enumerate(len(argument_list)):
                action.arguments[i].value = argument_list[i]

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

        return "{} [ pre: {}  eff: {} ]".format(action_line, precon_line, eff_line)

class PlanState:
    def __init__(self, state_predicate, is_predicate_true, argument_list):
        self.predicate = state_predicate
        self.is_true = is_predicate_true
        self.arguments = []

        for arg in argument_list:
            self.arguments.append(Argument(arg, None))

    def __eq__(self, value):
        return self.predicate == value.predicate and self.is_true == value.is_true

    def __repr__(self):
        arguments = []
        for arg in self.arguments:
            arguments.append(arg.name)

        line = "{}({})".format(self.predicate, ",".join(arguments))
        if not self.is_true:
            line = "{} {}".format("NOT", line)
        return line

class ActionOrdering:
    def __init__(self, before: 'PlanAction', after: 'PlanAction'):
        self.before = before
        self.after = after

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































# # Human-computed order of completing goals - will come from path computing algorithm
# cheat_map = {}
# cheat_map['A'] = ['C','B']
# cheat_map['B'] = ['C']
# cheat_map['C'] = []
# cheat_map['M'] = []
# cheat_map['H'] = []

# class Plan():
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