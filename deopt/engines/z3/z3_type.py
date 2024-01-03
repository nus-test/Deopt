from deopt.datalog.var_type import VariableType

class Z3Type(VariableType):
    def get_declation(self):
        return "Z 64"