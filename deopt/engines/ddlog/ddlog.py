from deopt.datalog.base_program import BaseProgram
from deopt.engines.ddlog.ddlog_rule import DDlogRule
from deopt.engines.ddlog.ddlog_fact import DDlogFact
from deopt.engines.ddlog.ddlog_type import DDlogType
from deopt.runner.ddlog_runner import DDlogRunner
from copy import deepcopy
from termcolor import colored
import os
from deopt.utils.file_operations import create_file, read_file

class DDlogProgram(BaseProgram):
    def get_allowed_types(self):
        # self.allowed_types = deepcopy(self.params["ddlog_types"])
        for t in self.params["ddlog_types"]:
            d_t = DDlogType(name=t, parent_type=None, relation=None)
            self.allowed_types.append(d_t)
        for t in self.allowed_types:
            if t.get_declation() != "":
                self.type_declarations.append(t.get_declation())
    
    def generate_single_rule(self):
        rule = DDlogRule(verbose=self.verbose, randomness=self.randomness, params=self.params)
        edb_relations = [fact.name for fact in self.facts]
        rule.generate_random_rule(allowed_types=self.allowed_types, available_relations=self.all_relations, edb_relations=edb_relations)

        rule.add_more_element_to_rule(available_relations=self.all_relations, all_facts_raw_data_entries=self.all_relations_raw_data_entries)
        rule.update_string()
        return rule
            

    def generate_facts(self):
        for i in range(self.number_of_facts):
            fact_table = DDlogFact(randomness=self.randomness, params=self.params, allowed_types=self.allowed_types)
            while self.is_duplicate_relation(fact_table.name):
                fact_table = DDlogFact(randomness=self.randomness, params=self.params, allowed_types=self.allowed_types)
            self.declarations.append(fact_table.get_decleration())
            self.facts.append(fact_table)
            self.all_relations.append(fact_table.get_fact_as_a_relation())
            self.all_relations_raw_data_entries[fact_table.name] = deepcopy(fact_table.raw_data_entries)

    def get_real_value(self, item, type_list):
        item = item.strip()
        item = item.split('\t')
        res = list()
        for idx, value in enumerate(item):
            if value == 'NaN':
                res.append('NaN')
            elif type_list[idx].get_ancestor_type_name() == "bigint" or type_list[idx].get_ancestor_type_name().startswith("signed"):
                res.append(int(value))
            elif type_list[idx].get_ancestor_type_name() == "string":
                res.append(str(value))
            elif type_list[idx].get_ancestor_type_name().startswith("bit"):
                res.append(int(value))
            elif type_list[idx].get_ancestor_type_name() == "float" or type_list[idx].get_ancestor_type_name() == "double":
                res.append(float(value))
            elif type_list[idx].get_ancestor_type_name() == "bool":
                res.append(str(value))
            else:
                print("different shape of result!")
                exit(0)
        return res


    def pretty_print_program(self):
        for decl in self.type_declarations: print(colored(decl, "green", attrs=["bold"]))
        print("\n\n")        
        for decl in self.declarations[:-1]: print(colored(decl, "red", attrs=["bold"]))
        print(colored("output " + self.output_rule.get_declaration(), "green", attrs=["bold"]))

        # facts (only when in_file_facts is true)
        if self.params["in_file_facts"]:
            for fact in self.facts:
                for row in fact.get_fact_data(): print(colored(row, "yellow", attrs=["bold"]))
            print("")

        print("")
        for rule in self.all_rules:
            rule_string = deepcopy(rule.get_string())
            if rule_string.find("simple rule") != -1:
                rule_string = rule_string.replace("//simple rule", "")
                print(colored(rule_string, "white", attrs=["bold"]), end="")
                print(colored("//simple rule", "green", attrs=["bold"]))
            # Transformed rule
            if rule_string.find("transformed rule") != -1:
                print(colored(rule_string, "yellow", attrs=["bold"]))
        print("")



    def create_whole_program_string(self):
        # declarations
        self.program_string = ""

        # type declarations
        for t_d in self.type_declarations:
            self.program_string += t_d + "\n"
        self.program_string += "\n"

        # declarations
        for decl in self.declarations:
            if not "input relation" in decl:
                self.program_string += "output " + decl + "\n"
            else:
                self.program_string += decl + "\n"

        if not self.output_rule.recursive_rule:
            self.program_string += "output " + self.output_rule.get_declaration() 
        self.program_string += "\n\n"
        # rule definitions
        self.program_string += "\n\n"
        for rule in self.all_rules:
            self.program_string += rule.get_string() + "\n"
        self.program_string += self.output_rule.get_string() + "\n\n"
        


    def export_whole_program_string(self):
        def export_facts():
            fact_file_string = "start;\n\n"
            for fact in self.facts:
                for row in fact.get_fact_data():
                    fact_file_string += row + "\n"
            fact_file_string += "commit;\ndump " + self.output_rule.get_head().get_name() + ";\n" 
            create_file(fact_file_string, os.path.join(self.program_path, "facts.dat"))

        self.create_whole_program_string()
        self.program_file_path = os.path.join(self.program_path, "orig_rules.dl")
        self.logs.set_log_file_name("orig.log")
        self.logs.set_log_file_path(self.program_path)
        if not os.path.exists(self.program_path):
            os.mkdir(self.program_path)
        create_file(self.program_string, self.program_file_path)
        export_facts()


    def create_single_query_string(self, single_rule):
        """
            DDlog program structure:
                declarations
                output declaration
                rule definitions
        """
        self.single_query_string = ""
        print("current rule: " + single_rule.get_string())

        # type declarations
        for t_d in self.type_declarations:
            self.single_query_string += t_d + "\n"
        self.single_query_string += "\n"

        # declarations
        self.single_query_string += "\n".join(single_rule.generate_decleration_for_single_query())
        self.single_query_string += "\n"

        if not single_rule.head.name in self.single_query_string:
            self.single_query_string += "output " + single_rule.head.generate_decleration()[6:] + "\n"

        # rule definitions
        self.single_query_string += "\n\n"
        self.single_query_string += single_rule.get_string() + "\n\n"


        for subgoal in single_rule.subgoals:
            for row in subgoal.get_fact_data(self.all_relations_raw_data_entries):
                self.single_query_string += "// " + row + "\n"
        

    def export_single_query_string(self, single_rule):
        """
            Export single query program string
        """
        def export_facts():
            fact_file_string = "start;\n\n"
            subgoal_set = []
            for subgoal in single_rule.subgoals:
                if subgoal.name not in subgoal_set:
                    subgoal_set.append(subgoal.name)
                else:
                    continue
                for row in subgoal.get_fact_data(self.all_relations_raw_data_entries):
                    fact_file_string += row + "\n"
            fact_file_string += "commit;\ndump " + single_rule.get_head().get_name() + ";\n" 
            create_file(fact_file_string, os.path.join(self.program_path, "facts.dat"))

        self.create_single_query_string(single_rule)

        self.single_query_file_path = os.path.join(self.program_path, "single_query.dl")
        self.logs.set_log_file_name("orig.log")
        self.logs.set_log_file_path(self.program_path)
        if not os.path.exists(self.program_path):
            os.mkdir(self.program_path)
        create_file(self.single_query_string, self.single_query_file_path)
        export_facts()

    def run_single_query_program(self, single_rule):
        self.export_single_query_string(single_rule)
        if len(self.single_query_string) < 10000:
            self.add_log_text("Current rule: " + self.single_query_string)

        program_runner = DDlogRunner(params=self.params, program=self)
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
        program_runner = DDlogRunner(params=self.params, program=self)
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


    # def save_the_last_rule(self):
    #     if self.output_rule.recursive_rule:
    #         pass
    #     else:
    #         self.declarations.append(self.output_rule.get_declaration())
    #         self.all_relations.append(self.output_rule.get_head())
    #         self.all_relations_raw_data_entries[self.output_rule.head.get_name()]= deepcopy(read_file(self.get_output_result_file_path()))
    #         self.all_rules_raw_data_entries.append(read_file(self.get_output_result_file_path()))
    #     self.all_rules.append(deepcopy(self.output_rule))