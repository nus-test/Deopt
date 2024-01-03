from unittest import result
from deopt.datalog.base_predicate import BasePredicate
from termcolor import colored


class DDlogPredicate(BasePredicate):
    def generate_predicate(self):
        number_operations = ["==", 
            "!=", 
            "<", 
            ">", 
            "<=", 
            ">=", 
        ]
        string_operations = [
            "contains",          # function contains(s1: string, s2: string): bool
            "string_contains",   # extern function string_contains(s1: string, s2: string): bool
            "starts_with",       # function starts_with(s: string, prefix: string): bool
            "string_starts_with", # extern function string_starts_with(s: string, prefix: string)
            "ends_with",          # function ends_with(s: string, suffix: string): bool
            "string_ends_with" # extern function string_ends_with(s: string, suffix: string)
        ]
        operations = number_operations + string_operations
        operation = self.randomness.random_choice(operations)

        self.normal_var_list = [i for i in self.variables if not i.underline and not i.constant]
        number_var_list = [i for i in self.normal_var_list if i.get_type().get_ancestor_type_name() == "float" or i.get_type().get_ancestor_type_name() == "double" or i.get_type().get_ancestor_type_name() == "bigint" or i.get_type().get_ancestor_type_name().startswith("signed") or i.get_type().get_ancestor_type_name().startswith("bit")]

        string_var_list = [i for i in self.normal_var_list if i.get_type().get_ancestor_type_name() == "string"]

        if operation in number_operations and len(number_var_list) != 0:          
            var_1 = self.randomness.random_choice(number_var_list)
            type_1 = var_1.get_type()
            operand_2 = 0
            if type_1.get_name() == "float" or type_1.get_name() == "double":
                operand_2 = self.randomness.get_random_float(-100, 100)
            if type_1.get_name() == "bigint" or type_1.get_name().startswith("signed"):
                operand_2 = self.randomness.get_random_integer(-10,10)
            if type_1.get_name().startswith("bit"):
                operand_2 = self.randomness.get_random_integer(0,10)
            self.string =  var_1.get_name() + " " + operation + " " + str(operand_2)

        elif operation in string_operations and len(string_var_list) != 0:
            var_1 = self.randomness.random_choice(string_var_list)
            operand_2 = self.generate_string_operand()
            self.string = operation + "(" + var_1.get_name() + ", " + operand_2 + ")"
        else:
            pass

    def generate_number_operand(self):
        if True: # return a variable directly
            result_list = []
            result_list.extend([i.get_name() for i in self.normal_var_list if i.get_type().get_ancestor_type_name() == "float" or i.get_type().get_ancestor_type_name() == "double" or i.get_type().get_ancestor_type_name() == "bigint" or i.get_type().get_ancestor_type_name().startswith("signed") or i.get_type().get_ancestor_type_name().startswith("bit")])
            result_list.append(str(self.randomness.get_random_integer(-10,10)))
            result_list.append(str(self.randomness.get_random_float(-10, 10)))
            result_list.append("len(" + self.generate_string_operand() + ")")
            return self.randomness.random_choice(result_list)
        else:
            numeric_operations = ["+", "-", "*", "/", "%", "&", "^"]
            operand_1 = self.generate_number_operand()
            operand_2 = self.generate_number_operand()
            return "(" + operand_1 + self.randomness.random_choice(numeric_operations) + operand_2 + ")"

    def generate_string_operand(self):
        result_list = []
        result_list.extend([i.get_name() for i in self.normal_var_list if i.get_type().get_ancestor_type_name() == "string"])
        random_string = self.randomness.get_random_alpha_numeric_string(self.randomness.get_random_integer(1, 10))
        if not '"' in random_string:
            random_string = '"' + random_string + '"'
        result_list.append(random_string)
        return self.randomness.random_choice(result_list)