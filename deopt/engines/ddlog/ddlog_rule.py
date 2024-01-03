from deopt.datalog.base_rule import BaseRule
from deopt.engines.ddlog.ddlog_subgoal import DDlogSubgoal
from deopt.engines.ddlog.ddlog_predicate import DDlogPredicate
from copy import deepcopy
import string

class DDlogRule(BaseRule):

    def generate_random_rule(self, allowed_types, available_relations, edb_relations):
        if self.randomness.get_random_integer(0, 99) < self.params["probability_of_recursive_rule"] and len(available_relations) > self.params["max_number_of_facts"]:
            self.head = deepcopy(self.randomness.random_choice(available_relations))
            while self.head.name in edb_relations:
                self.head = deepcopy(self.randomness.random_choice(available_relations))
            # print("generate recusive rule for " + self.head.name)
            self.head_arity = self.head.arity
            for var in self.head.get_variables():
                # Search for a relations that contains a variable of this type
                while True:
                    # This will ALWAYS break at some point
                    rel = deepcopy(self.randomness.random_choice(available_relations))
                    is_type_match = False
                    for t in rel.get_types():
                        if t.is_subtype(var.get_type()):
                            is_type_match = True
                            break
                    if is_type_match:
                        self.subgoals.append(rel)
                        break
            # Add the remaining number of subgoals
            for i in range(self.number_of_subgoals - len(self.subgoals)):
                self.subgoals.append(deepcopy(self.randomness.random_choice(available_relations)))
            self.get_types_in_body()
            self.recursive_rule = True
        else:
            for i in range(self.number_of_subgoals):
                self.subgoals.append(deepcopy(self.randomness.random_choice(available_relations)))
            self.get_types_in_body()
            # self.head_arity = 1
            self.head_arity = self.randomness.get_random_integer(1, self.params["max_head_arity"])
            self.head = DDlogSubgoal(randomness=self.randomness, arity=self.head_arity, params=self.params)
            self.head.generate_random_subgoal(type_used=self.types_used, all_allowed_types=allowed_types)

        # for subgoal in self.subgoals:
        #     if not subgoal.name in self.dependent_subgoals:
        #         self.dependent_subgoals.append(subgoal.name)

        self.validate_rule() 
        self.head.upper_case_name()
        self.lower_case_variables()
        self.remove_same_variable_in_one_subgoal()
        self.update_string()
        self.generate_decleration()

    def add_more_element_to_rule(self, available_relations, all_facts_raw_data_entries):
        # add negated subgoal in rule
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_negated"]:
            self.add_negated_subgoal(available_relations=available_relations)
            self.update_string()

        # underline a variable in a subgoal in rule
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_underline"]:
            self.underline_variable_in_subgoal()

        # add a constant for a variable in a subgoal
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_constant"]:
            self.add_constant_variable_in_subgoal(all_facts_raw_data_entries)

        # add predicts into rule
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_predicate"]:
            self.generate_predicates()

        # add binary operations in head
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_head_operations"]:
            self.insert_operations_in_head()

        # add binary operations in subgoals
        # if self.randomness.get_random_integer(0, 9) < self.params["probability_of_rule_body_operations"]:
        #     self.insert_operations_in_rule_body()

        self.get_dependent_subgoals()
        self.update_string()

    def add_negated_subgoal(self, available_relations): 
        success = True
        subgoal = deepcopy(self.randomness.random_choice(available_relations))
        # Now for each variable type in this new subgoal, we have to get a variable that is already in the rule
        # and put it here. If we cannot find such a variable then we are in trouble and we cannot safely negate it 
        for i, var in enumerate(subgoal.get_variables()):
            # pick a random variable from the following list of copied variables
            variables_of_this_type = self.get_body_variables_of_type(var.get_type().get_ancestor_type())
            if len(variables_of_this_type) == 0:
                success = False
                break
            new_var = self.randomness.random_choice(variables_of_this_type)
            subgoal.update_variable_at_location(new_var, i)
        if not success: return
        # Negate this subgoal
        subgoal.negate_subgoal()
        # Add this subgoal in the list of subgoals
        self.subgoals.append(subgoal)
        self.update_string()

    def generate_predicates(self):
        for i in range(self.number_of_predicates):
            predicate = DDlogPredicate([i for i in self.all_variables if i.get_name() != '_' and not i.constant], self.randomness)
            if predicate.get_string() != "": self.predicates.append(predicate.get_string())
            self.update_string()

    def insert_operations_in_head(self):
        """
            Insert operations in head
        """
        self.head.insert_operations(self.get_all_variables())
        self.update_string()

    def insert_operations_in_rule_body(self):
        modified_subgoal = self.randomness.random_choice(self.subgoals)
        modified_subgoal.insert_operations_in_rule_body(self.get_all_variables())
        self.update_string()
        
    def remove_same_variable_in_one_subgoal(self):
        for subgoal in self.subgoals:
            name_set = []
            for var in subgoal.variables:
                var_name = var.get_name()
                if var_name in name_set:
                    idx = 1
                    new_var_name = var_name + str(idx)
                    while new_var_name in name_set:
                        idx += 1
                        new_var_name = var_name + str(idx)
                    var.set_name(new_var_name)
                    subgoal.update_string()
                    name_set.append(new_var_name)
                    self.predicates.append(var_name + " == " + new_var_name)
                else:
                    name_set.append(var_name)
                    

    def generate_decleration(self):
        self.decleration_string = "relation " + self.head.get_name() + "("
        for i in range(self.head_arity):
            self.decleration_string += string.ascii_lowercase[i] + ":" + self.head.get_types()[i].get_name() + ", "
        self.decleration_string = self.decleration_string[:-2] + ")"

    def generate_decleration_for_single_query(self):
        decl_list = list()
        for subgoal in self.get_subgoals():
            if subgoal.generate_decleration() not in decl_list:
                decl_list.append(subgoal.generate_decleration())

        if self.aggregate_instance != None:
            decl_list += [i for i in self.aggregate_instance.aggregate_body_rule.generate_decleration_for_single_query() if not i in decl_list]

        if self.disjunctive_rule != None:
            decl_list += [i for i in self.disjunctive_rule.generate_decleration_for_single_query() if not i in decl_list]
        return decl_list
    
    def update_string(self):
        # update the list of variables in the body as well
        self.all_variables = list()
        for subgoal in self.subgoals:
            self.all_variables = self.all_variables + subgoal.get_variables()
        # update string
        self.string = self.head.get_string()
        self.string += " :- "
        # body
        
        # Subgoal
        for subgoal in self.subgoals:
            self.string += subgoal.get_string() + ", "
        
        # Predicates
        for predicate in self.predicates:
            self.string += predicate + ", "
        
        # Aggregate
        if self.aggregate is not None: self.string += self.aggregate
        if self.aggregate is None: self.string = self.string[:-2]

        self.string += "."