from deopt.datalog.base_subgoal import BaseSubgoal
from deopt.datalog.variable import Variable
from termcolor import colored
import os
from deopt.utils.file_operations import create_file
import string
from copy import deepcopy

class SouffleSubgoal(BaseSubgoal):

    def parse_subgoal_declaration(self, subgoal_decleration_string):
        temp_string = deepcopy(subgoal_decleration_string)
        temp_string = temp_string.replace(".decl ", "")
        self.name = temp_string[0:temp_string.find("(")]
        variables_with_types = temp_string[temp_string.find("(") + 1 : temp_string.find(")")].replace(" ", "").split(",")
        if variables_with_types[0] == "":
            # No variables were declared in this subgoal
            self.arity = 0
        else:
            # Found atleast one variable declaration
            self.arity = len(variables_with_types)
            for variable in variables_with_types:
                var_name = variable[:variable.find(":")]
                var_type = variable[variable.find(":") + 1:]
                self.variables.append(Variable(var_name, var_type))
                self.variables_types.append(var_type)        
            self.update_string()


    def negate_subgoal(self):
        self.negated = True
        self.string = "!" + self.string

    def insert_operations(self, all_rule_variables):
        operations_dictionary = {
                                    "number" : {
                                                    "binary"    :   ["+", "-", "*", "/", "^", "%", " land ", " lor ", " lxor ", " band ", " bor ", " bxor ", " bshl ", " bshr ", " bshru "],
                                                    "unary"     :   ["-", "--", "bnot ", "lnot "],
                                                    "func"      :   ["min", "max"]
                                    },
                                    "unsigned" : {
                                                    "binary"    :   ["+", "-", "*"],
                                                    "unary"     :   [""],
                                                    "func"      :   ["min", "max"]
                                    },
                                    "float" : {
                                                    # "binary"    :   ["+", "-", "*", "/", "^"],
                                                    "binary"    :   ["+", "-", "*", "/"],
                                                    "unary"     :   ["-", "--"],
                                                    "func"      :   ["min", "max"]
                                    },
                                    "symbol" : {    
                                                    "binary"    :   [""],
                                                    "unary"     :   [""],
                                                    "func"      :   ["cat"]
                                    }
        }         
        max_expression_adding_operations = self.randomness.get_random_integer(0, self.params["max_expression_adding_operations"])
        for i in range(max_expression_adding_operations):
            variable = self.randomness.random_choice(self.variables)
            variable_type = variable.get_type().get_ancestor_type().get_name()
            if variable_type not in self.params["souffle_types"]: continue
            new_variable_string = ""
            operation_type = self.randomness.random_choice(["binary", "binary", "unary", "unary", "func"])
            if variable_type == "symbol": operation_type = "func"
            operation = self.randomness.random_choice(operations_dictionary[variable_type][operation_type])
            random_constant = ""
            random_variable_list = [i.get_name() for i in all_rule_variables if i.get_type().get_ancestor_type().get_name() == variable_type and i.get_name() != '_']
            if len(random_variable_list) == 0: continue
            random_variable = self.randomness.random_choice(random_variable_list)
            if variable_type == "symbol": random_constant = '"' + self.randomness.get_random_alpha_string(1) + '"'
            if variable_type == "number": random_constant = str(self.randomness.get_random_integer(-10,10))   
            if variable_type == "unsigned": random_constant = str(self.randomness.get_random_integer(0,20))   
            if variable_type == "float" : random_constant = str(self.randomness.get_random_float(-10, 10))   
            if operation_type == "func": new_variable_string = operation + '(' + variable.get_name() + ',' + self.randomness.random_choice([random_constant, random_variable]) + ')'
            if operation_type == "binary": new_variable_string = variable.get_name() + operation + self.randomness.random_choice([random_constant, random_variable])
            if operation_type == "unary": new_variable_string = operation + variable.get_name()
            variable.set_name(new_variable_string)
        self.update_string()

    def insert_operations_in_rule_body(self, all_rule_variables):
        operations_dictionary = {
                                    "number" : {
                                                    "binary"    :   ["+", "-", "*", "/", "^", "%", " land ", " lor ", " lxor ", " band ", " bor ", " bxor ", " bshl ", " bshr ", " bshru "],
                                                    "unary"     :   ["-", "--", "bnot ", "lnot "],
                                                    "func"      :   ["min", "max"]
                                    },
                                    "unsigned" : {
                                                    "binary"    :   ["+", "-", "*"],
                                                    "unary"     :   [""],
                                                    "func"      :   ["min", "max"]
                                    },
                                    "float" : {
                                                    # "binary"    :   ["+", "-", "*", "/", "^"],
                                                    "binary"    :   ["+", "-", "*", "/"],
                                                    "unary"     :   ["-", "--"],
                                                    "func"      :   ["min", "max"]
                                    },
                                    "symbol" : {    
                                                    "binary"    :   [""],
                                                    "unary"     :   [""],
                                                    "func"      :   ["cat"]
                                    }
        }         
        max_expression_adding_operations = self.randomness.get_random_integer(0, self.params["max_expression_adding_operations"])
        all_rule_variable_names = [n.get_name() for n in all_rule_variables]
        for i in range(max_expression_adding_operations):
            variable = self.randomness.random_choice(self.variables)
            if all_rule_variable_names.count(variable.get_name()) == 1:
                continue
            variable_type = variable.get_type().get_ancestor_type().get_name()
            if variable_type not in self.params["souffle_types"]: continue
            new_variable_string = ""
            operation_type = self.randomness.random_choice(["binary", "binary", "unary", "unary", "func"])
            if variable_type == "symbol": operation_type = "func"
            operation = self.randomness.random_choice(operations_dictionary[variable_type][operation_type])
            random_constant = ""
            random_variable = self.randomness.random_choice([i.get_name() for i in all_rule_variables if i.get_type().get_ancestor_type().get_name() == variable_type and i.get_name() != '_'])
            if variable_type == "symbol": random_constant = '"' + self.randomness.get_random_alpha_string(1) + '"'
            if variable_type == "number": random_constant = str(self.randomness.get_random_integer(-10,10))   
            if variable_type == "unsigned": random_constant = str(self.randomness.get_random_integer(0,20))   
            if variable_type == "float" : random_constant = str(self.randomness.get_random_float(-10, 10))   
            if operation_type == "func": new_variable_string = operation + '(' + variable.get_name() + ',' + self.randomness.random_choice([random_constant, random_variable]) + ')'
            if operation_type == "binary": new_variable_string = variable.get_name() + operation + self.randomness.random_choice([random_constant, random_variable])
            if operation_type == "unary": new_variable_string = operation + variable.get_name()
            variable.set_name(new_variable_string)
        self.update_string()

    def get_fact_data(self, all_raw_data_entries):
        res = list()
        var_types = self.get_types()
        if self.name not in all_raw_data_entries.keys() or len(all_raw_data_entries[self.name]) == 0:
            return res
        for item in all_raw_data_entries[self.name]:
            table_entry = self.name + "("
            
            for idx, d in enumerate(item.strip().split("\t")):
                if var_types[idx].get_ancestor_type_name() == "symbol" and not '"' in d:
                    d = '"' + d + '"'
                if d == "-nan":
                    d = "(-1)^0.5"
                if d == "inf":
                    d = "1/0"
                table_entry += str(d) + ", "

            table_entry = table_entry[:-2] + ")."
            res.append(table_entry)
        return res

    def generate_fact_file(self, export_location, all_relations_raw_data_entries):
        # Converts self.fact_data in a string and exports to the program_path location as a fact file
        file_path = os.path.join(export_location, self.name + ".facts")
        data_as_a_string = "".join(i + "\n" for i in all_relations_raw_data_entries[self.name])
        create_file(data_as_a_string, file_path)

    def generate_decleration(self):
        declaration = ".decl " + self.name + "("
        for i in range(self.arity):
            declaration += string.ascii_uppercase[i] + ":" + self.variables_types[i].get_name() + ", "
        declaration = declaration[:-2] + ")"
        declaration += self.functional_keywords
        return declaration

    def add_eqrel_keywords(self):
        if self.arity != 2:
            return ""
        # if self.variables_types[0] == "symbol" or self.variables_types[1] == "symbol":
        #     return ""
        if self.variables_types[0] != self.variables_types[1]:
            return ""
        self.functional_keywords = " eqrel"
        return self.functional_keywords

    def generate_functional_keywords(self):
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_eqrel_relation"]:
            return self.add_eqrel_keywords()
        return ""
