from deopt.datalog.base_fact import BaseFact
from deopt.engines.cozodb.cozodb_subgoal import CozoDBSubgoal
from deopt.datalog.variable import Variable
from deopt.utils.file_operations import create_file
import string
import os


class CozoDBFact(BaseFact):

    def generate_fact_file(self, export_location):
        # Converts self.fact_data in a string and exports to the program_path location as a fact file
        file_path = os.path.join(export_location, self.name + ".facts")
        data_as_a_string = "".join(i + "\n" for i in self.raw_data_entries)
        create_file(data_as_a_string, file_path)

    def generate_fact(self):
        self.name = self.randomness.get_lower_case_alpha_string(4)
        invalid_name = []
        while self.name in invalid_name:
            self.name = self.randomness.get_lower_case_alpha_string(4)
        self.variables_types = [self.randomness.random_choice(self.allowed_types) for i in range(self.arity)]

        variables = list(string.ascii_lowercase[:self.arity])
        variables = ", ".join(variables)
        table_entry = self.name + "[" + variables + "] <- [{}]"
        table_data_entry_string_list = []
        for i in range(self.number_of_rows):
            data_list = []
            for j in range(self.arity):
                data_type = self.variables_types[j]
                data_item = self.generate_data_item(data_type)
                data_list.append(str(data_item))
            self.raw_data_entries.append("\t".join(data_list))
            table_data_entry_string_list.append("[" + ", ".join(data_list) + "]")
        self.fact_data.append(table_entry.format(", ".join(table_data_entry_string_list)))

    def get_fact_as_a_relation(self):
        fact_subgoal = CozoDBSubgoal(randomness=self.randomness, arity=self.arity, params=self.params)
        fact_subgoal.generate_subgoal(name=self.name, 
                                        variables=[Variable(name=string.ascii_uppercase[i], vtype=self.variables_types[i]) for i in range(self.arity)], 
                                        variables_types=self.variables_types)
        return fact_subgoal

    def generate_decleration(self):
        variables = list(string.ascii_lowercase[:self.arity])
        variables = ", ".join(variables)
        self.declaration = ":create {} {{{}}}".format(self.name, variables)

    def generate_data_item(self, type):
        if type.get_ancestor_type_name() == "Number":
            return self.randomness.random_choice([self.randomness.get_random_float(-10, 10), self.randomness.get_random_float(-10, 10), 0.0, -0.0])
        
        if type.get_ancestor_type_name() == "String":
            return '"' + self.randomness.get_random_alpha_numeric_string(self.randomness.get_random_integer(1, 10)) + '"'

        if type.get_ancestor_type_name() == "Null":
            return 'null'
        
        if type.get_ancestor_type_name() == "Bool":
            return self.randomness.random_choice(['false', 'true'])

    def get_fact_input_string(self):
        return ""