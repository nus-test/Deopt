from deopt.datalog.base_rule import BaseRule
from deopt.engines.cozodb.cozodb_subgoal import CozoDBSubgoal
from deopt.engines.cozodb.cozodb_predicate import CozoDBPredicate
import string 
from copy import deepcopy
from termcolor import colored
import time
import random


class CozoDBDisjunctiveRule(BaseRule):

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

        # add generative functors into rule
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_generator"]:
            self.add_generator()

        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_disjunctive_rule"]:
            self.generate_disjunctive_rule(self, available_relations, all_facts_raw_data_entries)

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

    def generate_body(self, available_relations):
        """
            It takes the head as input and the list of all avaiable relations
            Will just generate 1 disjunctive rule
        """
        # For each variable type in the head, find a relation that conatins such a variable type and then insert it in the body
        for var in self.head.get_variables():
            # Search for a relations that contains a variable of this type
            while True:
                # This will ALWAYS break at some point
                rel = deepcopy(self.randomness.random_choice(available_relations))
                is_type_match = False
                for t in rel.get_types():
                    if t.is_subtype(var.get_type()):
                        is_type_match = True
                if is_type_match:
                    self.subgoals.append(rel)
                    break
        # Add the remaining number of subgoals
        for i in range(self.number_of_subgoals - len(self.subgoals)):
            self.subgoals.append(deepcopy(self.randomness.random_choice(available_relations)))
        self.get_types_in_body()
        self.validate_rule()
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

    def validate_rule(self):
        """
            Determine number of variable spots "s" of each type.
            Generate "n" variables
            where 1 <= n <= s
        """
        collection_of_variable = [i for i in string.ascii_uppercase] +  [i+i for i in string.ascii_uppercase] + [i+i+i for i in string.ascii_uppercase] + [i+i+i+i for i in string.ascii_uppercase] + [i+i+i+i+i for i in string.ascii_uppercase]
        variables_in_head = [i.get_name() for i in self.head.variables]
        type_varname_map = {}
        for idx, v in enumerate(self.head.variables):
            t = self.head.variables_types[idx]
            if t.get_name() in type_varname_map:
                type_varname_map[t.get_name()].append(v.get_name())
            else:
                type_varname_map[t.get_name()] = list()
                type_varname_map[t.get_name()].append(v.get_name())

        for subgoal in self.subgoals:
            for idx, t in enumerate(subgoal.get_types()):
                if t.get_name() in type_varname_map:
                    new_var_name = self.randomness.random_choice(type_varname_map[t.get_name()])
                    if len(type_varname_map[t.get_name()]) != 1:
                        type_varname_map[t.get_name()].remove(new_var_name)
                    subgoal.update_variable_at_location(new_var_name, idx)
                else:
                    new_var_name = self.randomness.random_choice(collection_of_variable)
                    while new_var_name in variables_in_head:
                        new_var_name = self.randomness.random_choice(collection_of_variable)
                    subgoal.update_variable_at_location(new_var_name, idx)

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
        

    def update_string(self):
        # Subgoal
        self.string = "("
        for subgoal in self.subgoals:
            self.string += subgoal.get_string() + ", "
        
        # Predicates
        for predicate in self.predicates:
            self.string += predicate.get_string() + ", "
        
        # Generator
        if self.generator != "":
            self.string += self.generator + ", "

        self.string = self.string[:-2] + ")"

        # Disjunction rule
        if self.disjunctive_rule != None:
            self.string += " or "
            self.string += self.disjunctive_rule.string