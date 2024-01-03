from abc import ABC, abstractmethod

class VariableType(object):
    def __init__(self, name, parent_type, relation):
        self.name = name
        self.parent_type = parent_type
        self.relation = relation  # [equivalencetypes, subtype, uniontype, recordtype]

    def get_name(self):
        return self.name

    def get_parent_type(self):
        return self.parent_type

    def get_relation(self):
        return self.relation

    def get_ancestor_type(self):
        current_type = self
        # each type can only have one ancestor type
        while current_type.get_parent_type() != None:
            current_type = current_type.get_parent_type()[0]
        return current_type

    def get_ancestor_type_name(self):
        current_type = self
        # each type can only have one ancestor type
        while current_type.get_parent_type() != None:
            current_type = current_type.get_parent_type()[0]
        return current_type.get_name()

    def is_subtype(self, another_type):
        # subtype contains equivalence type
        if self.name == another_type.get_name():
            return True
        if self.parent_type == None:
            if self.is_equivalence_type(another_type):
                return True
            if self.name != another_type.get_name():
                return False
        for p_t in self.parent_type:
            if p_t.is_subtype(another_type):
                return True
        return False

    def is_equivalence_type(self, another_type):
        # subtype contains equivalence type
        if self.name == another_type.get_name():
            return True
        type_1 = self
        while type_1.parent_type != None and type_1.get_relation() == "equivalencetype":
            type_1 = type_1.parent_type[0]
            if type_1.get_name() == another_type.get_name():
                return True
        type_2 = another_type
        while type_2.parent_type != None and type_2.get_relation() == "equivalencetype":
            type_2 = type_2.parent_type[0]
            if type_2.get_name() ==self.name:
                return True
        return False

    @abstractmethod
    def get_declation(self):
        pass