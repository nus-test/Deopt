from deopt.datalog.base_rule import BaseRule
from deopt.engines.cozodb.cozodb_disjunctive_rule import CozoDBDisjunctiveRule
from deopt.engines.cozodb.cozodb_subgoal import CozoDBSubgoal
from deopt.engines.cozodb.cozodb_predicate import CozoDBPredicate
import string 
from copy import deepcopy
from termcolor import colored
import time
import random


class CozoDBRule(BaseRule):
    def generate_random_rule(self, allowed_types, available_relations):
        """
            First we select the subgoals for the body from available_relations. 
            A head is then generated depending on the types
            that are in the body.

            Step 1: Choose subgoals for the body
            Step 2: Get all the types in the body
            Step 3: Create a head
            Step 4: Create joins by variable renamings and make this a valid clause
        """
        
        
        if self.randomness.get_random_integer(0, 99) < self.params["probability_of_recursive_rule"] and len(available_relations) > self.params["max_number_of_facts"]:
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
            # Step 1: Generate body by choosing relations in the base program
            for i in range(self.number_of_subgoals):
                self.subgoals.append(deepcopy(self.randomness.random_choice(available_relations)))
            # Step 2: Get the used types in the body
            self.get_types_in_body()
            # Step 3: Create basic head subgoal
            self.head_arity = self.randomness.get_random_integer(1, self.params["max_head_arity"])
            self.head = CozoDBSubgoal(randomness=self.randomness, arity=self.head_arity, params=self.params)
            self.head.generate_random_subgoal(type_used=self.types_used, all_allowed_types=allowed_types)
            while self.is_duplicate_head(self.head.get_name(), available_relations):
                self.head.generate_random_subgoal(type_used=self.types_used, all_allowed_types=allowed_types)
            self.functional_keywords = self.head.generate_functional_keywords()
        
        # Step 4: Make this a valid clause + create joins
        self.validate_rule()        
        # Done! Update string
        self.update_string()
        self.generate_decleration()


    def is_duplicate_head(self, head_name, available_relations):
        for relation in available_relations:
            if relation.get_name() == head_name:
                return True
        return False


    def add_more_element_to_rule(self, available_relations, all_facts_raw_data_entries):
        # add negated subgoal in rule
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_negated"]:
            self.add_negated_subgoal(available_relations=available_relations)
        
        # underline a variable in a subgoal in rule
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_underline"]:
            self.underline_variable_in_subgoal()

        # add a constant for a variable in a subgoal
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_constant"]:
            self.add_constant_variable_in_subgoal(all_facts_raw_data_entries)
        
        # add predicts into rule
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_predicate"]:
            self.generate_predicates()

        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_disjunctive_rule"]:
            self.generate_disjunctive_rule(self, available_relations, all_facts_raw_data_entries)

        # # add binary operations in head
        # if self.randomness.get_random_integer(0, 9) < self.params["probability_of_head_operations"]:
        #     self.insert_operations_in_head()

        # # add binary operations in subgoals
        # if self.randomness.get_random_integer(0, 9) < self.params["probability_of_rule_body_operations"]:
        #     self.insert_operations_in_rule_body()

        # add generative functors into rule
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_generator"]:
            self.add_generator()

        self.get_dependent_subgoals()
        self.update_string()

    def add_negated_subgoal(self, available_relations): 
        success = True
        subgoal = deepcopy(self.randomness.random_choice(available_relations))
        if subgoal.name == self.head.name:
            return
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

    def generate_disjunctive_rule(self, parent_rule, available_relations, all_facts_raw_data_entries):
        """
            It takes the head as input and the list of all avaiable relations
            Will just generate 1 disjunctive rule
        """
        self.disjunctive_rule = CozoDBDisjunctiveRule(verbose=self.verbose, randomness=self.randomness, params=self.params)
        self.disjunctive_rule.head = deepcopy(parent_rule.get_head())

        self.disjunctive_rule.generate_body(available_relations)
        self.disjunctive_rule.add_more_element_to_rule(available_relations=available_relations, all_facts_raw_data_entries=all_facts_raw_data_entries)
        self.update_string()

    def generate_decleration(self):
        self.decleration_string = self.head.generate_decleration

    def generate_decleration_for_single_query(self):
        decl_list = list()

        for subgoal in self.get_subgoals():
            if subgoal.generate_decleration() not in decl_list:
                decl_list.append(subgoal.generate_decleration())

        if self.aggregate_instance != None:
            decl_list += [i for i in self.aggregate_instance.aggregate_body_rule.generate_decleration_for_single_query() if not i in decl_list]

        if self.disjunctive_rule != None:
            decl_list += [i for i in self.disjunctive_rule.generate_decleration_for_single_query() if not i in decl_list]

        if self.head.generate_decleration not in decl_list:
            decl_list.append(self.head.generate_decleration)
        return decl_list

    def generate_in_file_fact_for_single_query(self, all_raw_data_entries):
        fact_list = list()
        for subgoal in self.get_subgoals():
            fact_list += subgoal.get_fact_data(all_raw_data_entries)
        if self.aggregate_instance != None:
            fact_list += self.aggregate_instance.aggregate_body_rule.generate_in_file_fact_for_single_query(all_raw_data_entries)
        if self.disjunctive_rule != None:
            fact_list += self.disjunctive_rule.generate_in_file_fact_for_single_query(all_raw_data_entries)
        return list(set(fact_list))


    def generate_predicates(self):
        for i in range(self.number_of_predicates):
            predicate = CozoDBPredicate([i for i in self.all_variables if i.get_name() != '_'and not i.constant], self.randomness)
            if predicate.get_string() != "": self.predicates.append(predicate)
            self.update_string()

    def generate_heads(self, non_cyclic_relations):
        """ 
            Add multiple heads in the rule.
            Only updates the string of the rule. Nothing else is changed. Updating the rule will reset it to its original string.
        """
        # TODO: update this later
        valid_relations = list()
        for relation in non_cyclic_relations:
            flag = True
            for _type in relation.get_types():
                if _type not in self.types_used: 
                    flag = False
                    continue
            if flag: valid_relations.append(relation)
        
        # Do nothing if valid_relations is empty
        if len(valid_relations) == 0: return 1
        number_of_heads = self.randomness.get_random_integer(0, self.params["max_heads_in_mixed_rule"])
        new_head_string = ""
        # Now pick a realtion and rename the variables
        for i in range(number_of_heads):
            picked_relation = deepcopy(self.randomness.random_choice(valid_relations))
            for j, var in enumerate(picked_relation.get_variables()):
                picked_var = self.randomness.random_choice(self.get_body_variables_of_type(var.get_type()))
                picked_relation.update_variable_at_location(picked_var, j)
            new_head_string += ", " + picked_relation.get_string()
        self.string = self.head.get_string() + new_head_string + " " + self.string[self.string.find(":-"):]

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

    def add_generator(self):
        selected_var = None
        var_list = None
        
        if self.randomness.flip_a_coin():
            # add generator for number
            number_var_list = [i for i in self.get_all_variables() if i.get_type().get_ancestor_type().get_name() == "Number" and i.get_name() != '_' and not i.constant]
            if len(number_var_list) == 0:
                return
            selected_var = self.randomness.random_choice(number_var_list)
            var_list = self.randomness.get_random_integer_list(-999, 999, self.randomness.get_random_integer(5, 10))
            var_list = [str(x) for x in var_list]
        else:
            # add generator for string
            float_var_list = [i for i in self.get_all_variables() if i.get_type().get_ancestor_type().get_name() == "float" and i.get_name() != '_']
            if len(float_var_list) == 0:
                return
            selected_var = self.randomness.random_choice(float_var_list)
            var_list = self.randomness.get_random_string_list(self.randomness.get_random_integer(5, 10))
            var_list = ['"' + x + '"' for x in var_list]
        self.generator = ""
        self.generator += selected_var.get_name() + " in [" + ', '.join(var_list) + "]"
        self.update_string()

    def add_queryplan(self):
        pass
        

    def update_string(self):
        # update the list of variables in the body as well
        self.all_variables = list()
        for subgoal in self.subgoals:
            self.all_variables = self.all_variables + subgoal.get_variables()

        # update string
        self.string = self.head.get_string()
        self.string += " := "
        if self.disjunctive_rule != None:
            self.string += "("
        # body
        
        # Subgoal
        for subgoal in self.subgoals:
            self.string += subgoal.get_string() + ", "
        
        # Predicates
        for predicate in self.predicates:
            self.string += predicate.get_string() + ", "
        
        # Generator
        if self.generator != "":
            self.string += self.generator + ", "

        # Aggregate
        if self.aggregate is not None: self.string += self.aggregate
        if self.aggregate is None: self.string = self.string[:-2]

        # Disjunction rule
        if self.disjunctive_rule != None:
            self.string += ") or "
            self.string += self.disjunctive_rule.string