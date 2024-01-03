import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
import json
import sys

default_param = {
	"execution_mode": "evaluation",
	"original_timeout" : 60,
	"single_query_timeout" : 10,
	"path_to_souffle_engine" : "/tmp/souffle/build/src/souffle",
	"path_to_ddlog_engine" : "/root/.local/bin/ddlog",
	"path_to_ddlog_home_dir" : "/tmp/differential-datalog",
	"path_to_z3_engine" : "",
	"souffle_types" : ["number", "symbol", "unsigned", "float"],
	"z3_types" :["Z"],
	"ddlog_types" : ["string", "bool", "bit<32>", "signed<64>", "bigint", "float", "double"],
	"xsb_types" : ["number"],
	"cozodb_types" : ["Null", "Bool", "Number", "String"],
	"logica_types" : ["Number", "String"],
	"souffle_options" : ["", 
		"--magic-transform=*", 
		"--magic-transform-exclude=*", 
		"--profile-frequency", 
		"-t none",
		"-j 4", 
		"--legacy", 
		"-PSIPS:strict", 
		"-PSIPS:all-bound", 
		"-PSIPS:naive", 
		"-PSIPS:max-bound", 
		"-PSIPS:max-ratio", 
		"-PSIPS:least-free", 
		"-PSIPS:least-free-vars", 
		"-PSIPS:input"
	],
	"souffle_disable_options" : [
		"ExpandEqrelsTransformer", 
		"RemoveRelationCopiesTransformer", 
		"ResolveAliasesTransformer", 
		"MaterializeSingletonAggregationTransformer", 
		"MinimiseProgramTransformer", 
		"AstSemanticChecker", 
		"ReplaceSingletonVariablesTransformer", 
		"PartitionBodyLiteralsTransformer", 
		"InliningTransformer"
	],

	"in_file_facts" : True,
	"max_number_of_facts" : 3,
	"max_number_of_fact_rows" : 5,
	"max_fact_arity" : 3,
	"max_head_arity" : 8,

	"max_number_rules" : 100,
	"max_number_of_attempts_for_rule_generation": 100,
	"max_number_of_body_subgoals" : 3,

	"probability_of_negated" : 2,
	"probability_of_underline": 2,
	"probability_of_constant": 2,
	
	"probability_of_predicate": 2,
	"max_number_of_predicates" : 3,

	"probability_of_head_operations": 2,
	"max_expression_adding_operations": 3,

	"probability_of_rule_body_operations": 2,
	
	"probability_of_aggregate": 2,
	"probability_of_generator": 2,
	"probability_of_subsumption": 2,

	"probability_of_eqrel_relation": 2,
	"probability_of_disjunctive_rule": 2,
	
	"max_number_of_random_type": 10,

	"probability_of_recursive_rule": 2,
	"max_iterations_for_recursive_query": 100,
	
	"max_heads_in_mixed_rule" : 3,

	"add_inline_and_magic": False,

	"probability_of_query_plan": 2,

	"probability_of_empty_result_rule": 10,
	"max_size_of_facts": 1000,

	"total_fuzzing_time": 24
}

def generate_param_file(task_name):
    param = default_param.copy()
    if task_name.startswith('compare_with_random'):
        if 'normal' not in task_name:
            param['execution_mode'] = 'random'
        param['max_number_rules'] = int(task_name.split('_')[-1])
    elif task_name.startswith('max_att'):
        param['max_number_of_attempts_for_rule_generation'] = int(task_name.split('_')[-1])
    elif task_name.startswith('max_iter'):
        param['max_iterations_for_recursive_query'] = int(task_name.split('_')[-1])
    elif task_name.startswith('max_rules'):
        param['max_number_rules'] = int(task_name.split('_')[-1])
    elif task_name.startswith('p_empty'):
        param['probability_of_empty_result_rule'] = int(task_name.split('_')[-1])
    elif task_name.startswith('p_head'):
        param['probability_of_head_operations'] = int(task_name.split('_')[-1])
    else:
        return None
    return param

