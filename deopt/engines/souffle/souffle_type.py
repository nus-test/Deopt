from deopt.datalog.var_type import VariableType

class SouffleType(VariableType):
    def get_declation(self):
        if self.get_relation() == "equivalencetype":
            return ".type " + self.get_name() + " = " + self.get_parent_type()[0].get_name()
        if self.get_relation() == "uniontype":
            return ".type " + self.get_name() + " = " + " | ".join([i.get_name() for i in self.get_parent_type()])
        if self.get_relation() == "subtype":
            return ".type " + self.get_name() + " <: " + self.get_parent_type()[0].get_name()
        if self.get_relation() == "recordtype":
            print("not support recordtype yet!")
            exit(0)
        if self.get_relation() == None:
            return ""
        return ""