from termcolor import colored
from deopt.engines.cozodb.cozodb_subgoal import CozoDBSubgoal
from deopt.engines.cozodb.cozodb_rule import CozoDBRule
from copy import deepcopy
from deopt.datalog.variable import Variable

class CozoDBAggregate(object):
    def __init__(self, parent_rule, verbose, randomness, params, allowed_types, available_relations, all_facts_raw_data_entries):
        # This should get the original rule and should be able to generate a new rule
        self.parent_rule = parent_rule
        self.verbose = verbose
        self.randomness = randomness
        self.params = params
        self.allowed_types = allowed_types
        self.available_relations = available_relations
        self.string = ""
        self.chosen_aggregate = None
        self.aggregate_body = None
        self.external_variable = None
        self.internal_variable = None
        self.aggregate_equality = self.randomness.random_choice(["=", "!=", "<", ">", ">=", "<="])
        self.aggregate_body_rule = None
        self.generate_aggregate(all_facts_raw_data_entries)


    def generate_aggregate(self, all_facts_raw_data_entries):
        """
            B(y) :- y = max z : A("A", z).
            B(z) :- z = min x+y : { A(x), A(y), C(y) }.
            B(s, c) :- W(s), c = count : { C(s, _) }.
            B(n, m) :- A(n, m), B(m, s), 2 * s = 2 * sum s : { A(n, s) } + 2.
            C(n) :- D(n), B(n, max p : { A(n, p) }).
            B(s, count : { C(s, _) }) :- W(s).
            mean: https://github.com/cozodb-lang/cozodb/blob/68062082dc95cd4086e8ba31fe1f09fa95361456/tests/evaluation/aggregates7/aggregates7.dl
        """

        aggregate_body_rule = CozoDBRule(verbose=self.verbose, randomness=self.randomness, params=self.params)
        aggregate_body_rule.generate_random_rule(allowed_types=self.allowed_types, available_relations=self.available_relations)
        # Rename the variables in the aggregate internals. They cannot be the same as in parent rule. This can cause serious type errors.
        for subgoal in aggregate_body_rule.get_real_subgoals():
            for i,var in enumerate(subgoal.get_variables()):
                subgoal.update_variable_at_location(var.get_name() + var.get_name() + var.get_name(), i)
        aggregate_body_rule.update_string()
        aggregate_body_rule.add_more_element_to_rule(self.available_relations, all_facts_raw_data_entries)
        self.aggregate_body = aggregate_body_rule.get_body_string()
        self.aggregate_body_rule = aggregate_body_rule

        # Pick a variable of type "number" in the parent rule.
        number_variables = [i for i in self.parent_rule.get_all_variables() if i.get_type() == "number" and i.get_name() != '_']
        if len(number_variables) == 0: return 1
        self.external_variable = self.randomness.random_choice(number_variables)
        self.internal_variable = self.randomness.random_choice(aggregate_body_rule.get_all_variables())  
        if self.internal_variable.get_type() == "number": self.chosen_aggregate = self.randomness.random_choice(["min", "max", "sum", "count", "mean"])
        if self.internal_variable.get_type() == "symbol": self.chosen_aggregate = "count"

    def get_string(self):
        if self.external_variable is None or self.internal_variable is None or self.chosen_aggregate is None or self.aggregate_body is None:
            return "0 = 0"
        # No need to include the internal variable in case of count aggregate
        if self.chosen_aggregate == "count":
            self.string = self.external_variable.get_name() + " " + self.aggregate_equality + " " + self.chosen_aggregate + " : {" + self.aggregate_body + "}"
        else:
            self.string = self.external_variable.get_name() + " " + self.aggregate_equality + " " + self.chosen_aggregate + " " + self.internal_variable.get_name() + " : { " + self.aggregate_body + "}"
        return self.string

    def generate_decl_for_body_rule(self):
        result = []
        for subgoal in self.aggregate_body_rule.subgoals:
            result.append(subgoal.generate_decleration())
        return result

    def generate_input_decl_for_body_rule(self):
        result = []
        for subgoal in self.aggregate_body_rule.subgoals:
            result.append(".input " + subgoal.get_name())
        return result

