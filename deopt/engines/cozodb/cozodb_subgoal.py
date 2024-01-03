from deopt.datalog.base_subgoal import BaseSubgoal
from deopt.datalog.variable import Variable
from termcolor import colored
import os
from deopt.utils.file_operations import create_file
import string
from copy import deepcopy

class CozoDBSubgoal(BaseSubgoal):

    def negate_subgoal(self):
        self.negated = True
        self.string = "not " + self.string

    def insert_operations(self, all_rule_variables):
        """
            Number data type:
                Binary operations:
                    +, -, *, /, ^, %, min, max
                    C(i*2,j) :- A(i), B(j), i!=j, i = 2.1.
                    C(i*2,j) :- A(i), B(j), i!=j, i = 2.1.
                    C(i*2,j/i) :- A(i), B(j), i!=j, i = 2.1, j < 5.

                Unaray operations 
                    Negation:
                    C(-i*2,j/i) :- A(i), B(j), i!=j, i = 2.1, j < 5.
                    
                    Double negation:
                        C(--i*2,j/i) :- A(i), B(j), i!=j, i = 2.1, j < 5.

            String data type:
                Binary operations:
                    cat(A, "x")
                    cat(A, B)
        """
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
            if variable_type not in self.params["cozodb_types"]: continue
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
        """
            Number data type:
                Binary operations:
                    +, -, *, /, ^, %, min, max
                    C(i*2,j) :- A(i), B(j), i!=j, i = 2.1.
                    C(i*2,j) :- A(i), B(j), i!=j, i = 2.1.
                    C(i*2,j/i) :- A(i), B(j), i!=j, i = 2.1, j < 5.

                Unaray operations 
                    Negation:
                    C(-i*2,j/i) :- A(i), B(j), i!=j, i = 2.1, j < 5.
                    
                    Double negation:
                        C(--i*2,j/i) :- A(i), B(j), i!=j, i = 2.1, j < 5.

            String data type:
                Binary operations:
                    cat(A, "x")
                    cat(A, B)
        """
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
            if variable_type not in self.params["cozodb_types"]: continue
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
        variables = list(string.ascii_lowercase[:self.arity])
        variables = ", ".join(variables)

        if self.name not in all_raw_data_entries.keys() or len(all_raw_data_entries[self.name]) == 0:
            res.append(self.name + "[" + variables + "] <- []")
            return res
        
        table_entry = self.name + "[" + variables + "] <- [{}]"
        table_entry_string_list = []
        for item in all_raw_data_entries[self.name]:
            data_list = []
            for idx, d in enumerate(item.strip().split("\t")):
                if var_types[idx].get_ancestor_type_name() == "String" and not '"' in d:
                    d = '"' + d + '"'
                elif d == "None":
                    d = "null"
                elif d == "False":
                    d = "false"
                elif d == "True":
                    d = "true"
                data_list.append(str(d))
            table_entry_string_list.append("[" + ", ".join(data_list) + "]")

        res.append(table_entry.format(", ".join(table_entry_string_list)))
        return res

    def generate_decleration(self):
        return ""

    def update_string(self):
        self.string = self.name + "["
        for variable in self.variables:
            self.string += str(variable.get_name()) + ", "
        self.string = self.string[:-2] + "]"
        if self.negated: self.negate_subgoal()

    def generate_functional_keywords(self):
        pass
