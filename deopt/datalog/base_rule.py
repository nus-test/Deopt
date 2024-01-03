from abc import ABC, abstractmethod
from deopt.datalog.base_subgoal import BaseSubgoal
from deopt.datalog.variable import Variable
from termcolor import colored
from copy import deepcopy
import string

class BaseRule(object):
    def __init__(self, verbose, randomness, params):
        """
            This is a conjunctive query. The most basic 
            rule definition we can have.
        """
        self.verbose = verbose          # Type: bool 
        self.params = params
        self.string = ""                # Type: string
        self.decleration_string = ""    # Type: string
        self.head = None                # Type: Subgoal()
        self.subgoals = list()          # Type: Subgoal() list
        self.predicates = list()        # Type: Predicate() list
        self.aggregate = None           # Type: String
        self.randomness = randomness    # Type: Randomenss()
        self.head_arity = 0             # Type: int
        self.all_variables = list()     # Type: Variable() list        

        self.aggregate_instance = None
        self.generator = ""
        self.subsumption_string = ""
        self.functional_keywords = ""
        self.disjunctive_rule = None
        self.querypaln = None
        
        # Parameters
        self.number_of_subgoals = self.randomness.get_random_integer(1, params["max_number_of_body_subgoals"])
        self.number_of_predicates = self.randomness.get_random_integer(0, params["max_number_of_predicates"])

        # Internal things
        self.types_used = list()
        self.recursive_rule = False
        self.dependent_subgoals = list()
        self.negative_dependent_subgoals = list()

    # >>>> ENGINE SPECIFIC THINGS ---------------------------- 
    @abstractmethod
    def add_queryplan(self):
        pass

    @abstractmethod
    def generate_random_rule(self, allowed_types, available_relations):
        pass

    @abstractmethod
    def generate_disjunctive_rule(self, head, available_relations):
        pass

    @abstractmethod
    def add_functions_in_head(self):
        pass

    def add_operations_in_head(self):
        pass

    @abstractmethod
    def parse_rule(self, rule_string):
        pass

    @abstractmethod
    def generate_decleration(self):
        pass

    @abstractmethod
    def add_negated_subgoals(self, available_relations):
        pass

    @abstractmethod
    def generate_predicates(self):
        pass

    @abstractmethod 
    def insert_operations_in_head(self):
        pass

    @abstractmethod
    def generate_heads(self, non_cyclic_relations):
        pass

    @abstractmethod
    def update_string(self):
        pass

    # >>>> HELPER FUNCTIONS ---------------------------- 
    def get_types_in_body(self):
        """
            Get all the child types used in the body as a set
        """
        # for subgoal in self.subgoals:
        #     self.types_used = self.types_used + [i.get_ancestor_type() for i in subgoal.get_types()]
        # self.types_used = list(set(self.types_used))
        # self.types_used.sort()    # Because set() messes up the randomness
        for subgoal in self.subgoals:
            for var_type in subgoal.get_types():
                parent_index = -1
                for idx, t in enumerate(self.types_used):
                    if var_type.is_subtype(t):
                        parent_index = idx
                        break
                if parent_index == -1:
                    self.types_used.append(deepcopy(var_type))
                else:
                    self.types_used[parent_index] = var_type



    def validate_rule(self):
        """
            Determine number of variable spots "s" of each type.
            Generate "n" variables
            where 1 <= n <= s
        """
        temporary_index = 0
        collection_of_variable = [i for i in string.ascii_uppercase] +  [i+i for i in string.ascii_uppercase] + [i+i+i for i in string.ascii_uppercase] + [i+i+i+i for i in string.ascii_uppercase] + [i+i+i+i+i for i in string.ascii_uppercase]
        for var_type in self.types_used:
            # see how many variable spots have these types in the subgoal
            spots = 0
            for subgoal in self.subgoals:
                # spots += len([i for i in subgoal.get_types() if i.get_ancestor_type() == var_type])
                spots += len([i for i in subgoal.get_types() if var_type.is_subtype(i)])
            # Create variables of this type
            number_of_variables = 1 if spots < 3 else self.randomness.get_random_integer(2, spots-1)
            if number_of_variables + temporary_index >= len(collection_of_variable):
                new_variable_names = self.randomness.get_random_alpha_string(5).upper()
            else:
                new_variable_names = [collection_of_variable[i + temporary_index] for i in range(number_of_variables)]
            temporary_index += number_of_variables
            # Now we rename variables
            for subgoal in self.subgoals:
                for i in range(len(subgoal.get_types())):
                    # if subgoal.get_types()[i].get_ancestor_type() == var_type:
                    if var_type.is_subtype(subgoal.get_types()[i]):
                        new_var_name = deepcopy(self.randomness.random_choice(new_variable_names))
                        subgoal.update_variable_at_location(new_var_name, i)

        # Choose variables for the head
        for i in range(len(self.head.get_variables())):
            chosen_variable_name = self.randomness.random_choice(self.get_body_variables_of_type(self.head.get_variables()[i].get_type()))
            self.head.update_variable_at_location(chosen_variable_name, i)

    def lower_case_variables(self):
        self.head.lower_case_variables()
        for subgoal in self.subgoals:
            subgoal.lower_case_variables()


    def get_body_variables_of_type(self, var_type):
        """
            Return copies of variables, not the real things!
        """
        variables = list()
        for subgoal in self.subgoals:
            for var in subgoal.get_variables():
                if var.get_type().is_subtype(var_type):
                    variables.append(deepcopy(var.get_name())) # Return copies
        return variables
    
    def get_string(self):
        return self.string
    def get_subgoals(self):
        """
            Pass by value
        """
        return deepcopy(self.subgoals)
    def get_real_subgoals(self):
        """
            Pass by reference
        """
        return self.subgoals    
    def get_head(self):
        return self.head
    def get_declaration(self):
        return self.decleration_string
    def get_all_variables(self):
        return deepcopy(self.all_variables)
    def get_a_random_positive_subgoal(self):
        while True:
            # This must terminate at some point
            subgoal = self.randomness.random_choice(self.subgoals)
            if not subgoal.is_negated():
                return deepcopy(subgoal)
    
    def get_a_real_random_positive_subgoal(self):
        while True:
            # This must terminate at some point
            subgoal = self.randomness.random_choice(self.subgoals)
            if not subgoal.is_negated():
                return subgoal
    
    def get_body_string(self):
        body_string = ""
        for subgoal in self.subgoals: body_string += subgoal.get_string() + ", "
        for predicate in self.predicates: body_string += predicate.get_string() + ", "
        if self.generator != "": body_string += self.generator + ", "
        if self.aggregate is not None: body_string += self.aggregate
        if self.aggregate is None: body_string = body_string[:-2]
        
        return body_string

    def append_subgoal(self, subgoal):
        self.subgoals.append(subgoal)
        self.update_string()

    def get_variable_names_as_a_set(self):
        variable_set = list()
        for subgoal in self.subgoals:
            variable_set += [i.get_name() for i in subgoal.get_variables() if i.get_name() not in variable_set]
        return variable_set

    def add_aggregate(self, aggregate_string):
        self.aggregate = aggregate_string
        self.update_string()

    def get_decl_in_aggregate(self, decl_in_aggregate):
        self.decl_in_aggregate = decl_in_aggregate

    def set_string(self, string):
        self.string = string

    def underline_variable_in_subgoal(self):
        subgoals_more_arity = [i for i in self.subgoals if len(i.get_variables()) > 1]
        if len(subgoals_more_arity) == 0:
            return
        modified_subgoal = self.randomness.random_choice(subgoals_more_arity)
        variable_list = []
        for subgoal in self.subgoals:
            if subgoal.negated:
                continue
            variable_list += [i.get_name() for i in subgoal.get_variables()]
        modified_subgoal.underline_a_variable(variable_list)
        self.update_string()

    def add_constant_variable_in_subgoal(self, all_facts_raw_data_entries):
        subgoals_more_arity = [i for i in self.subgoals if len(i.get_variables()) > 1]
        if len(subgoals_more_arity) == 0:
            return
        modified_subgoal = self.randomness.random_choice(subgoals_more_arity)
        variable_list = []
        for subgoal in self.subgoals:
            if subgoal.negated:
                continue
            variable_list += [i.get_name() for i in subgoal.get_variables()]
        modified_subgoal.constant_a_variable(variable_list, all_facts_raw_data_entries)
        self.update_string()

    def get_dependent_subgoals(self):
        for subgoal in self.subgoals:
            if not subgoal.name in self.dependent_subgoals:
                self.dependent_subgoals.append(subgoal.name)
        if self.aggregate_instance != None:
            self.aggregate_instance.aggregate_body_rule.get_dependent_subgoals()
            for subgoal_name in self.aggregate_instance.aggregate_body_rule.dependent_subgoals:
                if not subgoal_name in self.dependent_subgoals:
                    self.dependent_subgoals.append(subgoal_name)
        if self.disjunctive_rule != None:
            self.disjunctive_rule.get_dependent_subgoals()
            for subgoal_name in self.disjunctive_rule.dependent_subgoals:
                if not subgoal_name in self.dependent_subgoals:
                    self.dependent_subgoals.append(subgoal_name)

        for subgoal in self.subgoals:
            if subgoal.negated and not subgoal.name in self.negative_dependent_subgoals:
                self.negative_dependent_subgoals.append(subgoal.name)
        if self.aggregate_instance != None:
            for subgoal_name in self.aggregate_instance.aggregate_body_rule.negative_dependent_subgoals:
                if not subgoal_name in self.negative_dependent_subgoals:
                    self.negative_dependent_subgoals.append(subgoal_name)
        if self.disjunctive_rule != None:
            for subgoal_name in self.disjunctive_rule.negative_dependent_subgoals:
                if not subgoal_name in self.negative_dependent_subgoals:
                    self.negative_dependent_subgoals.append(subgoal_name)