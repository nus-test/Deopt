from queue import Queue
from deopt.datalog.base_program import BaseProgram
from deopt.engines.souffle.souffle_rule import SouffleRule
from deopt.engines.souffle.souffle_fact import SouffleFact
from deopt.engines.souffle.souffle_aggregate import SouffleAggregate
from deopt.engines.souffle.souffle_subgoal import SouffleSubgoal
from deopt.engines.souffle.souffle_type import SouffleType
from deopt.utils.file_operations import create_file, read_file
from deopt.runner.souffle_runner import SouffleRunner
from copy import deepcopy
from termcolor import colored
import os
import shutil
from collections import Counter

class SouffleProgram(BaseProgram):
    def get_allowed_types(self):
        for t in self.params["souffle_types"]:
            s_t = SouffleType(name=t, parent_type=None, relation=None)
            self.allowed_types.append(s_t)
        # self.allowed_types = deepcopy(self.params["souffle_types"])
        support_relations = ["equivalencetype", "subtype"] #  "uniontype", "recordtype"
        for i in range(self.randomness.get_random_integer(0, self.params["max_number_of_random_type"])):
            type_name = "type" + self.randomness.get_first_upper_and_lower_case_alpha_string(4)
            while self.is_duplicate_type(type_name):
                type_name = "type" + self.randomness.get_first_upper_and_lower_case_alpha_string(4)
            relation = self.randomness.random_choice(support_relations)
            parent_type = [self.randomness.random_choice(self.allowed_types)]
            s_t = SouffleType(name=type_name, parent_type=parent_type, relation=relation)
            self.allowed_types.append(s_t)
        for t in self.allowed_types:
            if t.get_declation() != "":
                self.type_declarations.append(t.get_declation())

    def generate_facts(self):
        # Generate fact tables
        for i in range(self.number_of_facts):
            fact_table = SouffleFact(randomness=self.randomness, params=self.params, allowed_types=self.allowed_types)
            while self.is_duplicate_relation(fact_table.name):
                fact_table = SouffleFact(randomness=self.randomness, params=self.params, allowed_types=self.allowed_types)
            # Add information about this fact table in the program
            self.declarations.append(fact_table.get_decleration())
            self.facts.append(fact_table)
            self.all_relations.append(fact_table.get_fact_as_a_relation())
            self.all_relations_raw_data_entries[fact_table.name] = deepcopy(fact_table.raw_data_entries)
            if self.params["in_file_facts"] is False: self.inputs.append(fact_table.get_fact_input_string())

    def generate_single_rule(self):
        rule = SouffleRule(verbose=self.verbose, randomness=self.randomness, params=self.params)
        # generate the basic subgoal in rule
        rule.generate_random_rule(allowed_types=self.allowed_types, available_relations=self.all_relations)

        # get more complex rule
        rule.add_more_element_to_rule(available_relations=self.all_relations, all_facts_raw_data_entries=self.all_relations_raw_data_entries)

        # add aggregate into rule
        if self.randomness.get_random_integer(0, 9) < self.params["probability_of_aggregate"]:
            aggregate = SouffleAggregate(parent_rule=rule, 
                                            verbose=self.verbose, 
                                            randomness=self.randomness, 
                                            params=self.params,
                                            allowed_types=self.allowed_types,
                                            available_relations=self.all_relations,
                                            all_facts_raw_data_entries=self.all_relations_raw_data_entries)
            if aggregate.external_variable is None or aggregate.internal_variable is None or aggregate.chosen_aggregate is None or aggregate.aggregate_body is None:
                aggregate = None
            else:
                rule.add_aggregate(aggregate.get_string())
                rule.aggregate_instance = aggregate
                rule.dependent_subgoals.extend(aggregate.aggregate_body_rule.dependent_subgoals)

        rule.update_string()

        return rule

    def get_real_value(self, item, type_list):
        item = item.strip()
        item = item.split('\t')
        res = list()
        for idx, value in enumerate(item):
            if value == "-nan" or value == "inf":
                res.append(value)
            elif type_list[idx].get_ancestor_type_name() == "number":
                res.append(int(value))
            elif type_list[idx].get_ancestor_type_name() == "symbol":
                value = value.replace('"', '')
                res.append(str(value))
            elif type_list[idx].get_ancestor_type_name() == "unsigned":
                res.append(int(value))
            elif type_list[idx].get_ancestor_type_name() == "float":
                res.append(float(value))
            else:
                print("different shape of result!")
                exit(0)
        return res

    def pretty_print_program(self):
        pass # the origonal program is so big so we don't want to print it
        for decl in self.type_declarations: print(colored(decl, "green", attrs=["bold"]))
        print("\n\n")
        
        for decl in self.declarations: print(colored(decl, "red", attrs=["bold"]))
        print("")
        
        for _input in self.inputs: print(colored(_input, "green", attrs=["bold"]))
        print("")

        print(colored( ".output " + self.output_rule.get_head().get_name(), "green", attrs=["bold"]))   
        
        print("\n\n")
        if self.params["in_file_facts"]:
            for fact in self.facts:
                for row in fact.get_fact_data(): print(colored(row, "yellow", attrs=["bold"]))
            print("")
        
        for thing in self.other_things:
            print(colored(thing, "yellow", attrs=["bold"]))
        
        print("")
        for rule in self.all_rules:
            rule_string = deepcopy(rule.get_string())

            # Parsed rule
            if rule_string.find("parsed rule") != -1:
                rule_string = rule_string.replace("//parsed rule", "")
                print(colored(rule_string, "blue", attrs=["bold"]), end="")
                print(colored("//parsed rule", "green", attrs=["bold"]))

            # Cycle breaker rule
            if rule_string.find("cycle breaker rule") != -1:
                rule_string = rule_string.replace("//cycle breaker rule", "")
                print(colored(rule_string, "blue", attrs=["bold"]), end="")
                print(colored("//cycle breaker rule", "red", attrs=["bold"]))

            # Mixed rule
            if rule_string.find("mixed rule") != -1:
                rule_string = rule_string.replace("//mixed rule", "")
                print(colored(rule_string, "blue", attrs=["bold"]), end="")
                print(colored("//mixed rule", "magenta", attrs=["bold"]))

            # Complex rule
            if rule_string.find("complex rule") != -1:
                rule_string = rule_string.replace("//complex rule", "")
                print(colored(rule_string, "blue", attrs=["bold"]), end="")
                print(colored("//complex rule", "red", attrs=["bold"]))

            # Simple rule
            if rule_string.find("simple rule") != -1:
                rule_string = rule_string.replace("//simple rule", "")
                print(colored(rule_string, "blue", attrs=["bold"]), end="")
                print(colored("//simple rule", "green", attrs=["bold"]))

            # Transformed rule
            if rule_string.find("transformed rule") != -1:
                print(colored(rule_string, "yellow", attrs=["bold"]))


    def create_whole_program_string(self):
        """
            Souffle program structure:
                declarations
                facts
                rule definitions  
                output declaration  
        """
        self.program_string = ""

        # type declarations
        for t_d in self.type_declarations:
            self.program_string += t_d + "\n"
        self.program_string += "\n"

        # declarations
        for decl in self.declarations:
            if decl.find(self.output_rule.get_head().get_name()) != -1:
                self.program_string += decl.replace(" inline", "") + "\n"
            else:
                self.program_string += decl + "\n"
        if not self.output_rule.recursive_rule:
            self.program_string += self.output_rule.get_declaration().replace(" inline", "") + "\n"
        
        self.program_string += "\n\n"
        # Inputs
        for _input in self.inputs:
            self.program_string += _input + "\n"

        # facts (only when in_file_facts is true)
        if self.params["in_file_facts"]:
            self.program_string += "\n\n"
            for fact in self.facts:
                for row in fact.get_fact_data():
                    self.program_string += row + "\n"

        # other things that are kinda hard to parse
        for thing in self.other_things:
            self.program_string += thing + "\n"

        # rule definitions
        self.program_string += "\n\n"
        for rule in self.all_rules:
            self.program_string += rule.get_string() + "\n"
        self.program_string += self.output_rule.get_string() + "\n"
        # output
        self.program_string += "\n" + ".output " + self.output_rule.get_head().get_name() + "\n"

    def export_whole_program_string(self):
        """
            Export original program string
        """
        self.create_whole_program_string()

        self.program_file_path = os.path.join(self.program_path, "orig_rules.dl")
        self.logs.set_log_file_name("orig.log")
        self.logs.set_log_file_path(self.program_path)
        if not os.path.exists(self.program_path):
            os.mkdir(self.program_path)
        create_file(self.program_string, self.program_file_path)
        
        # Create .facts file here as well
        if self.params["in_file_facts"] is False:
            for fact in self.facts: 
                fact.generate_fact_file(self.program_path)


    def create_single_query_string(self, single_rule):
        """
            Souffle program structure:
                declarations
                facts
                rule definitions  
                output declaration  
        """
        self.single_query_string = ""

        # type declarations
        for t_d in self.type_declarations:
            self.single_query_string += t_d + "\n"
        self.single_query_string += "\n"

        # declarations
        self.single_query_string += "\n".join(single_rule.generate_decleration_for_single_query())
        self.single_query_string += "\n"

        
        # use self.output_rule.head.generate_decleration() but not self.output_rule.get_decleration() because
        # subgoal.generate_decleration() do not generate keywords
        if ".decl " + single_rule.head.name not in self.single_query_string:
            self.single_query_string += single_rule.head.generate_decleration().replace(" inline", "") + "\n"

        self.single_query_string += "\n\n"

        # Inputs
        if not self.params["in_file_facts"]:
            self.single_query_string += "\n".join(single_rule.generate_input_decleration_for_single_query())
            
        self.single_query_string += "\n\n"

        # facts (only when in_file_facts is true)
        if self.params["in_file_facts"]:
            self.single_query_string += "\n".join(single_rule.generate_in_file_fact_for_single_query(self.all_relations_raw_data_entries))

        # rule definitions
        self.single_query_string += "\n\n"
        rule_string = single_rule.get_string()
        if ".plan" in rule_string:    # remove query plan
            rs = rule_string.split("\n")
            rs = [i for i in rs if not ".plan" in i]
            rule_string = "\n".join(rs)
        self.single_query_string += rule_string + "\n"
        # output
        self.single_query_string += "\n" + ".output " + single_rule.get_head().get_name() + "\n"


    def export_single_query_string(self, single_rule):
        """
            Export single query program string
        """
        self.create_single_query_string(single_rule)

        self.single_query_file_path = os.path.join(self.program_path, "single_query.dl")
        self.logs.set_log_file_name("orig.log")
        self.logs.set_log_file_path(self.program_path)
        if not os.path.exists(self.program_path):
            os.mkdir(self.program_path)
        create_file(self.single_query_string, self.single_query_file_path)
        
        # Create .facts file here as well
        if self.params["in_file_facts"] is False:
            single_rule.generate_fact_file(self.program_path, self.all_relations_raw_data_entries)


    def run_single_query_program(self, single_rule):
        self.export_single_query_string(single_rule)
        # self.add_log_text("Current rule: " + single_rule.get_string())
        if len(self.single_query_string) < 10000:
            self.add_log_text("Current rule: " + self.single_query_string)

        program_runner = SouffleRunner(params=self.params, program=self)
        signal = program_runner.run_single_query(engine_options="", output_relation_name=single_rule.head.name)
        if signal == 3:
            return 3

        if signal != 0 or not os.path.exists(self.get_single_query_result_path()):
            # print(colored("Signal = " + str(signal), "red", attrs=["bold"]))
            # print(colored("SOMETHING WENT WRONG. Check it out please", "red", attrs=["bold"]))           
            print(colored("Unknown error in reference program.", "red", attrs=["bold"]))    
            self.add_log_text("XXXXX SOMETHING WENT WRONG. PLEASE CHECK IT OUT. XXXXXX")
            self.dump_program_log_file()
            return signal

        # if len(read_file(self.get_single_query_result_path())) == 0:
        #     return 3

        return 0

    def run_whole_program(self):
        program_runner = SouffleRunner(params=self.params, program=self)
        # engine_option = self.randomness.random_choice(self.params["souffle_options"])
        engine_option = ""
        engine_option += " ".join(self.randomness.random_sample(self.params["souffle_options"]))
        if self.randomness.flip_a_coin():
            engine_option += " --disable-transformers=" + ",".join(self.randomness.random_sample(self.params["souffle_disable_options"]))
        if self.params["execution_mode"] != "fuzzing":
            engine_option = ""
        signal = program_runner.run_original(engine_options=engine_option)
        if signal == 3:
            return 3

        if signal != 0 or not os.path.exists(self.get_output_result_file_path()):
            # print(colored("Signal = " + str(signal), "red", attrs=["bold"]))
            # print(colored("SOMETHING WENT WRONG. Check it out please", "red", attrs=["bold"]))       
            print(colored("Unknown error in optimized program.", "red", attrs=["bold"]))      
            self.add_log_text("XXXXX SOMETHING WENT WRONG. PLEASE CHECK IT OUT. XXXXXX")
            self.dump_program_log_file()
            return signal

        return 0


    def build_the_minimal_test_case(self):
        temp_rule_list = list()
        temp_relations = Queue()
        temp_included_subgoals = list()

        temp_rule_list.append(deepcopy(self.output_rule))
        for subgoal in self.output_rule.subgoals:
            temp_relations.put(deepcopy(subgoal))
            

        while not temp_relations.empty():
            selected_subgoal = temp_relations.get()
            selected_subgoal_name = selected_subgoal.get_name()
            for rule in self.all_rules:
                if rule.head.get_name == selected_subgoal_name:
                    temp_rule_list.insert(0, deepcopy(rule))
                    for subgoal in rule.subgoals:
                        temp_relations.put(deepcopy(subgoal))
                    break
            
