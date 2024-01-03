from deopt.datalog.base_subgoal import BaseSubgoal
import string

class Z3Subgoal(BaseSubgoal):
    def negate_subgoal(self):
        self.negated = True
        self.string = "!" + self.string

    def generate_decleration(self):
        declaration = self.name + "("
        for i in range(self.arity):
            declaration += string.ascii_uppercase[i] + ":" + self.variables_types[i].get_name() + ", "
        declaration = declaration[:-2] + ") input"
        return declaration

    def get_fact_data(self, all_raw_data_entries):
        res = list()
        if self.name not in all_raw_data_entries.keys() or len(all_raw_data_entries[self.name]) == 0:
            return res
        for item in all_raw_data_entries[self.name]:
            table_entry = self.name + "("
            
            for idx, d in enumerate(item.strip().split("\t")):
                table_entry += str(d) + ", "

            table_entry = table_entry[:-2] + ")."
            res.append(table_entry)
        return res