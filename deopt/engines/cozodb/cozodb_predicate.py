from deopt.datalog.base_predicate import BasePredicate
from termcolor import colored


class CozoDBPredicate(BasePredicate):
    def generate_number_predicate(self):
        comparion_operators = ["eq", "neq", "gt", "ge", "lt", "le"]
        operand_left = self.generate_number_operand()
        operand_right = self.generate_number_operand()
        operator = self.randomness.random_choice(comparion_operators)
        self.string = operator + "(" + operand_left + ", " + operand_right + ")"


    def generate_string_predicate(self):
        comparion_operators = ["str_includes", "starts_with", "ends_with"]
        operand_left = self.generate_string_operand()
        operand_right = self.generate_string_operand()
        operator = self.randomness.random_choice(comparion_operators)
        self.string = operator + "(" + operand_left + ", " + operand_right + ")"


    def generate_predicate(self):
        if len(self.variables) == 0:
            return
        predicate_type = self.randomness.random_choice([i.get_type().get_ancestor_type().get_name() for i in self.variables])

        if predicate_type == "Number":
            self.generate_number_predicate()
        
        if predicate_type == "String":
            self.generate_string_predicate()

    def generate_number_operand(self):
        if self.randomness.get_random_integer(0, 100) < 5:
            binary_operators = ["add", "sub", "div", "pow", "mod", "atan2", "max", "min"]
            operator = self.randomness.random_choice(binary_operators)
            operand_left = self.generate_number_operand()
            operand_right = self.generate_number_operand()
            if operator == "mod":
                while operand_right == "0":
                    operand_right = self.generate_number_operand()
            return operator + "(" + operand_left + ", " + operand_right + ")"
        else:
            operand = self.randomness.random_choice([i for i in self.variables])
            while operand == "_":
                operand = self.randomness.random_choice([i for i in self.variables])
            if operand.get_type().get_ancestor_type().get_name() == "Number":
                unary_operators = ["minus", "sqrt", "abs", "signum", "floor", "ceil", "round", "exp", "exp2", "ln", "log2",     "log10", "sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh", "asinh", "acosh", "atanh",    "deg_to_rad", "rad_to_deg", ""]
                operator = self.randomness.random_choice(unary_operators)
                if operator == "":
                    return operand.get_name()
                else:
                    return operator + "(" + operand.get_name() + ")"
            elif operand.get_type().get_ancestor_type().get_name() == "String":
                string_operator = ["length"]
                operator = self.randomness.random_choice(string_operator)
                return operator + "(" + operand.get_name() + ")"
            else:
                return str(self.randomness.get_random_integer(-10,10))
            
    def generate_string_operand(self):
        if self.randomness.get_random_integer(0, 100) < 5:
            binary_operators = ["concat"]
            operand_left = self.generate_string_operand()
            operand_right = self.generate_string_operand()
            operator = self.randomness.random_choice(binary_operators)
            return operator + "(" + operand_left + ", " + operand_right + ")"
        else:
            operand = self.randomness.random_choice([i for i in self.variables])
            while operand == "_":
                operand = self.randomness.random_choice([i for i in self.variables])
            if operand.get_type().get_ancestor_type().get_name() == "String":
                unary_operators = ["lowercase", "uppercase", "trim", "trim_start", "trim_end", ""]
                operator = self.randomness.random_choice(unary_operators)
                if operator == "":
                    return operand.get_name()
                else:
                    return operator + "(" + operand.get_name() + ")"
            elif operand.get_type().get_ancestor_type().get_name() == "Number":
                string_operator = ["to_string"]
                operator = self.randomness.random_choice(string_operator)
                return operator + "(" + operand.get_name() + ")"
            else:
                len = self.randomness.get_random_integer(1,10)
                return '"' + self.randomness.get_random_alpha_string(len) + '"'