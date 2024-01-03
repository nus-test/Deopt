from deopt.datalog.base_fact import BaseFact
from deopt.engines.z3.z3_subgoal import Z3Subgoal
from deopt.datalog.variable import Variable
import string
from copy import deepcopy

class Z3Fact(BaseFact):
    def generate_fact(self):
        self.name = self.randomness.get_lower_case_alpha_string(4)
        self.variables_types = [self.randomness.random_choice(self.allowed_types) for i in range(self.arity)]
        # Generate rows
        for i in range(self.number_of_rows):
            table_entry = self.name + "("
            raw_data_row = ""
            for j in range(self.arity):
                data_type = self.variables_types[j]
                data_item = self.generate_data_item(data_type)
                table_entry += str(data_item) + ", "
                raw_data_row += str(data_item) + "\t"
            table_entry = table_entry[:-2] + ")."
            self.raw_data_entries.append(raw_data_row)
            self.fact_data.append(table_entry)


    def get_fact_as_a_relation(self):
        fact_subgoal = Z3Subgoal(randomness=self.randomness, arity=self.arity, params=self.params)
        fact_subgoal.generate_subgoal(name=self.name, 
                                        variables=[Variable(name=string.ascii_uppercase[i], vtype=self.variables_types[i]) for i in range(self.arity)], 
                                        variables_types=self.variables_types)
        return fact_subgoal

    def generate_decleration(self):
        self.declaration = self.name + "("
        for i in range(self.arity):
            self.declaration += string.ascii_uppercase[i] + ":" + self.variables_types[i].get_name() + ", "
        self.declaration = self.declaration[:-2] + ") input"
 
    def generate_data_item(self, type):
        if type.get_name() == "Z":
            return self.randomness.get_random_integer(0,50)
