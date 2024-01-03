from deopt.datalog.base_program import BaseProgram
from deopt.engines.z3.z3_rule import Z3Rule
from deopt.engines.z3.z3_fact import Z3Fact
from deopt.engines.z3.z3_type import Z3Type
from deopt.runner.z3_runner import Z3Runner
from copy import deepcopy
from termcolor import colored
import os
from deopt.utils.file_operations import create_file, read_file

class Z3Program(BaseProgram):

    def get_allowed_types(self):
        # self.allowed_types = deepcopy(self.params["z3_types"])
        for t in self.params["z3_types"]:
            d_t = Z3Type(name=t, parent_type=None, relation=None)
            self.allowed_types.append(d_t)
        for t in self.allowed_types:
            if t.get_declation() != "":
                self.type_declarations.append(t.get_declation())

    def generate_single_rule(self):
        """
            Simplest rules possible
        """
        # Generate simple rules
        rule = Z3Rule(verbose=self.verbose, randomness=self.randomness, params=self.params)
        fact_list = [i.name for i in self.facts]
        rule.generate_random_rule(allowed_types=self.allowed_types, available_relations=self.all_relations, fact_list=fact_list)
        rule.add_more_element_to_rule(available_relations=self.all_relations, all_facts_raw_data_entries=self.all_relations_raw_data_entries)
        
        rule.update_string()

        return rule

    # def save_the_last_rule(self):
    #     if self.output_rule.recursive_rule:
    #         pass
    #     else:
    #         self.declarations.append(self.output_rule.get_declaration())
    #         self.all_relations.append(self.output_rule.get_head())
    #         self.all_relations_raw_data_entries[self.output_rule.head.get_name()]= deepcopy(read_file(self.get_output_result_file_path()))
    #         self.all_rules_raw_data_entries.append(read_file(self.get_output_result_file_path()))
    #     self.all_rules.append(deepcopy(self.output_rule))

    def generate_facts(self):
        for i in range(self.number_of_facts):
            fact_table = Z3Fact(randomness=self.randomness, params=self.params, allowed_types=self.allowed_types)
            self.declarations.append(fact_table.get_decleration())
            self.facts.append(fact_table)
            self.all_relations.append(fact_table.get_fact_as_a_relation())
            self.all_relations_raw_data_entries[fact_table.name] = deepcopy(fact_table.raw_data_entries)

    def get_real_value(self, item, type_list):
        item = item.strip()
        item = item.split('\t')
        res = list()
        for idx, value in enumerate(item):
            if type_list[idx].get_ancestor_type_name() == "Z":
                res.append(int(value))
            else:
                print("different shape of result!")
                exit(0)
        return res

    def pretty_print_program(self):
        for decl in self.type_declarations: print(colored(decl, "green", attrs=["bold"]))
        print("\n\n")        
        for decl in self.declarations: print(colored(decl, "red", attrs=["bold"]))
        print(colored( self.output_rule.get_declaration() + " printtuples" , "green", attrs=["bold"]))   
        print("\n")
        for fact in self.facts:
            for row in fact.get_fact_data(): print(colored(row, "yellow", attrs=["bold"]))
        print("")
        for rule in self.all_rules:
            rule_string = deepcopy(rule.get_string())
            # Mixed rule
            if rule_string.find("mixed rule") != -1:
                rule_string = rule_string.replace("##mixed rule", "")
                print(colored(rule_string, "blue", attrs=["bold"]), end="")
                print(colored("##mixed rule", "magenta", attrs=["bold"]))
            if rule_string.find("simple rule") != -1:
                rule_string = rule_string.replace("##simple rule", "")
                print(colored(rule_string, "blue", attrs=["bold"]), end="")
                print(colored("##simple rule", "green", attrs=["bold"]))
            # Transformed rule
            if rule_string.find("transformed rule") != -1:
                print(colored(rule_string, "yellow", attrs=["bold"]))


    def create_whole_program_string(self):
        """
            Z3 program structure:
                declarations
                facts
                rule definitions  
                output declaration  
        """
        self.program_string = ""

        # type declaration
        for type_decl in self.type_declarations:
            self.program_string += type_decl + "\n"
        self.program_string += "\n"
        # declarations
        for decl in self.declarations:
            self.program_string += decl + "\n"
        self.program_string += self.output_rule.get_declaration() + " printtuples"        
        self.program_string += "\n\n"
        # facts (only when in_file_facts is true)
        self.program_string += "\n\n"
        for fact in self.facts:
            for row in fact.get_fact_data():
                self.program_string += row + "\n"
        # rule definitions
        self.program_string += "\n\n"
        for rule in self.all_rules:
            self.program_string += rule.get_string() + "\n"
        self.program_string += self.output_rule.get_string() + "\n"


    def export_whole_program_string(self):
        """
            Export original program string
        """
        self.create_whole_program_string()

        self.program_file_path = os.path.join(self.program_path, "orig_rules.datalog")
        self.logs.set_log_file_name("orig.log")
        self.logs.set_log_file_path(self.program_path)
        if not os.path.exists(self.program_path):
            os.mkdir(self.program_path)
        create_file(self.program_string, self.program_file_path)
        

    def create_single_query_string(self, single_rule):
        """
            Z3 program structure:
                declarations
                facts
                rule definitions  
                output declaration  
        """
        self.single_query_string = ""

        # type declaration
        for type_decl in self.type_declarations:
            self.single_query_string += type_decl + "\n"
        self.single_query_string += "\n"

        # declarations
        self.single_query_string += single_rule.get_declaration() + " printtuples\n"
        for subgoal in single_rule.get_subgoals():
            if subgoal.generate_decleration() not in self.single_query_string and subgoal.name not in self.single_query_string:
                self.single_query_string += subgoal.generate_decleration() + "\n"
        # self.single_query_string += single_rule.get_declaration() + " printtuples"        
        # self.single_query_string += "\n"
        # facts (only when in_file_facts is true)
        self.single_query_string += "\n\n"
        for subgoal in single_rule.get_subgoals():
            for row in subgoal.get_fact_data(self.all_relations_raw_data_entries):
                self.single_query_string += row + "\n"
        # rule definitions
        self.single_query_string += "\n\n"
        self.single_query_string += single_rule.get_string() + "\n"

    def export_single_query_string(self, single_rule):
        """
            Export single query program string
        """
        self.create_single_query_string(single_rule)

        self.single_query_file_path = os.path.join(self.program_path, "single_query.datalog")
        self.logs.set_log_file_name("orig.log")
        self.logs.set_log_file_path(self.program_path)
        if not os.path.exists(self.program_path):
            os.mkdir(self.program_path)
        create_file(self.single_query_string, self.single_query_file_path)

    def run_single_query_program(self, single_rule):
        self.export_single_query_string(single_rule)
        self.add_log_text("Current rule: " + single_rule.get_string())

        program_runner = Z3Runner(params=self.params, program=self)
        signal = program_runner.run_single_query(engine_options="")
        if signal == 3:
            return 3

        if signal != 0 or not os.path.exists(self.get_single_query_result_path()):
            print(colored("Signal = " + str(signal), "red", attrs=["bold"]))
            print(colored("SOMETHING WENT WRONG. Check it out please", "red", attrs=["bold"]))            
            self.add_log_text("XXXXX SOMETHING WENT WRONG. PLEASE CHECK IT OUT. XXXXXX")
            self.dump_program_log_file()
            return signal

        # if len(read_file(self.get_single_query_result_path())) == 0:
        #     return 3

        return 0

    def run_whole_program(self):
        program_runner = Z3Runner(params=self.params, program=self)
        signal = program_runner.run_original(engine_options="")
        if signal == 3:
            return 3

        if signal != 0 or not os.path.exists(self.get_output_result_file_path()):
            print(colored("Signal = " + str(signal), "red", attrs=["bold"]))
            print(colored("SOMETHING WENT WRONG. Check it out please", "red", attrs=["bold"]))            
            self.add_log_text("XXXXX SOMETHING WENT WRONG. PLEASE CHECK IT OUT. XXXXXX")
            self.dump_program_log_file()
            self.pretty_print_program()
            return signal

        return 0
