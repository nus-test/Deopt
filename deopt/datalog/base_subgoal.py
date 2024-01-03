from abc import ABC, abstractmethod
from deopt.datalog.variable import Variable
from copy import deepcopy
import string

class BaseSubgoal(object):
    def __init__(self, randomness, arity, params):
        self.string = ""
        self.name = ""
        self.arity = arity  
        self.variables = list()             # Type: Variable() list
        self.variables_types = list()       # Type: String list
        self.randomness = randomness
        self.negated = False
        self.params = params

        self.functional_keywords = ""

    def generate_random_subgoal(self, type_used, all_allowed_types):
        """
            allowed_type: list of types that can be included in the attributes
        """
        # Generate subgoal name (Alpha-numeric of length 4)
        allowed_types = list()
        for a_t in all_allowed_types:
            for t_u in type_used:
                if t_u.is_subtype(a_t):
                    allowed_types.append(a_t)
                    break
        self.name = self.randomness.get_lower_case_alpha_string(4)
        while self.name == "fold":
            self.name = self.randomness.get_lower_case_alpha_string(4)   # fold is a keyword in Souffle
        # Pick types
        self.variables_types = [self.randomness.random_choice(allowed_types) for i in range(self.arity)]
        # generate variables
        self.variables.clear()
        for i in range(self.arity):
            self.variables.append(Variable(name=self.randomness.get_upper_case_alpha_string(4), vtype=self.variables_types[i]))       
        self.update_string()

    def generate_subgoal(self, name, variables, variables_types):
        self.name = name
        self.variables = variables
        self.variables_types = variables_types
        self.update_string()

    @abstractmethod
    def generate_decleration(self):
        pass

    def set_functional_keywords(self, keywords):
        self.functional_keywords = keywords

    @abstractmethod
    def generate_functional_keywords(self):
        pass
        

    # >>> ENGINE SPECIFIC THINGS ---------------------------- 
    @abstractmethod
    def negate_subgoal(self):
        pass

    @abstractmethod
    def parse_subgoal_declaration(self, subgoal_decleration_string):
        pass

    @abstractmethod
    def insert_operations(self, all_rule_variables):
        pass
    
    def upper_case_name(self):
        self.name = self.name.upper()
        self.update_string()
    

    def lower_case_variables(self):
        for var in self.variables:
            var.set_name(var.get_name().lower())
        self.update_string()

    def update_string(self):
        self.string = self.name + "("
        for variable in self.variables:
            self.string += str(variable.get_name()) + ", "
        self.string = self.string[:-2] + ")"
        if self.negated: self.negate_subgoal()

    def get_name(self):
        return self.name
    def get_string(self):
        return self.string
    def get_variables(self):
        return self.variables
    def get_types(self):
        return self.variables_types
    def get_arity(self):
        return self.arity
    def update_variable_at_location(self, new_var_name, location):
        """
            new_var     :   Type Variable()
        """
        self.variables[location].set_name(new_var_name)
        self.update_string()
    def is_negated(self):
        # Return true if it is a negated subgoal
        return self.negated

    def update_subgoal_name(self, new_name):
        self.name = new_name

    def underline_a_variable(self, variable_list):
        """
            We must modify the neame of variable,
            because we need to give this information to reference interpreter
        """
        var = self.randomness.random_choice(self.variables)
        if variable_list.count(var.get_name()) == 1:
            return
        var.set_name("_")
        var.underline = True
        self.update_string()

    def constant_a_variable(self, variable_list, all_facts_raw_data_entries):
        """
            We must modify the neame of variable,
            because we need to give this information to reference interpreter
        """
        string_type_list = ["symbol", "string", "String"]
        var_index = self.randomness.get_random_integer(0, len(self.variables) - 1)
        var = self.variables[var_index]
        if variable_list.count(var.get_name()) == 1:
            return
        if not self.get_name() in all_facts_raw_data_entries.keys() or len(all_facts_raw_data_entries[self.get_name()]) == 0:
            return
        selected_data_entry = self.randomness.random_choice(all_facts_raw_data_entries[self.get_name()]).strip().split("\t")
        if var_index >= len(selected_data_entry):
            return
        selected_data = selected_data_entry[var_index]
        if var.get_type().get_ancestor_type_name() in string_type_list and not '"' in selected_data:
            selected_data = '"' + selected_data + '"'
        var.set_name(selected_data)
        var.constant = True
        self.update_string()

