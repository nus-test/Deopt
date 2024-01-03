import os
import json
import multiprocessing
import time
import shutil
from termcolor import colored
import pyfiglet
import argparse
import logging

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deopt.parsers.argument_parser import MainArgumentParser
from deopt.utils.file_operations import load_parameters, create_temp_directory, create_core_directory
from deopt.utils.randomness import Randomness

from deopt.engines.souffle.souffle import SouffleProgram
from deopt.engines.z3.z3 import Z3Program
from deopt.engines.ddlog.ddlog import DDlogProgram
from deopt.engines.cozodb.cozodb import CozoDBProgram

def run(core, local_seed, wait):
    time.sleep(wait)
    print("\nGlobal Variables:")
    print(colored("\tHOME = ", attrs=["bold"]) + colored(HOME, "cyan", attrs=["bold"]))
    print(colored("\tENGINE = ", attrs=["bold"]) + colored(ENGINE, "cyan", attrs=["bold"]))
    print(colored("\tVERBOSE = ", attrs=["bold"]) + colored(VERBOSE, "cyan", attrs=["bold"]))
    print("\nLocal Variables:")
    print(colored("\n\tcore number = ", attrs=["bold"]) + colored(core, "cyan", attrs=["bold"]))
    print(colored("\tlocal seed = ", attrs=["bold"]) + colored(local_seed, "cyan", attrs=["bold"]))

    core_dir_path = create_core_directory(os.path.join(HOME, "temp"), core) # Create the core directory
    randomness = Randomness(local_seed) # Initialize randomness

    total_statis = {}
    total_statis["test_case_number"] = 0
    total_statis["total_rules"] = 0
    total_statis["number_of_attempts_for_new_rules"] = 0
    total_statis["total_execution_time"] = 0
    total_statis["total_time_for_reference_program"] = 0
    total_statis["total_time_for_optimized_program"] = 0
    total_statis["number_of_times_for_evaluating_reference_program"] = 0
    total_statis["number_of_times_for_evaluating_optimized_program"] = 0
    total_statis["total_time_for_reference_program_of_recursive_query"] = 0
    total_statis["total_time_for_graph_stratify"] = 0
    total_statis["number_of_times_for_evaluating_reference_program_in_recursive_query"] = 0
    total_statis["total_recursive_query_number"] = 0
    total_statis["total_recursive_query_length"] = 0
    total_statis["max_recursive_query_length"] = 0
    total_statis["number_of_optimized_program_with_empty_result"] = 0
    total_statis["number_of_reference_program_with_empty_result"] = 0
    total_statis["number_of_optimized_prog_with_final_empty_result"] = 0
    total_statis["number_of_optimized_prog_with_final_non_empty_result"] = 0
    total_statis["total_number_of_optimized_timeouts"] = 0
    total_statis["total_number_of_reference_timeouts"] = 0
    total_statis["total_optimized_errors"] = 0
    total_statis["total_reference_errors"] = 0
    total_statis["total_optimized_assertion_failures"] = 0
    total_statis["total_reference_assertion_failures"] = 0

    total_statis["average_rule_number"] = 0
    total_statis["average_execution_time_for_test_case"] = 0
    total_statis["average_execution_time_for_reference_program"] = 0
    total_statis["average_execution_time_for_optimized_program"] = 0
    total_statis["average_recursive_query_number"] = 0
    total_statis["average_recursive_query_length"] = 0
    total_statis["probability_of_optimized_program_with_enmpty_result"] = 0
    total_statis["probability_of_final_program_with_empty_result"] = 0

    total_statis["iterations_for_recursive_query_exceed_threshold"] = 0
    total_statis["find_logic_bug"] = 0
    # this two only for random test case generation
    total_statis["total_final_program_fail"] = 0
    total_statis["total_final_program_normal"] = 0


    i = 0
    fuzzing_begin_time = time.time()
    while True:
        program = None
        program_path = os.path.join(core_dir_path, "program_" + str(i))
        if ENGINE == "souffle": 
            program = SouffleProgram(params=PARAMS, verbose=VERBOSE, randomness=randomness, program_number=i, program_path=program_path)
        elif ENGINE == "z3":
            program = Z3Program(params=PARAMS, verbose=VERBOSE, randomness=randomness, program_number=i, program_path=program_path)
        elif ENGINE == "ddlog":
            program = DDlogProgram(params=PARAMS, verbose=VERBOSE, randomness=randomness, program_number=i, program_path=program_path)
        elif ENGINE == "cozodb":
            program = CozoDBProgram(params=PARAMS, verbose=VERBOSE, randomness=randomness, program_number=i, program_path=program_path)
        else:
            print(colored("This engine is currently not supported", "red", attrs=["bold"]))
            exit(0)
        print("----- Prog # " + str(i)+ " ------------")
        # if program.differential_testing():
        signal = program.differential_testing()
        program.update_final_statistic()
        if signal:
            shutil.rmtree(program.get_program_path(), ignore_errors=True)
            pass
        i = i + 1

        # update total statis
        total_statis["test_case_number"] += 1
        total_statis["total_rules"] += program.statis.stats_data["total_rules"]
        total_statis["number_of_attempts_for_new_rules"] += program.statis.stats_data["number_of_attempts_for_new_rules"]
        total_statis["total_execution_time"] += program.statis.stats_data["end_time"] - program.statis.stats_data["begin_time"]
        total_statis["total_time_for_reference_program"] += program.statis.stats_data["total_time_for_reference_program"]
        total_statis["total_time_for_optimized_program"] += program.statis.stats_data["total_time_for_optimized_program"]
        total_statis["number_of_times_for_evaluating_reference_program"] += program.statis.stats_data["number_of_times_for_evaluating_reference_program"]
        total_statis["number_of_times_for_evaluating_optimized_program"] += program.statis.stats_data["number_of_times_for_evaluating_optimized_program"]
        total_statis["total_time_for_reference_program_of_recursive_query"] += program.statis.stats_data["total_time_for_reference_program_of_rq"]
        total_statis["total_time_for_graph_stratify"] += program.statis.stats_data["total_time_for_graph_stratify"]
        total_statis["number_of_times_for_evaluating_reference_program_in_recursive_query"] += program.statis.stats_data["number_of_times_for_evaluating_ref_prog_in_rq"]
        total_statis["total_recursive_query_number"] += len(program.statis.stats_data["recursive_queries_length"])
        total_statis["total_recursive_query_length"] += sum(program.statis.stats_data["recursive_queries_length"])
        if len(program.statis.stats_data["recursive_queries_length"]) > 0:
            total_statis["max_recursive_query_length"] = max(max(program.statis.stats_data["recursive_queries_length"]), total_statis["max_recursive_query_length"])
        total_statis["number_of_optimized_program_with_empty_result"] += program.statis.stats_data["number_of_optimized_prog_with_empty_result"]
        total_statis["number_of_reference_program_with_empty_result"] += program.statis.stats_data["number_of_ref_prog_with_empty_result"]
        total_statis["number_of_optimized_prog_with_final_empty_result"] += program.statis.stats_data["is_final_result_of_opt_prog_empty"]
        total_statis["number_of_optimized_prog_with_final_non_empty_result"] += program.statis.stats_data["is_final_result_of_opt_prog_nonempty"]
        total_statis["total_number_of_optimized_timeouts"] += program.statis.stats_data["total_optimized_timeouts"]
        total_statis["total_number_of_reference_timeouts"] += program.statis.stats_data["total_reference_timeouts"]
        total_statis["total_optimized_errors"] += program.statis.stats_data["total_optimized_errors"]
        total_statis["total_reference_errors"] += program.statis.stats_data["total_reference_errors"]
        total_statis["total_optimized_assertion_failures"] += program.statis.stats_data["total_optimized_assertion_failures"]
        total_statis["total_reference_assertion_failures"] += program.statis.stats_data["total_reference_assertion_failures"]
        total_statis["total_final_program_fail"] += program.statis.stats_data["is_final_program_fail"]
        total_statis["total_final_program_normal"] += program.statis.stats_data["is_final_program_normal"]
        total_statis["iterations_for_recursive_query_exceed_threshold"] += program.statis.stats_data["iterations_for_recursive_query_exceed_threshold"]
        total_statis["find_logic_bug"] +=program.statis.stats_data["find_logic_bug"]

        if total_statis["test_case_number"] != 0:
            total_statis["average_rule_number"] = total_statis["total_rules"] / total_statis["test_case_number"]
            total_statis["average_execution_time_for_test_case"] = total_statis["total_execution_time"] / total_statis["test_case_number"]
        if total_statis["number_of_times_for_evaluating_reference_program"] != 0:
            total_statis["average_execution_time_for_reference_program"] = total_statis["total_time_for_reference_program"] / total_statis["number_of_times_for_evaluating_reference_program"]
        if total_statis["number_of_times_for_evaluating_optimized_program"] != 0:
            total_statis["average_execution_time_for_optimized_program"] = total_statis["total_time_for_optimized_program"] / total_statis["number_of_times_for_evaluating_optimized_program"]
        if total_statis["test_case_number"] != 0:
            total_statis["average_recursive_query_number"] = total_statis["total_recursive_query_number"] / total_statis["test_case_number"]
        if total_statis["total_recursive_query_number"] != 0:
            total_statis["average_recursive_query_length"] = total_statis["total_recursive_query_length"] / total_statis["total_recursive_query_number"]
        if total_statis["total_rules"] != 0:
            total_statis["probability_of_optimized_program_with_enmpty_result"] = total_statis["number_of_optimized_program_with_empty_result"] / total_statis["total_rules"]
        if total_statis["test_case_number"] != 0:
            total_statis["probability_of_final_program_with_empty_result"] = total_statis["number_of_optimized_prog_with_final_empty_result"] / total_statis["test_case_number"]

        print(colored("ok", "green", attrs=["bold"]))
        current_time = time.time()
        if PARAMS["total_fuzzing_time"] > 0 and current_time - fuzzing_begin_time >= PARAMS["total_fuzzing_time"] * 60 * 60:
            with open(os.path.join(core_dir_path, "statis.json"), 'w', encoding="utf-8") as outfile:
                json.dump(total_statis, outfile, sort_keys=False)
            return

