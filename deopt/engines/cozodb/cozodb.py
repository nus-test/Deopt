from queue import Queue
from deopt.datalog.base_program import BaseProgram
from deopt.engines.cozodb.cozodb_rule import CozoDBRule
from deopt.engines.cozodb.cozodb_fact import CozoDBFact
from deopt.engines.cozodb.cozodb_aggregate import CozoDBAggregate
from deopt.engines.cozodb.cozodb_subgoal import CozoDBSubgoal
from deopt.engines.cozodb.cozodb_type import CozoDBType
from deopt.utils.file_operations import create_file, read_file
from deopt.runner.cozodb_runner import CozoDBRunner
from copy import deepcopy
from termcolor import colored
import os
import shutil
import string
from collections import Counter

class CozoDBProgram(BaseProgram):
    def get_allowed_types(self):
        for t in self.params["cozodb_types"]:
            s_t = CozoDBType(name=t, parent_type=None, relation=None)
            self.allowed_types.append(s_t)

    def generate_facts(self):
        # Generate fact tables
        for i in range(self.number_of_facts):
            fact_table = CozoDBFact(randomness=self.randomness, params=self.params, allowed_types=self.allowed_types)
            while self.is_duplicate_relation(fact_table.name):
                fact_table = CozoDBFact(randomness=self.randomness, params=self.params, allowed_types=self.allowed_types)
            # Add information about this fact table in the program
            self.declarations.append(fact_table.get_decleration()) 
            self.facts.append(fact_table)
            self.all_relations.append(fact_table.get_fact_as_a_relation())
            self.all_relations_raw_data_entries[fact_table.name] = deepcopy(fact_table.raw_data_entries)
            if self.params["in_file_facts"] is False: self.inputs.append(fact_table.get_fact_input_string())

    def generate_single_rule(self):
        rule = CozoDBRule(verbose=self.verbose, randomness=self.randomness, params=self.params)
        # generate the basic subgoal in rule
        rule.generate_random_rule(allowed_types=self.allowed_types, available_relations=self.all_relations)

        # get more complex rule
        rule.add_more_element_to_rule(available_relations=self.all_relations, all_facts_raw_data_entries=self.all_relations_raw_data_entries)

        rule.update_string()

        return rule


    def get_real_value(self, item, type_list):
        item = item.strip()
        item = item.split('\t')
        res = list()
        for idx, value in enumerate(item):
            if idx >= len(type_list):
                print("different shape of result!")
                print(str(type_list))
                print(str(item))
                exit(0)
            if value == "0.0" or value == "-0.0":
                res.append(value)
            elif type_list[idx].get_ancestor_type_name() == "Number":
                if "." in value:
                    res.append(float(value))
                else:
                    res.append(int(value))
            elif value == "None":
                res.append("null")
            elif type_list[idx].get_ancestor_type_name() == "String":
                value = value.replace('"', '')
                res.append(str(value))
            elif type_list[idx].get_ancestor_type_name() == "Bool":
                res.append(value)
            elif type_list[idx].get_ancestor_type_name() == "Null":
                res.append("null")
            else:
                print("different shape of result!")
                exit(0)
        return res


    def create_whole_program_string(self):
        """
            CozoDB program structure:
                declarations
                facts
                rule definitions  
                output declaration  (this should be a separate string)
        """
        self.program_string = ""

        for fact in self.facts:
            for row in fact.get_fact_data():
                self.program_string += row + "\n"

        # rule definitions
        self.program_string += "\n\n"
        for rule in self.all_rules:
            self.program_string += rule.get_string() + "\n"
        self.program_string += self.output_rule.get_string() + "\n"
        
        # output string, '?[a] := a[a]'
        variables = list(string.ascii_lowercase[:self.output_rule.head.arity])
        variables = ", ".join(variables)
        self.program_string += "?[" + variables + "] := " + self.output_rule.head.name + "[" + variables + "]"

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


    def create_single_query_string(self, single_rule):
        """
            CozoDB program structure:
                declarations
                facts
                rule definitions  
                output declaration  (this should be a separate string)
        """
        self.single_query_string = ""

        self.single_query_string += "\n".join(single_rule.generate_in_file_fact_for_single_query(self.all_relations_raw_data_entries))

        # rule definitions
        self.single_query_string += "\n\n"
        rule_string = single_rule.get_string()

        self.single_query_string += rule_string + "\n"

        # output
        variables = list(string.ascii_lowercase[:single_rule.head.arity])
        variables = ", ".join(variables)
        self.single_query_string += "?[" + variables + "] := " + single_rule.head.name + "[" + variables + "]"


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
        


    def run_single_query_program(self, single_rule):
        self.export_single_query_string(single_rule)
        if len(self.single_query_string) < 10000:
            self.add_log_text("Current rule: " + self.single_query_string)

        program_runner = CozoDBRunner(params=self.params, program=self)
        signal = program_runner.run_single_query(self.single_query_string)
        if signal == 3:
            return 3

        if signal != 0 or not os.path.exists(self.get_single_query_result_path()):      
            print(colored("Unknown error in reference program.", "red", attrs=["bold"]))    
            self.add_log_text("XXXXX SOMETHING WENT WRONG. PLEASE CHECK IT OUT. XXXXXX")
            self.dump_program_log_file()
            return signal

        return 0

    def run_whole_program(self):
        self.export_whole_program_string()
        program_runner = CozoDBRunner(params=self.params, program=self)
        signal = program_runner.run_original(self.program_string)
        if signal == 3:
            return 3

        if signal != 0 or not os.path.exists(self.get_output_result_file_path()):   
            print(colored("Unknown error in optimized program.", "red", attrs=["bold"]))      
            self.add_log_text("XXXXX SOMETHING WENT WRONG. PLEASE CHECK IT OUT. XXXXXX")
            self.dump_program_log_file()
            return signal

        return 0
            
