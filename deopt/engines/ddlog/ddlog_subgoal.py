from deopt.datalog.base_subgoal import BaseSubgoal
import string
from copy import deepcopy

class DDlogSubgoal(BaseSubgoal):

    def negate_subgoal(self):
        self.negated = True
        self.string = "not " + self.string

    def insert_operations(self, all_rule_variables):
        max_expression_adding_operations = self.randomness.get_random_integer(0, self.params["max_expression_adding_operations"])
        for i in range(max_expression_adding_operations):
            variable = self.randomness.random_choice(self.variables)
            variable_type = variable.get_type().get_ancestor_type().get_name()
            if variable_type not in self.params["ddlog_types"]: continue
            if variable_type == "bool": continue
            new_variable_string = ""
            operation = ""
            if variable_type == "string": operation = "++"
            else: operation = self.randomness.random_choice(["+", "-", "*", "/"])
            random_constant = ""
            random_variable = self.randomness.random_choice([i.get_name() for i in all_rule_variables if i.get_type().get_ancestor_type().get_name() == variable_type and i.get_name() != '_' and not i.constant])
            if variable_type == "string" and self.randomness.flip_a_coin():
                random_variable = '"${' + self.randomness.random_choice([i.get_name() for i in all_rule_variables if i.get_name() != '_' and not i.constant]) + '}"'
            if variable_type == "string": random_constant = '"' + self.randomness.get_random_alpha_string(1) + '"'
            else: random_constant = str(self.randomness.get_random_integer(0,20))
              
            new_variable_string = variable.get_name() + operation + self.randomness.random_choice([random_constant, random_variable])
            variable.set_name(new_variable_string)
        self.update_string()

    def insert_operations_in_rule_body(self, all_rule_variables):
        max_expression_adding_operations = self.randomness.get_random_integer(0, self.params["max_expression_adding_operations"])
        all_rule_variable_names = [n.get_name() for n in all_rule_variables]
        for i in range(max_expression_adding_operations):
            variable = self.randomness.random_choice(self.variables)
            if all_rule_variable_names.count(variable.get_name()) == 1:
                continue
            variable_type = variable.get_type().get_ancestor_type().get_name()
            if variable_type not in self.params["ddlog_types"]: continue
            if variable_type == "bool": continue
            new_variable_string = ""
            operation = ""
            random_constant = ""
            random_variable = self.randomness.random_choice([i.get_name() for i in all_rule_variables if i.get_type().get_ancestor_type().get_name() == variable_type and i.get_name() != '_' and not i.constant])
            if variable_type == "string": operation = "++"
            else: operation = self.randomness.random_choice(["+", "-", "*", "/"])
            if variable_type == "string": random_constant = '"' + self.randomness.get_random_alpha_string(1) + '"'
            else: random_constant = str(self.randomness.get_random_integer(0,20))

            new_variable_string = variable.get_name() + operation + self.randomness.random_choice([random_constant, random_variable])
            variable.set_name(new_variable_string)
        self.update_string()

    def generate_decleration(self):
        declaration = "input relation " + self.name + "("
        for i in range(self.arity):
            declaration += string.ascii_lowercase[i] + ": " + self.variables_types[i].get_name() + ", "
        declaration = declaration[:-2] + ")"
        declaration += self.functional_keywords
        return declaration

    def get_fact_data(self, all_raw_data_entries):
        res = list()
        var_types = self.get_types()

        if self.name not in all_raw_data_entries.keys() or len(all_raw_data_entries[self.name]) == 0:
            # print(self.name + " not in all raw data entries, please check")
            # print(str(all_raw_data_entries))
            # exit(0)
            return res

        for item in all_raw_data_entries[self.name]:
            table_entry = "insert " + self.name + "("
            
            for idx, d in enumerate(item.strip().split("\t")):
                if var_types[idx].get_ancestor_type_name() == "string" and not '"' in d:
                    d = '"' + d + '"'
                table_entry += str(d) + ", "

            table_entry = table_entry[:-2] + "),"
            res.append(table_entry)

        # Last entry should end with a semi colon
        res[-1] = res[-1][:-1] + ";"
        return res