def save_results(task_name):
    task_dir = task_name
    param_file_path = os.path.join(task_dir, 'params.json')
    result_file_path = os.path.join(task_dir, 'temp', 'core_0', 'statis.json')

    result_dir = ''
    conf_value = task_name.split('_')[-1]
    if task_name.startswith('compare_with_random'):
        result_dir = os.path.join('./results', 'compare_with_random')
        os.makedirs(result_dir, exist_ok=True)
        if 'ddlog' in task_name:
            result_dir = os.path.join(result_dir, 'ddlog')
        else:
            result_dir = os.path.join(result_dir, 'souffle')
        execution_mode = task_name.split('_')[-2]
        result_dir = os.path.join(result_dir, execution_mode + '_' + conf_value)
    elif task_name.startswith('max_att'):
        result_dir = os.path.join('./results', 'max_att', conf_value)
    elif task_name.startswith('max_iter'):
        result_dir = os.path.join('./results', 'max_iter', conf_value)
    elif task_name.startswith('max_rules'):
        if 'ddlog' in task_name:
            result_dir = os.path.join('./results', 'max_rules', 'ddlog', conf_value)
        else:
            result_dir = os.path.join('./results', 'max_rules', 'souffle', conf_value)
    elif task_name.startswith('p_empty'):
        result_dir = os.path.join('./results', 'p_empty', conf_value)
    elif task_name.startswith('p_head'):
        result_dir = os.path.join('./results', 'p_head', conf_value)
    else:
        return
    os.makedirs(result_dir, exist_ok=True)
    new_param_file_path = os.path.join(result_dir, 'params.json')
    new_result_file_path = os.path.join(result_dir, 'statis.json')
    shutil.copy2(param_file_path, new_param_file_path)
    shutil.copy2(result_file_path, new_result_file_path)

def run_docker_task(task_name):
    print("Running task:", task_name, "...")
    task_dir = task_name
    os.makedirs(task_dir, exist_ok=True)

    if os.path.exists(task_dir):
        os.rmdir(task_dir)
    try:
        for item in os.listdir('./deopt'):
            s = os.path.join('./deopt', item)
            d = os.path.join(task_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
    except Exception as e:
        print(e)

    param_file_path = os.path.join(task_dir, 'params.json')
    param = generate_param_file(task_name)
    if param is None:
        return
    with open(param_file_path, 'w') as f:
        json.dump(param, f)

    run_cmd = "python3 deopt/__main__.py"
    if 'ddlog' in task_name:
        run_cmd += " --engine=ddlog"

    docker_command = [
        "docker", "run", "--rm",
        "-v", f"{os.path.abspath(task_dir)}:/tmp/deopt",
        "deopt", "/bin/bash", "-c",
        "cd deopt; " + run_cmd + " &>/dev/null;"
    ]
    subprocess.run(docker_command)

    save_results(task_name)
    # os.rmdir(task_dir)

def analysis_results():
    shutil.copy('./deopt/evaluation/Q2Q3/data_analyzer.py', './data_analyzer.py')
    cmd = [
        "python3", "data_analyzer.py"
    ]
    subprocess.run(cmd)

def main(num_threads):
    tasks = [
        'compare_with_random_ddlog_normal_40',
        'compare_with_random_ddlog_normal_60',
        'compare_with_random_ddlog_normal_80',
        'compare_with_random_ddlog_random_40',
        'compare_with_random_ddlog_random_60',
        'compare_with_random_ddlog_random_80',
        'compare_with_random_souffle_normal_40',
        'compare_with_random_souffle_normal_60',
        'compare_with_random_souffle_normal_80',
        'compare_with_random_souffle_random_40',
        'compare_with_random_souffle_random_60',
        'compare_with_random_souffle_random_80',
        'max_att_10',
        'max_att_20',
        'max_att_30',
        'max_att_40',
        'max_att_50',
        'max_att_60',
        'max_att_70',
        'max_iter_10',
        'max_iter_50',
        'max_iter_100',
        'max_iter_200',
        'max_iter_300',
        'max_rules_ddlog_5',
        'max_rules_ddlog_10',
        'max_rules_ddlog_20',
        'max_rules_ddlog_40',
        'max_rules_ddlog_60',
        'max_rules_ddlog_80',
        'max_rules_ddlog_100',
        'max_rules_souffle_5',
        'max_rules_souffle_10',
        'max_rules_souffle_20',
        'max_rules_souffle_40',
        'max_rules_souffle_60',
        'max_rules_souffle_80',
        'max_rules_souffle_100',
        'p_empty_0',
        'p_empty_20',
        'p_empty_40',
        'p_empty_60',
        'p_empty_80',
        'p_empty_100',
        'p_head_0',
        'p_head_2',
        'p_head_4',
        'p_head_6',
        'p_head_8',
        'p_head_10'
    ]

    os.makedirs("./results", exist_ok=True)

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(run_docker_task, tasks)

    print("All tasks finished.")

    analysis_results()

if __name__ == "__main__":
    num_threads = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    main(num_threads)
