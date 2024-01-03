from deopt.datalog.base_rule import BaseRule
from deopt.engines.souffle.souffle_subgoal import SouffleSubgoal
from deopt.engines.souffle.souffle_predicate import SoufflePredicate
import string 
from copy import deepcopy
from termcolor import colored
import time
import random


class SouffleRule(BaseRule):
    def generate_random_rule(self, allowed_types, available_relations):
        if self.randomness.get_random_integer(0, 99) < self.params["probability_of_recursive_rule"] and len(available_relations) > self.params["max_number_of_facts"]:
            self.head = deepcopy(self.randomness.random_choice(available_relations))
            # print("generate recusive rule for " + self.head.name)
            self.head_arity = self.head.arity
            for var in self.head.get_variables():
                # Search for a relations that contains a variable of this type
                while True:
                    # This will ALWAYS break at some point
                    rel = deepcopy(self.randomness.random_choice(available_relations))
                    is_type_match = False
                    for t in rel.get_types():
                        if t.is_subtype(var.get_type()):
                            is_type_match = True
                            break
                    if is_type_match:
                        self.subgoals.append(rel)
                        break
            # Add the remaining number of subgoals
            for i in range(self.number_of_subgoals - len(self.subgoals)):
                self.subgoals.append(deepcopy(self.randomness.random_choice(available_relations)))
            self.get_types_in_body()
            self.recursive_rule = True
        else:
            # Step 1: Generate body by choosing relations in the base program
            for i in range(self.number_of_subgoals):
                self.subgoals.append(deepcopy(self.randomness.random_choice(available_relations)))
            # Step 2: Get the used types in the body
            self.get_types_in_body()
            # Step 3: Create basic head subgoal
            self.head_arity = self.randomness.get_random_integer(1, self.params["max_head_arity"])
            self.head = SouffleSubgoal(randomness=self.randomness, arity=self.head_arity, params=self.params)
            self.head.generate_random_subgoal(type_used=self.types_used, all_allowed_types=allowed_types)
            self.functional_keywords = self.head.generate_functional_keywords()

        # for subgoal in self.subgoals:
        #     if not subgoal.name in self.dependent_subgoals:
        #         self.dependent_subgoals.append(subgoal.name)
        
        # Step 4: Make this a valid clause + create joins
        self.validate_rule()        
        # Done! Update string
        self.update_string()
        self.generate_decleration()


    def add_more_element_to_rule(self, available_relations, all_facts_raw_data_entries):
        # add negated subgoal in rule
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_negated"]:
            self.add_negated_subgoal(available_relations=available_relations)
        
        # underline a variable in a subgoal in rule
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_underline"]:
            self.underline_variable_in_subgoal()

        # add a constant for a variable in a subgoal
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_constant"]:
            self.add_constant_variable_in_subgoal(all_facts_raw_data_entries)
        
        # add predicts into rule
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_predicate"]:
            self.generate_predicates()

        # add binary operations in head
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_head_operations"]:
            self.insert_operations_in_head()

        # add binary operations in subgoals
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_rule_body_operations"]:
            self.insert_operations_in_rule_body()

        # add generative functors into rule
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_generator"]:
            self.add_generator()

        # add subsumption into rule 
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_subsumption"]:
            self.add_subsumption()

        self.get_dependent_subgoals()
        self.update_string()

    def add_negated_subgoal(self, available_relations): 
        success = True
        subgoal = deepcopy(self.randomness.random_choice(available_relations))
        if subgoal.name == self.head.name:
            return
        # Now for each variable type in this new subgoal, we have to get a variable that is already in the rule
        # and put it here. If we cannot find such a variable then we are in trouble and we cannot safely negate it 
        for i, var in enumerate(subgoal.get_variables()):
            # pick a random variable from the following list of copied variables
            variables_of_this_type = self.get_body_variables_of_type(var.get_type().get_ancestor_type())
            if len(variables_of_this_type) == 0:
                success = False
                break
            new_var = self.randomness.random_choice(variables_of_this_type)
            subgoal.update_variable_at_location(new_var, i)
        if not success: return
        # Negate this subgoal
        subgoal.negate_subgoal()
        # Add this subgoal in the list of subgoals
        self.subgoals.append(subgoal)
        self.update_string()

    def generate_disjunctive_rule(self, parent_rule, available_relations):
        """
            It takes the head as input and the list of all avaiable relations
            Will just generate 1 disjunctive rule
        """
        self.head = deepcopy(parent_rule.get_head())
        # For each variable type in the head, find a relation that conatins such a variable type and then insert it in the body
        for var in self.head.get_variables():
            # Search for a relations that contains a variable of this type
            while True:
                # This will ALWAYS break at some point
                rel = deepcopy(self.randomness.random_choice(available_relations))
                is_type_match = False
                for t in rel.get_types():
                    if t.is_subtype(var.get_type()):
                        is_type_match = True
                if is_type_match:
                    self.subgoals.append(rel)
                    break
        # Add the remaining number of subgoals
        for i in range(self.number_of_subgoals - len(self.subgoals)):
            self.subgoals.append(deepcopy(self.randomness.random_choice(available_relations)))
        self.get_types_in_body()
        self.validate_rule()
        self.update_string()

    def generate_decleration(self):
        self.decleration_string = ".decl " + self.head.get_name() + "("
        for i in range(self.head_arity):
            self.decleration_string += string.ascii_uppercase[i] + ":" + self.head.get_types()[i].get_name() + ", "
        self.decleration_string = self.decleration_string[:-2] + ")"
        if self.params["execution_mode"] == "fuzzing":
            if self.params["add_inline_and_magic"]:
                self.decleration_string += self.randomness.random_choice(["", "", "", "", "", "", "", "", " inline", "  no_inline", " magic", " no_magic"])
            self.decleration_string += self.functional_keywords
            if self.functional_keywords == "":
                self.decleration_string += self.randomness.random_choice(["", " brie", " btree"])

    def generate_decleration_for_single_query(self):
        decl_list = list()

        for subgoal in self.get_subgoals():
            if subgoal.generate_decleration() not in decl_list:
                decl_list.append(subgoal.generate_decleration())

        if self.aggregate_instance != None:
            decl_list += [i for i in self.aggregate_instance.aggregate_body_rule.generate_decleration_for_single_query() if not i in decl_list]

        if self.disjunctive_rule != None:
            decl_list += [i for i in self.disjunctive_rule.generate_decleration_for_single_query() if not i in decl_list]
        return decl_list

    def generate_input_decleration_for_single_query(self):
        input_decl_list = list()
        input_decl_list += [".input " + i.get_name() for i in self.get_subgoals() if ".input " + i.get_name() not in input_decl_list]
        if self.aggregate_instance != None:
            input_decl_list += [i for i in self.aggregate_instance.aggregate_body_rule.generate_input_decleration_for_single_query() if not i in input_decl_list]
        if self.disjunctive_rule != None:
            input_decl_list += [i for i in self.disjunctive_rule.generate_input_decleration_for_single_query() if not i in input_decl_list]
        return input_decl_list

    def generate_in_file_fact_for_single_query(self, all_raw_data_entries):
        fact_list = list()
        for subgoal in self.get_subgoals():
            fact_list += subgoal.get_fact_data(all_raw_data_entries)
        if self.aggregate_instance != None:
            fact_list += self.aggregate_instance.aggregate_body_rule.generate_in_file_fact_for_single_query(all_raw_data_entries)
        if self.disjunctive_rule != None:
            fact_list += self.disjunctive_rule.generate_in_file_fact_for_single_query(all_raw_data_entries)
        return list(set(fact_list))

    def generate_fact_file(self, program_path, all_raw_data_entries):
        for subgoal in self.get_subgoals():
            subgoal.generate_fact_file(program_path, all_raw_data_entries)
        if self.aggregate_instance != None:
            self.aggregate_instance.aggregate_body_rule.generate_fact_file(self.program_path, all_raw_data_entries)
        if self.disjunctive_rule != None:
            self.disjunctive_rule.generate_fact_file(program_path, all_raw_data_entries)


    def generate_predicates(self):
        for i in range(self.number_of_predicates):
            predicate = SoufflePredicate([i for i in self.all_variables if i.get_name() != '_'and not i.constant], self.randomness)
            if predicate.get_string() != "": self.predicates.append(predicate)
            self.update_string()

    def generate_heads(self, non_cyclic_relations):
        """ 
            Add multiple heads in the rule.
            Only updates the string of the rule. Nothing else is changed. Updating the rule will reset it to its original string.
        """
        valid_relations = list()
        for relation in non_cyclic_relations:
            flag = True
            for _type in relation.get_types():
                if _type not in self.types_used: 
                    flag = False
                    continue
            if flag: valid_relations.append(relation)
        
        # Do nothing if valid_relations is empty
        if len(valid_relations) == 0: return 1
        number_of_heads = self.randomness.get_random_integer(0, self.params["max_heads_in_mixed_rule"])
        new_head_string = ""
        # Now pick a realtion and rename the variables
        for i in range(number_of_heads):
            picked_relation = deepcopy(self.randomness.random_choice(valid_relations))
            for j, var in enumerate(picked_relation.get_variables()):
                picked_var = self.randomness.random_choice(self.get_body_variables_of_type(var.get_type()))
                picked_relation.update_variable_at_location(picked_var, j)
            new_head_string += ", " + picked_relation.get_string()
        self.string = self.head.get_string() + new_head_string + " " + self.string[self.string.find(":-"):]

    def insert_operations_in_head(self):
        """
            Insert operations in head
        """
        self.head.insert_operations(self.get_all_variables())
        self.update_string()

    def insert_operations_in_rule_body(self):
        modified_subgoal = self.randomness.random_choice(self.subgoals)
        modified_subgoal.insert_operations_in_rule_body(self.get_all_variables())
        self.update_string()

    def add_generator(self):
        selected_var = None
        bgn = None
        endExcl = None
        step = None
        
        if self.randomness.flip_a_coin():
            # add generator for number
            number_var_list = [i for i in self.get_all_variables() if i.get_type().get_ancestor_type().get_name() == "number" and i.get_name() != '_']
            if len(number_var_list) == 0:
                return
            selected_var = self.randomness.random_choice(number_var_list)
            bgn = self.randomness.get_random_integer(-999, 999)
            endExcl = self.randomness.get_random_integer(-999, 999)
            if self.randomness.flip_a_coin():
                step = self.randomness.get_random_integer(-100, 100)
        else:
            # add generator for float
            float_var_list = [i for i in self.get_all_variables() if i.get_type().get_ancestor_type().get_name() == "float" and i.get_name() != '_']
            if len(float_var_list) == 0:
                return
            selected_var = self.randomness.random_choice(float_var_list)
            bgn = self.randomness.get_random_float(-999, 998)
            endExcl = self.randomness.get_random_float(-999, 999)
            if self.randomness.flip_a_coin():
                step = self.randomness.get_random_float(-100, 100)
        self.generator = ""
        self.generator += selected_var.get_name() + " = range("
        self.generator += str(bgn) + "," + str(endExcl)
        if step != None:
            self.generator += "," + str(step)
        self.generator += ")"
        
        self.update_string()

    def add_subsumption(self):
        head1 = deepcopy(self.head)
        head2 = deepcopy(self.head)
        select_var_index = self.randomness.get_random_integer(0, head1.arity - 1)
        var1 = head1.variables[select_var_index]
        var2 = head2.variables[select_var_index]
        var1_name = var1.get_name() + "1"
        var2_name = var2.get_name() + "2"
        if len(var1_name) > 3:
            return
        var1.set_name(var1_name)
        var2.set_name(var2_name)
        head1.update_string()
        head2.update_string()
        var_type = head1.variables_types[select_var_index].get_ancestor_type().get_name()
        operations = ["<", ">"]
        operation = self.randomness.random_choice(operations)
        self.subsumption_string = head1.get_string() + " <= " + head2.get_string() + " :- "
        if var_type == "symbol":
            self.subsumption_string += "strlen(" + var1_name + ") " + operation + " strlen(" + var2_name + ")."
        else:
            self.subsumption_string += var1_name + operation + var2_name + "."
        
        self.update_string()
        if self.subsumption_string != "":
            self.decleration_string = self.decleration_string.replace(" btree", "")
            self.decleration_string = self.decleration_string.replace(" inline", "")

    def add_queryplan(self):
        if self.randomness.get_random_integer(0, 9) > self.params["probability_of_query_plan"]:
            return
        # get unique subgoals
        subgoals_string = []
        for i in self.subgoals:
            if i.negated:
                continue
            subgoals_string.append(i.get_string())
        subgoals_string = list(set(subgoals_string))
        if len(subgoals_string) < 2:
            return
        queryplan_list = [str(i + 1) for i in range(len(subgoals_string))]
        self.querypaln = ".plan "
        queryplan_idx = 0
        total_ql = 1
        while queryplan_idx < total_ql:
            random.shuffle(queryplan_list)
            self.querypaln += str(queryplan_idx) + ":(" + ",".join(queryplan_list) + ")" + ", "
            queryplan_idx = queryplan_idx + 1
        self.querypaln = self.querypaln[:-2]
        self.update_string()
        

    def update_string(self):
        # update the list of variables in the body as well
        self.all_variables = list()
        for subgoal in self.subgoals:
            self.all_variables = self.all_variables + subgoal.get_variables()

        # update string
        self.string = self.head.get_string()
        self.string += " :- "
        # body
        
        # Subgoal
        for subgoal in self.subgoals:
            self.string += subgoal.get_string() + ", "
        
        # Predicates
        for predicate in self.predicates:
            self.string += predicate.get_string() + ", "
        
        # Generator
        if self.generator != "":
            self.string += self.generator + ", "

        # Aggregate
        if self.aggregate is not None: self.string += self.aggregate
        if self.aggregate is None: self.string = self.string[:-2]

        self.string += "."

        # query plan
        if self.querypaln != None:
            self.string += "\n"
            self.string += self.querypaln

        # Disjunction rule
        if self.disjunctive_rule != None:
            self.string += "\n"
            self.string += self.disjunctive_rule.string

        if self.subsumption_string != "":
            self.string += "\n"
            self.string += self.subsumption_string