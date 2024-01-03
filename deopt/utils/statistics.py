"""
    Statistics class for progress reporting    
    Numbers we keep track of: 
        - Total number of program
        - Total number of reference 
        - Timeouts
        - Number of segfaults
        - Assertion failures
        - Unknown errors
        - Uninteresting errors
        - Inline errors
        - Soundness errors
"""
import os
import json
from termcolor import colored
from copy import deepcopy

class Statistics(object):
    def __init__(self, test_case_ID, core_dir):
        self.stats_file_path = os.path.join(core_dir, "stats.json") # should it be a json format

        # Initialize 
        self.stats_data = dict()

        self.stats_data["test_case_ID"] = test_case_ID #
        self.stats_data["total_rules"] = 0 #
        self.stats_data["total_bugs"] = 0

        self.stats_data["begin_time"] = 0 #
        self.stats_data["end_time"] = 0 #

        self.stats_data["total_time_for_reference_program"] = 0 #
        self.stats_data["total_time_for_optimized_program"] = 0 #

        self.stats_data["number_of_times_for_evaluating_reference_program"] = 0 #
        self.stats_data["number_of_times_for_evaluating_optimized_program"] = 0 #

        self.stats_data["number_of_times_for_evaluating_ref_prog_in_rq"] = 0 
        self.stats_data["total_time_for_reference_program_of_rq"] = 0

        self.stats_data["total_time_for_graph_stratify"] = 0 

        self.stats_data["number_of_attempts_for_new_rules"] = 0 #

        self.stats_data["recursive_queries_length"] = [] #

        self.stats_data["number_of_optimized_prog_with_empty_result"] = 0 #
        self.stats_data["number_of_ref_prog_with_empty_result"] = 0 #
        self.stats_data["number_of_ref_prog_facts_size_bigger_than_threshold"] = 0 #
        self.stats_data["is_final_result_of_opt_prog_empty"] = 0 #
        self.stats_data["is_final_result_of_opt_prog_nonempty"] = 0 #
        
        self.stats_data["total_optimized_timeouts"] = 0 #
        self.stats_data["total_reference_timeouts"] = 0 #
        
        self.stats_data["total_optimized_errors"] = 0 #
        self.stats_data["total_reference_errors"] = 0 #

        self.stats_data["total_optimized_assertion_failures"] = 0 #
        self.stats_data["total_reference_assertion_failures"] = 0 #

        self.stats_data["is_final_program_fail"] = 0
        self.stats_data["is_final_program_normal"] = 0

        self.stats_data["iterations_for_recursive_query_exceed_threshold"] = 0
        self.stats_data["find_logic_bug"] = 0

    def dump_data(self):
        old_result = []
        if os.path.exists(self.stats_file_path):
            with open(self.stats_file_path, "r", encoding="utf-8") as infile:
                old_result = json.load(infile)
        old_result.append(self.stats_data)
        with open(self.stats_file_path, 'w', encoding="utf-8") as outfile:
            json.dump(old_result, outfile, sort_keys=False)

    def get_data_points(self):
        return self.stats_data.keys()

    # Increment methods ---------------------------------------
    def set_total_rules(self, n):
        self.stats_data["total_rules"] = n
    def add_total_bugs(self):
        self.stats_data["total_bugs"] += 1
    def set_begin_time(self, begin_time):
        self.stats_data["begin_time"] = begin_time
    def set_end_time(self, end_time):
        self.stats_data["end_time"] = end_time
    def add_total_time_for_reference_program(self, single_time):
        self.stats_data["total_time_for_reference_program"] += single_time
    def add_total_time_for_optimized_program(self, single_time):
        self.stats_data["total_time_for_optimized_program"] += single_time
    def add_number_of_times_for_evaluating_reference_program(self):
        self.stats_data["number_of_times_for_evaluating_reference_program"] += 1
    def add_number_of_times_for_evaluating_optimized_program(self):
        self.stats_data["number_of_times_for_evaluating_optimized_program"] += 1
    def add_number_of_attempts_for_new_rules(self):
        self.stats_data["number_of_attempts_for_new_rules"] += 1
    def set_recursive_queries_length(self, length_list):
        self.stats_data["recursive_queries_length"] = deepcopy(length_list)
    def add_number_of_optimized_prog_with_empty_result(self):
        self.stats_data["number_of_optimized_prog_with_empty_result"] += 1
    def add_number_of_ref_prog_with_empty_result(self):
        self.stats_data["number_of_ref_prog_with_empty_result"] += 1
    def add_number_of_ref_prog_facts_size_bigger_than_threshold(self):
        self.stats_data["number_of_ref_prog_facts_size_bigger_than_threshold"] += 1
    def set_final_result_of_opt_prog_empty(self, label):
        if label:
            self.stats_data["is_final_result_of_opt_prog_empty"] = 1
            self.stats_data["is_final_result_of_opt_prog_nonempty"] = 0
        else:
            self.stats_data["is_final_result_of_opt_prog_empty"] = 0
            self.stats_data["is_final_result_of_opt_prog_nonempty"] = 1
    def add_total_optimized_timeouts(self):
        self.stats_data["total_optimized_timeouts"] += 1
    def add_total_reference_timeouts(self):
        self.stats_data["total_reference_timeouts"] += 1
    def add_total_optimized_errors(self):
        self.stats_data["total_optimized_errors"] += 1
    def add_total_reference_errors(self):
        self.stats_data["total_reference_errors"] += 1
    def add_total_optimized_assertion_failures(self):
        self.stats_data["total_optimized_assertion_failures"] += 1
    def add_total_reference_assertion_failures(self):
        self.stats_data["total_reference_assertion_failures"] += 1 
    def add_number_of_times_for_evaluating_ref_prog_in_rq(self):
        self.stats_data["number_of_times_for_evaluating_ref_prog_in_rq"] += 1
    def add_total_time_for_reference_program_of_rq(self, rq_time):
        self.stats_data["total_time_for_reference_program_of_rq"] += rq_time
    def add_total_time_for_graph_stratify(self, st_time):
        self.stats_data["total_time_for_graph_stratify"] += st_time

    def add_final_program_state(self, state):
        if state:
            self.stats_data["is_final_program_normal"] = 1
            self.stats_data["is_final_program_fail"] = 0
        else:
            self.stats_data["is_final_program_fail"] = 1
            self.stats_data["is_final_program_normal"] = 0

    def add_iterations_for_recursive_query_exceed_threshold(self):
        self.stats_data["iterations_for_recursive_query_exceed_threshold"] += 1

    def add_find_logic_bug(self):
        self.stats_data["find_logic_bug"] += 1
        
    def print_stats(self):
        with open(self.stats_file_path) as f:
            data = json.load(f)
            json_dump = json.dumps(data, indent=4)
        print(json_dump)