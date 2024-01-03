from deopt.utils.file_operations import create_file, read_file
from abc import ABC, abstractmethod
from termcolor import colored
import copy
from deopt.utils.logging import Logging
from copy import deepcopy
from queue import Queue
from deopt.datalog.dependence_graph import DependenceGraph
from collections import defaultdict
import os
import time
from deopt.utils.statistics import Statistics

class BaseProgram(object):

    def __init__(self, params, verbose, randomness, program_number, program_path):
        self.params = params
        self.verbose = verbose
        self.randomness = randomness
        self.string = ""
        self.seed_program_file = None
        self.logs = Logging()
        # Program things
        self.allowed_types = list()         # Type: string
        self.facts = list()                 # A list of fact objects
        self.other_things = list()          # Type: string
        self.type_declarations = list()     # Type : string
        self.declarations = list()
        self.inputs = list()                # Type: string
        self.all_rules = list()
        self.all_relations = list()         # Type: Subgoal() list
        self.all_rules_raw_data_entries = list()
        self.all_relations_raw_data_entries = defaultdict(list)
        self.output_rule = None             # Type: rule
        self.program_string = ""
        self.single_query_string = ""
        self.output_result_path = ""        # Path
        self.single_query_result_path = ""
        self.cycle_breakers = list()        # Type: Subgoal() list
        # Parameters
        self.number_of_facts = self.randomness.get_random_integer(1, params["max_number_of_facts"])
        
        # other stuff
        self.program_path = program_path
        self.program_number = program_number
        self.program_file_path = None
        self.single_query_file_path = None

        self.dependence_graph = DependenceGraph()
        self.temp_dependence_graph = None

        # Get allowed types
        self.get_allowed_types()

        # Some initial logs
        self.logs.add_log_text("\tSEED:" + str(self.randomness.get_initial_random_seed()))

        # Statistics
        self.statis = Statistics(program_number, os.path.dirname(program_path))
        self.statis.set_begin_time(time.time())

        self.logs.add_log_text("\n ================= ")
        self.logs.add_log_text("  File Generation ")
        self.logs.add_log_text(" ================= ")

    def differential_testing(self):
        # this only for the evaluation of random test case generation
        if self.params["execution_mode"] == "random":
            return self.run_random_test_case()


        # First, generate the fact
        self.logs.add_log_text("\tGenerating facts...")
        self.generate_facts()

        # Second, generate the rules
        whole_program_fail_number = 0
        while len(self.all_rules) < self.params["max_number_rules"] and (whole_program_fail_number < self.params["max_number_of_attempts_for_rule_generation"] or self.params["max_number_of_attempts_for_rule_generation"] == -1):
            self.logs.add_log_text("\tGenerating rule ... " + str(len(self.all_rules) + 1))
            reference_program_signal = -1
            attempts = 0
            temp_all_relations_raw_data_entries = deepcopy(self.all_relations_raw_data_entries)
            temp_all_rules_raw_data_entries = deepcopy(self.all_rules_raw_data_entries)
            while reference_program_signal != 0:
                self.logs.add_log_text("\tGenerating rule at attemp_" + str(attempts))
                if attempts >= self.params["max_number_of_attempts_for_rule_generation"] and self.params["max_number_of_attempts_for_rule_generation"] != -1:
                    return True
                last_rule = self.generate_single_rule()
                self.statis.add_number_of_attempts_for_new_rules()
                self.update_temp_dependence_graph(last_rule)
                if last_rule.recursive_rule and self.temp_dependence_graph.is_node_in_circle(len(self.all_rules)):
                    last_rule.add_queryplan()    # only for souffle
                self.output_rule = copy.deepcopy(last_rule)
                reference_program_signal = self.run_reference_program()
                if self.params["execution_mode"] != "evaluation":
                    if reference_program_signal == 1 or reference_program_signal == 2:
                        return False
                attempts = attempts + 1
            opt_prog_start_time = time.time()
            self.export_whole_program_string()
            whole_program_signal = self.run_whole_program()
            opt_prog_end_time = time.time()
            opt_prog_duration_time = opt_prog_end_time - opt_prog_start_time
            self.statis.add_total_time_for_optimized_program(opt_prog_duration_time)
            self.statis.add_number_of_times_for_evaluating_optimized_program()

            self.statis.add_final_program_state(whole_program_signal == 0)
            if whole_program_signal == 3 or (self.params["execution_mode"] == "evaluation" and whole_program_signal != 0):
                # we don't care about this and ignore this rule
                # in evaluation, we ignore all errors
                whole_program_fail_number += 1
                self.all_relations_raw_data_entries = deepcopy(temp_all_relations_raw_data_entries)
                self.all_rules_raw_data_entries = deepcopy(temp_all_rules_raw_data_entries)
                continue
            whole_program_fail_number = 0
            if self.params["execution_mode"] != "evaluation" and whole_program_signal != 0:
                # there maybe an error in engines
                return False
            if self.compare_results_for_two_program(self.output_rule.head.get_types()):
                whole_program_result = read_file(self.get_output_result_file_path())
                if len(whole_program_result) == 0:
                    self.statis.add_number_of_optimized_prog_with_empty_result()
                self.statis.set_final_result_of_opt_prog_empty(len(whole_program_result) == 0)
                # save the last rule
                self.save_the_last_rule()
                continue
            else:
                if self.params["execution_mode"] != "evaluation":
                    print(" " + colored("SOUNDNESS BUG FOUND", "white", "on_red", attrs=["bold"]))
                    if self.output_rule.recursive_rule:
                        print(str(self.all_relations_raw_data_entries[self.output_rule.head.name]))
                        self.add_log_text("recursive query ref res: " + str(self.all_relations_raw_data_entries[self.output_rule.head.name]))
                    else:
                        print(str(read_file(self.get_single_query_result_path())))
                        self.add_log_text("single query ref res: " + str(read_file(self.get_single_query_result_path())))
                    print(str(read_file(self.get_output_result_file_path())))
                    self.add_log_text("opt res: " + str(read_file(self.get_output_result_file_path())))
                    return False
                else:
                    self.all_relations_raw_data_entries = deepcopy(temp_all_relations_raw_data_entries)
                    self.all_rules_raw_data_entries = deepcopy(temp_all_rules_raw_data_entries)
                    self.statis.add_find_logic_bug()
                    continue
                
        return True


    def run_reference_program(self):
        if self.output_rule.recursive_rule:
            # The core algorithm to compute the fix point
            temp_all_relations_raw_data_entries = deepcopy(self.all_relations_raw_data_entries)     # used to recovery the data
            temp_all_rules_raw_data_entries = deepcopy(self.all_rules_raw_data_entries)
            temp_all_rules = deepcopy(self.all_rules)
            temp_all_rules.append(deepcopy(self.output_rule))
            self.all_rules_raw_data_entries.append([])     # for the last rule
            stratify_begin_time = time.time()
            layered_execution_order, cycle_node_map, all_influenced_node = self.temp_dependence_graph.get_precedence_graph_of_query_node(len(temp_all_rules) - 1)
            stratify_end_time = time.time()
            self.statis.add_total_time_for_graph_stratify(stratify_end_time - stratify_begin_time)
            self.add_log_text("layers: " + str(layered_execution_order))
            self.add_log_text("cycle_node_map: " + str(cycle_node_map))
            self.dump_program_log_file()
            self.refresh_all_relations_raw_data_entries(all_influenced_node)
            for layer_number, execution_nodes in enumerate(layered_execution_order):
                for current_node_index in execution_nodes:
                    if current_node_index < self.temp_dependence_graph.cycle_node_base_number:
                        current_rule = temp_all_rules[current_node_index]

                        ref_prog_start_time = time.time()
                        signal = self.run_single_query_program(current_rule)
                        ref_prog_end_time = time.time()
                        ref_prog_duration_time = ref_prog_end_time - ref_prog_start_time
                        self.statis.add_total_time_for_reference_program(ref_prog_duration_time)
                        self.statis.add_number_of_times_for_evaluating_reference_program()

                        if signal != 0:
                            self.logs.add_log_text("meet error in single query execution")
                            self.all_relations_raw_data_entries = deepcopy(temp_all_relations_raw_data_entries)
                            self.all_rules_raw_data_entries = deepcopy(temp_all_rules_raw_data_entries)
                            return signal
                        else:
                            if len(read_file(self.get_single_query_result_path())) == 0:
                                self.statis.add_number_of_ref_prog_with_empty_result()
                                if self.randomness.get_random_integer(0, 99) >= self.params["probability_of_empty_result_rule"]:
                                    self.logs.add_log_text("empty result")
                                    self.all_relations_raw_data_entries = deepcopy(temp_all_relations_raw_data_entries)
                                    self.all_rules_raw_data_entries = deepcopy(temp_all_rules_raw_data_entries)
                                    return 3
                            if len(read_file(self.get_single_query_result_path())) > self.params["max_size_of_facts"]:
                                self.statis.add_number_of_ref_prog_facts_size_bigger_than_threshold()
                                self.all_relations_raw_data_entries = deepcopy(temp_all_relations_raw_data_entries)
                                self.all_rules_raw_data_entries = deepcopy(temp_all_rules_raw_data_entries)
                                return 3
                        current_result = [i.strip() for i in read_file(self.get_single_query_result_path())]
                        self.all_rules_raw_data_entries[current_node_index] = deepcopy(current_result)
                        ignore_list = self.temp_dependence_graph.get_ignored_facts_list(layered_execution_order, layer_number, cycle_node_map)
                        self.update_all_relations_raw_data_entries(current_rule.head.name, temp_all_rules, ignore_list)
                    else:  # recursive query
                        recursive_query_index_list = self.temp_dependence_graph.get_real_value_of_node(cycle_node_map, current_node_index)
                        if self.temp_dependence_graph.contain_negative_edge(recursive_query_index_list):  # need well founded semantic
                            self.logs.add_log_text("recursive query with negation!")
                            self.all_relations_raw_data_entries = deepcopy(temp_all_relations_raw_data_entries)
                            self.all_rules_raw_data_entries = deepcopy(temp_all_rules_raw_data_entries)
                            return 3
                        else:
                            is_not_stable = True
                            iterations_for_recursive_query = 0 # one execute one time
                            iteration_times = 0 # for the first node in first iteration, maybe equals to empty, one loop one time
                            while is_not_stable:
                                is_not_stable = False
                                for recursive_node_index in recursive_query_index_list:
                                    if iterations_for_recursive_query == self.params["max_iterations_for_recursive_query"]:
                                        self.add_log_text("too much iterations in recursive query.")
                                        self.all_relations_raw_data_entries = deepcopy(temp_all_relations_raw_data_entries)
                                        self.all_rules_raw_data_entries = deepcopy(temp_all_rules_raw_data_entries)
                                        self.statis.add_iterations_for_recursive_query_exceed_threshold()
                                        return 3
                                    iterations_for_recursive_query = iterations_for_recursive_query + 1
                                    current_rule = temp_all_rules[recursive_node_index]

                                    ref_prog_start_time = time.time()
                                    signal = self.run_single_query_program(current_rule)
                                    ref_prog_end_time = time.time()
                                    ref_prog_duration_time = ref_prog_end_time - ref_prog_start_time
                                    self.statis.add_total_time_for_reference_program(ref_prog_duration_time)
                                    self.statis.add_total_time_for_reference_program_of_rq(ref_prog_duration_time)
                                    self.statis.add_number_of_times_for_evaluating_reference_program()
                                    self.statis.add_number_of_times_for_evaluating_ref_prog_in_rq()

                                    if signal != 0:
                                        self.logs.add_log_text("meet error in single query execution")
                                        self.all_relations_raw_data_entries = deepcopy(temp_all_relations_raw_data_entries)
                                        self.all_rules_raw_data_entries = deepcopy(temp_all_rules_raw_data_entries)
                                        return signal
                                    else:
                                        if len(read_file(self.get_single_query_result_path())) > self.params["max_size_of_facts"]:
                                            self.statis.add_number_of_ref_prog_facts_size_bigger_than_threshold()
                                            self.all_relations_raw_data_entries = deepcopy(temp_all_relations_raw_data_entries)
                                            self.all_rules_raw_data_entries = deepcopy(temp_all_rules_raw_data_entries)
                                            return 3
                                    current_result = [i.strip() for i in read_file(self.get_single_query_result_path())]
                                    old_result = self.all_rules_raw_data_entries[recursive_node_index]
                                    if not self.compare_results(old_result, current_result, current_rule.head.get_types()):
                                        is_not_stable = True
                                        self.all_rules_raw_data_entries[recursive_node_index] = deepcopy(current_result)
                                    if len(current_result) == 0 and iteration_times == 0 and is_not_stable == False:
                                        is_not_stable = True
                                    ignore_list = self.temp_dependence_graph.get_ignored_facts_list(layered_execution_order, layer_number, cycle_node_map)
                                    self.update_all_relations_raw_data_entries(current_rule.head.name, temp_all_rules, ignore_list)
                                iteration_times = iteration_times + 1
            return 0
        else:
            ref_prog_start_time = time.time()
            signal = self.run_single_query_program(self.output_rule)
            ref_prog_end_time = time.time()
            ref_prog_duration_time = ref_prog_end_time - ref_prog_start_time
            self.statis.add_total_time_for_reference_program(ref_prog_duration_time)
            self.statis.add_number_of_times_for_evaluating_reference_program()
            
            if signal == 0 and len(read_file(self.get_single_query_result_path())) == 0 and self.randomness.get_random_integer(0, 99) >= self.params["probability_of_empty_result_rule"]:
                self.statis.add_number_of_ref_prog_with_empty_result()
                return 3
            elif signal == 0 and len(read_file(self.get_single_query_result_path())) > self.params["max_size_of_facts"]:
                self.statis.add_number_of_ref_prog_facts_size_bigger_than_threshold()
                return 3
            else:
                return signal
        
    def run_random_test_case(self):
        self.generate_facts()
        while len(self.all_rules) < self.params["max_number_rules"]:
            self.output_rule = self.generate_single_rule()
            if not self.output_rule.recursive_rule:
                self.declarations.append(self.output_rule.get_declaration())
                self.all_relations.append(self.output_rule.get_head())
            self.all_rules.append(deepcopy(self.output_rule))
            self.update_dependence_graph_for_random_test_case(self.output_rule)
        self.all_rules = self.all_rules[:-1]
        if not self.output_rule.recursive_rule:
            self.declarations = self.declarations[:-1]
        # run optimized program first
        opt_prog_start_time = time.time()
        self.export_whole_program_string()
        whole_program_signal = self.run_whole_program()
        opt_prog_end_time = time.time()
        opt_prog_duration_time = opt_prog_end_time - opt_prog_start_time
        self.statis.add_total_time_for_optimized_program(opt_prog_duration_time)
        self.statis.add_number_of_times_for_evaluating_optimized_program()
        self.statis.add_final_program_state(whole_program_signal == 0)

        # save the rule
        self.all_rules.append(deepcopy(self.output_rule))
        self.declarations.append(self.output_rule.get_declaration())

        if whole_program_signal == 0:
            whole_program_result = read_file(self.get_output_result_file_path())
            if len(whole_program_result) == 0:
                self.statis.add_number_of_optimized_prog_with_empty_result()
            self.statis.set_final_result_of_opt_prog_empty(len(whole_program_result) == 0)
        else:
            return
        
        # run reference programs second
        stratify_begin_time = time.time()
        layered_execution_order, cycle_node_map = self.dependence_graph.get_precedence_graph_of_whole_graph()
        stratify_end_time = time.time()
        self.statis.add_total_time_for_graph_stratify(stratify_end_time - stratify_begin_time)
        for idx, rule in enumerate(self.all_rules):
            self.all_rules_raw_data_entries.append([])
        for layer_number, execution_nodes in enumerate(layered_execution_order):
            for current_node_index in execution_nodes:
                if current_node_index < self.dependence_graph.cycle_node_base_number:
                    current_rule = self.all_rules[current_node_index]

                    ref_prog_start_time = time.time()
                    signal = self.run_single_query_program(current_rule)
                    ref_prog_end_time = time.time()
                    ref_prog_duration_time = ref_prog_end_time - ref_prog_start_time
                    self.statis.add_total_time_for_reference_program(ref_prog_duration_time)
                    self.statis.add_number_of_times_for_evaluating_reference_program()

                    if signal != 0:
                        return signal

                    current_result = [i.strip() for i in read_file(self.get_single_query_result_path())]
                    self.all_rules_raw_data_entries[current_node_index] = deepcopy(current_result)
                    ignore_list = self.dependence_graph.get_ignored_facts_list(layered_execution_order, layer_number, cycle_node_map)
                    self.update_all_relations_raw_data_entries(current_rule.head.name, self.all_rules, ignore_list)
                else:  # recursive query
                    recursive_query_index_list = self.dependence_graph.get_real_value_of_node(cycle_node_map, current_node_index)
                    if self.dependence_graph.contain_negative_edge(recursive_query_index_list):  # need well founded semantic
                        return 3
                    else:
                        is_not_stable = True
                        iterations_for_recursive_query = 0 # one execute one time
                        iteration_times = 0 # for the first node in first iteration, maybe equals to empty, one loop one time
                        while is_not_stable:
                            is_not_stable = False
                            for recursive_node_index in recursive_query_index_list:
                                if iterations_for_recursive_query == self.params["max_iterations_for_recursive_query"]:
                                    self.statis.add_iterations_for_recursive_query_exceed_threshold()
                                    return 3
                                iterations_for_recursive_query = iterations_for_recursive_query + 1
                                current_rule = self.all_rules[recursive_node_index]

                                ref_prog_start_time = time.time()
                                signal = self.run_single_query_program(current_rule)
                                ref_prog_end_time = time.time()
                                ref_prog_duration_time = ref_prog_end_time - ref_prog_start_time
                                self.statis.add_total_time_for_reference_program(ref_prog_duration_time)
                                self.statis.add_total_time_for_reference_program_of_rq(ref_prog_duration_time)
                                self.statis.add_number_of_times_for_evaluating_reference_program()
                                self.statis.add_number_of_times_for_evaluating_ref_prog_in_rq()

                                if signal != 0:
                                    return signal
                                current_result = [i.strip() for i in read_file(self.get_single_query_result_path())]
                                old_result = self.all_rules_raw_data_entries[recursive_node_index]
                                if not self.compare_results(old_result, current_result, current_rule.head.get_types()):
                                    is_not_stable = True
                                    self.all_rules_raw_data_entries[recursive_node_index] = deepcopy(current_result)
                                if len(current_result) == 0 and iteration_times == 0 and is_not_stable == False:
                                    is_not_stable = True
                                ignore_list = self.dependence_graph.get_ignored_facts_list(layered_execution_order, layer_number, cycle_node_map)
                                self.update_all_relations_raw_data_entries(current_rule.head.name, self.all_rules, ignore_list)
                            iteration_times = iteration_times + 1
        if not self.compare_results(read_file(self.get_output_result_file_path()), self.all_relations_raw_data_entries[self.output_rule.head.name], self.output_rule.head.get_types()):
            self.statis.add_find_logic_bug()
        return True

    def update_dependence_graph_for_random_test_case(self, new_rule):
        new_rule_idx = len(self.all_rules) - 1
        new_rule_head_name = new_rule.head.get_name()
        self.dependence_graph.add_node(new_rule_idx)
        if new_rule_idx == 0:
            return
        for idx, rule in enumerate(self.all_rules[:-1]):
            rule_head_name = rule.head.get_name()
            if rule_head_name in new_rule.dependent_subgoals:
                self.dependence_graph.add_edge(idx, new_rule_idx)
            if rule_head_name in new_rule.negative_dependent_subgoals:
                self.dependence_graph.add_negative_edge(idx, new_rule_idx)

            if new_rule_head_name in rule.dependent_subgoals:
                self.dependence_graph.add_edge(new_rule_idx, idx)
            if new_rule_head_name == rule.negative_dependent_subgoals:
                self.dependence_graph.add_edge(new_rule_idx, idx)


    def update_temp_dependence_graph(self, new_rule):
        self.temp_dependence_graph = deepcopy(self.dependence_graph)
        new_rule_idx = len(self.all_rules)
        new_rule_head_name = new_rule.head.get_name()
        self.temp_dependence_graph.add_node(new_rule_idx)
        for idx, rule in enumerate(self.all_rules):
            rule_head_name = rule.head.get_name()
            if rule_head_name in new_rule.dependent_subgoals:
                self.temp_dependence_graph.add_edge(idx, new_rule_idx)
            if rule_head_name in new_rule.negative_dependent_subgoals:
                self.temp_dependence_graph.add_negative_edge(idx, new_rule_idx)

            if new_rule_head_name in rule.dependent_subgoals:
                self.temp_dependence_graph.add_edge(new_rule_idx, idx)
            if new_rule_head_name == rule.negative_dependent_subgoals:
                self.temp_dependence_graph.add_edge(new_rule_idx, idx)

    def enrich_program(self):
        # Step 2 : Generate facts
        self.logs.add_log_text("\tGenerating facts...")
        self.generate_facts()
        # Step 3 : Generate some more complex program elements.
        # Generate non-cyclic rules. These are the rules that are not used in the body of complex rules
        self.logs.add_log_text("\tGenerating some more complex program elements...")
        self.generate_cycle_breaker_rules()
        # self.generate_mixed_rules()
        self.generate_complex_rules()

        # Generate Simple rules
        # Both the gen mode and nogen mode, both have program generation phase
        self.logs.add_log_text("\tGenerating simple rules...")
        self.generate_simple_rules()
        # Step 4 : Select an output rule
        self.output_rule = copy.deepcopy(self.all_rules[-1])
        self.logs.add_log_text("\tOutput rule: " + self.output_rule.get_head().get_string())
        # Output rule cannot be inlined. 
        for i, decl_string in enumerate(self.declarations):
            if decl_string.find(self.output_rule.get_head().get_name()) != -1:
                self.declarations[i] = decl_string.replace(" inline", "")

    @abstractmethod
    def get_allowed_types(self):
        pass

    @abstractmethod
    def generate_single_rule(self):
        pass

    @abstractmethod
    def generate_facts(self):
        pass

    @abstractmethod
    def create_whole_program_string(self):
        pass

    @abstractmethod
    def pretty_print_program(self):
        pass
    
    @abstractmethod
    def export_whole_program_string(self):
        pass

    @abstractmethod
    def create_single_query_string(self):
        pass

    @abstractmethod
    def export_single_query_string(self):
        pass

    @abstractmethod
    def run_whole_program(self):
        pass

    @abstractmethod
    def run_single_query_program(self):
        pass

    def compare_results_for_two_program(self, type_list):
        whole_program_result = read_file(self.get_output_result_file_path())

        if self.output_rule.recursive_rule:
            single_query_result = self.all_relations_raw_data_entries[self.output_rule.head.name]
            return self.compare_results(whole_program_result, single_query_result, type_list)
        else:
            single_query_result = read_file(self.get_single_query_result_path())
            return self.compare_results(whole_program_result, single_query_result, type_list)

    def compare_results(self, whole_program_result, single_query_result, type_list):

        deduplicate_whole_program_result = list()
        for item in whole_program_result:
            item = self.get_real_value(item, type_list)
            # if item not in deduplicate_whole_program_result:
            if not self.is_duplicate(item, deduplicate_whole_program_result):
                deduplicate_whole_program_result.append(deepcopy(item))
        
        deduplicate_single_query_result = list()
        for item in single_query_result:
            item = self.get_real_value(item, type_list)
            # if item not in deduplicate_single_query_result:
            if not self.is_duplicate(item, deduplicate_single_query_result):
                deduplicate_single_query_result.append(deepcopy(item))

        if len(deduplicate_whole_program_result) != len(deduplicate_single_query_result):
            return False
        for item in deduplicate_whole_program_result:
            if not item in deduplicate_single_query_result:
                return False
        return True

    def is_duplicate(self, item, deduplicate_list):
        for deduplicate_item in deduplicate_list:
            is_same = True
            for idx, value in enumerate(item):
                if value != deduplicate_item[idx]:
                    is_same = False
                    break
            if is_same:
                return True
        return False
                

    @abstractmethod
    def get_real_value(self, item, type_list):
        pass


    def get_denpendent_rule(self, rule_list, relation_name, rule_queue, rule_idx_queue):
        for idx, rule in enumerate(rule_list):
            if relation_name in rule.dependent_subgoals:
                rule_queue.put(deepcopy(rule))
                rule_idx_queue.put(idx)

    def update_all_relations_raw_data_entries(self, current_rule_name, all_rules, ignore_list):
        temp_results = []
        for idx, rule in enumerate(all_rules):
            if idx in ignore_list:
                continue
            if rule.head.name == current_rule_name:
                temp_results.extend(deepcopy(self.all_rules_raw_data_entries[idx]))
        for fact in self.facts:
            if fact.name == current_rule_name:
                temp_results.extend(deepcopy(fact.raw_data_entries))
        self.all_relations_raw_data_entries[current_rule_name] = deepcopy(temp_results)


    def refresh_all_relations_raw_data_entries(self, ignored_rules_list):
        self.all_relations_raw_data_entries.clear()
        for fact in self.facts:
            self.all_relations_raw_data_entries[fact.name].extend(deepcopy(fact.raw_data_entries))
        for idx, rule in enumerate(self.all_rules):
            if idx in ignored_rules_list:
                continue
            self.all_relations_raw_data_entries[rule.head.name].extend(deepcopy(self.all_rules_raw_data_entries[idx]))


    def save_the_last_rule(self):
        if self.output_rule.recursive_rule:
            pass
        else:
            self.declarations.append(self.output_rule.get_declaration())
            self.all_relations.append(self.output_rule.get_head())
            self.all_relations_raw_data_entries[self.output_rule.head.get_name()]= deepcopy(read_file(self.get_output_result_file_path()))
            self.all_rules_raw_data_entries.append(deepcopy(read_file(self.get_output_result_file_path())))
        self.all_rules.append(deepcopy(self.output_rule))
        self.dependence_graph = deepcopy(self.temp_dependence_graph)

    @abstractmethod
    def build_the_minimal_test_case(self):
        pass

    def set_output_result_path(self, path):
        self.output_result_path = path
    def set_single_query_result_path(self, path):
        self.single_query_result_path = path
    def get_string(self):
        return self.string
    def get_program_path(self):
        return self.program_path + "/"
    def get_program_file_path(self):
        return self.program_file_path
    def get_single_query_file_path(self):
        return self.single_query_file_path
    def get_output_relation_name(self):
        return self.output_rule.get_head().get_name()
    def get_output_result_file_path(self):
        return self.output_result_path
    def get_single_query_result_path(self):
        return self.single_query_result_path
    def get_output_relation(self):
        # Return : output (Subgoal)
        return self.output_rule.get_head()
    def get_all_relations(self):
        # Return : list of relations in the program.
        return copy.deepcopy(self.all_relations)

    def add_log_text(self, text):
        self.logs.add_log_text(text)

    def dump_program_log_file(self):
        self.logs.dump_log_file(self.params["execution_mode"] != "evaluation")

    def refresh_log_text(self):
        self.logs.refresh_log_text()

    def get_log_file_path(self):
        return self.logs.get_log_file_path()

    def get_type_declarations(self):
        return self.type_declarations

    def update_final_statistic(self):
        self.statis.set_end_time(time.time())
        self.statis.set_total_rules(len(self.all_rules))
        self.statis.set_recursive_queries_length(self.dependence_graph.get_cycles_length())

        # self.statis.dump_data()




    def is_duplicate_type(self, type_name):
        for t in self.allowed_types:
            if t.get_name() == type_name:
                return True
        return False

    def is_duplicate_relation(self, relation_name):
        for rel in self.all_relations:
            if relation_name == rel.name:
                return True
        return False