def main():
    # init
    # Set home link in parameters file
    datalog_difftest_home = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Create a params.json file at home directory location. Copy everything from default_params.py
    default_parameters = os.path.join(datalog_difftest_home, "deopt", "default_params.json")
    with open(default_parameters) as f:
        data = json.load(f)
        json_dump = json.dumps(data, indent=4)


    # Create params.json at home
    data["datalog_difftest_home"] = datalog_difftest_home
    params_json_path = os.path.join(datalog_difftest_home, "params.json")
    if not os.path.exists(params_json_path):
        file=open(params_json_path ,"w")
        file.write("")
        file.close()
        with open(params_json_path, "w") as outfile:
            json.dump(data, outfile, indent=4)

    global HOME         # Datalog Differential Testing home (retrieved from params.py)
    global VERBOSE      # Verbose mode (We will print a lot of stuff + we won't handle errors and just stop)
    global PARAMS       # Tunable parameters
    global ENGINE       # Datalog engine
    global CORES        # Number of cores
    initial_text = pyfiglet.figlet_format("Datalog Deopt")
    print(colored(initial_text , "yellow", attrs=["bold"]))
    # Parse arguments
    arguments = MainArgumentParser()
    arguments.parse_arguments(argparse.ArgumentParser())
    parsedArguments = arguments.get_arguments()
    VERBOSE = parsedArguments["verbose"]
    SEED = parsedArguments["seed"]
    HOME = str(datalog_difftest_home)
    CORES = parsedArguments["cores"]
    PARAMS = load_parameters(HOME)
    ENGINE = parsedArguments["engine"]

    # INSTALL SOUFFLE IF IT IS NOT FOUND -----------------------------------------------------------
    if ENGINE == "souffle" and PARAMS["path_to_souffle_engine"] == "":
        if os.path.exists(os.path.join("/usr", "bin", "souffle")):
            # Add souffle path in params.json
            with open(os.path.join(HOME, "params.json")) as f: data = json.load(f)
            data["path_to_souffle_engine"] = os.path.join("/usr", "bin", "souffle")
            with open(os.path.join(HOME, "params.json"), "w") as f: json.dump(data, f, indent=4)
            # Reload PARAMS
            PARAMS = load_parameters(HOME) 
        else:
            not_valid_path = True
            while not_valid_path:
                path_to_souffle = input(colored("Please provide full path to souffle binary (/soffle/src/souffle): ", "red", attrs=["bold"]))
                if os.path.exists(path_to_souffle):
                    not_valid_path = False
                    with open(os.path.join(HOME, "params.json")) as f:  # Add souffle path in params.json
                        data = json.load(f)
                    data["path_to_souffle_engine"] = path_to_souffle
                    with open(os.path.join(HOME, "params.json"), "w") as f:
                        json.dump(data, f, indent=4)
                else:
                    print("This is not a valid path: " + path_to_souffle)
            PARAMS = load_parameters(HOME)  # Reload PARAMS

    # Z3 not found
    if ENGINE == "z3" and PARAMS["path_to_z3_engine"] == "":
        if os.path.exists(os.path.join("/usr", "bin", "z3")):
            # Add z3 path in params.json
            with open(os.path.join(HOME, "params.json")) as f: data = json.load(f)
            data["path_to_z3_engine"] = os.path.join("/usr", "bin", "z3")
            with open(os.path.join(HOME, "params.json"), "w") as f: json.dump(data, f, indent=4)
            # Reload PARAMS
            PARAMS = load_parameters(HOME) 
        else:
            print(colored("Please provide path to z3 binary in " + HOME + "/params.json and run again", "red", attrs=["bold"]))
            return 1

    # DDLOG not found
    if ENGINE == "ddlog" and PARAMS["path_to_ddlog_engine"] == "" and PARAMS["path_to_ddlog_home_dir"] == "":
        if os.path.exists(os.path.join("/usr", "bin", "ddlog")):
            # Add ddlog path in params.json
            with open(os.path.join(HOME, "params.json")) as f: data = json.load(f)
            data["path_to_ddlog_engine"] = os.path.join("/usr", "bin", "ddlog")
            with open(os.path.join(HOME, "params.json"), "w") as f: json.dump(data, f, indent=4)
            # Reload PARAMS
            PARAMS = load_parameters(HOME) 
        else:
            print(colored("Please provide path to ddlog binary and ddlog home directory in " + HOME + "/params.json and run again", "red", attrs=["bold"]))
            return 1


    # START FUZZING ------------------------------------------------------------------------------------
    print("\nGlobal Variables:")
    print(colored("\tHOME = ", attrs=["bold"]) + colored(HOME, "cyan", attrs=["bold"]))
    print(colored("\tCORES = ", attrs=["bold"]) + colored(CORES, "cyan", attrs=["bold"]))
    print(colored("\tENGINE = ", attrs=["bold"]) + colored(ENGINE, "cyan", attrs=["bold"]))

    create_temp_directory(os.path.join(HOME, "temp")) # Create server directory in temp
    print("Begin fuzzing!\n")
    try:
        start_time = time.time()
        if CORES is not None:
            for i in range(int(CORES)):
                core = i
                wait = int(CORES)
                local_seed = str(int(SEED) + core)
                process = multiprocessing.Process(target=run, args=(core, local_seed, wait))
                process.start()
                # pin the process to a specific CPU
                os.system("taskset -p -c " + str(i) + " " + str(process.pid))
        else:
            run(core=0, local_seed=SEED, wait=0)

        end_time = time.time()
        print("total time: " + str(end_time - start_time))
    except (KeyboardInterrupt, SystemExit) as e:
        end_time = time.time()
        print("total time: " + str(end_time - start_time))
        print("\nGood Bye!\n")
        logging.exception(e)
    except Exception as e:
        logging.exception(e)

if __name__ == '__main__':
    signal = main()
