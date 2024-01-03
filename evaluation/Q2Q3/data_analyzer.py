import json
import matplotlib.pyplot as plt
import numpy as np

def read_json(file_path):
    with open(file_path, 'r') as f:
        res = json.load(f)
    return res
results_basepath = "results/"

# create the figure
fig, axs = plt.subplots(5, 2, figsize=(9, 12))

# rules threshold
rules_threshold_souffle_path = results_basepath + "max_rules/souffle/"
rules_threshold_ddlog_path = results_basepath + "max_rules/ddlog/"
rules_config = [5, 10, 20, 40, 60, 80, 100]
souffle_ratio = ""
souffle_ref_weight = ""
souffle_opt_weight = ""

ddlog_ratio = ""
ddlog_ref_weight = ""
ddlog_opt_weight = ""

souffle_ratio_list = []
souffle_ref_weight_list = []
ddlog_ratio_list = []
ddlog_ref_weight_list = []
for conf in rules_config:
    souffle_result = read_json(rules_threshold_souffle_path + str(conf) + "/statis.json")
    souffle_ratio += "(%s, %s) " % (conf, souffle_result["average_execution_time_for_optimized_program"]/souffle_result["average_execution_time_for_reference_program"])
    souffle_ratio_list.append(souffle_result["average_execution_time_for_optimized_program"]/souffle_result["average_execution_time_for_reference_program"])
    souffle_ref_weight += "(%s, %s) " % (conf, souffle_result["total_time_for_reference_program"]/(souffle_result["total_time_for_reference_program"] + souffle_result["total_time_for_optimized_program"]))
    souffle_ref_weight_list.append(souffle_result["total_time_for_reference_program"]/(souffle_result["total_time_for_reference_program"] + souffle_result["total_time_for_optimized_program"]))
    souffle_opt_weight += "(%s, %s) " % (conf, souffle_result["total_time_for_optimized_program"]/(souffle_result["total_time_for_reference_program"] + souffle_result["total_time_for_optimized_program"]))
    ddlog_result = read_json(rules_threshold_ddlog_path + str(conf) + "/statis.json")
    ddlog_ratio += "(%s, %s) " % (conf, ddlog_result["average_execution_time_for_optimized_program"]/ddlog_result["average_execution_time_for_reference_program"])
    ddlog_ratio_list.append(ddlog_result["average_execution_time_for_optimized_program"]/ddlog_result["average_execution_time_for_reference_program"])
    ddlog_ref_weight += "(%s, %s) " % (conf, ddlog_result["total_time_for_reference_program"]/(ddlog_result["total_time_for_reference_program"] + ddlog_result["total_time_for_optimized_program"]))
    ddlog_ref_weight_list.append(ddlog_result["total_time_for_reference_program"]/(ddlog_result["total_time_for_reference_program"] + ddlog_result["total_time_for_optimized_program"]))
    ddlog_opt_weight += "(%s, %s) " % (conf, ddlog_result["total_time_for_optimized_program"]/(ddlog_result["total_time_for_reference_program"] + ddlog_result["total_time_for_optimized_program"]))

print("The results for Max_rules: ")
print("execution time ratio for souffle: ")
print(souffle_ratio)
print("reference program execution time percentage for souffle: ")
print(souffle_ref_weight)
# print("optimized program execution time percentage for souffle: ")
# print(souffle_opt_weight)

print("execution time ratio for ddlog: ")
print(ddlog_ratio)
print("reference program execution time weight for ddlog: ")
print(ddlog_ref_weight)
# print("optimized program execution time weight for ddlog: ")
# print(ddlog_opt_weight)

axs[0, 0].plot(rules_config, souffle_ref_weight_list)
axs[0, 0].plot(rules_config, ddlog_ref_weight_list)
axs[0, 0].set_title("Runtime percentage (Figure 6(a)).")

axs[0, 1].plot(rules_config, souffle_ratio_list)
axs[0, 1].plot(rules_config, ddlog_ratio_list)
axs[0, 1].set_title("The cause of results (Figure 6(b)).")

print("")
print("")

# attemtps
attempts_path = results_basepath + "max_att/"

attempts_configs = [10, 20, 30, 40, 50, 60, 70]
average_program_size_results = ""
total_test_case = ""

average_program_size_list = []
total_test_case_list = []
for conf in attempts_configs:
    result = read_json(attempts_path + str(conf) + "/statis.json")
    average_program_size_results += "(%s, %s)" % (conf, result["average_rule_number"])
    average_program_size_list.append(result["average_rule_number"])
    total_test_case += "(%s, %s)" % (conf, result["test_case_number"])
    total_test_case_list.append(result["test_case_number"])

print("The results for Max_att: ")
print("number of rules in each test iteration: ")
print(average_program_size_results)
print("total test case number: ")
print(total_test_case)

axs[1, 0].plot(attempts_configs, average_program_size_list)
axs[1, 0].set_title("Average number of rules (Figure 7(a).")

axs[1, 1].plot(attempts_configs, total_test_case_list)
axs[1, 1].set_title("Number of test cases (Figure 7(b)).")

print("")
print("")


# emtpy
empty_path = results_basepath + "p_empty/"
empty_configs = [0, 20, 40, 60, 80, 100]
opt_empty_prob = ""
final_empty_prob = ""
total_test_case = ""
opt_empty_prob_list = []
total_test_case_list = []
for conf in empty_configs:
    result = read_json(empty_path + str(conf) + "/statis.json")
    opt_empty_prob += "(%s, %s) " % (conf, result["probability_of_optimized_program_with_enmpty_result"])
    opt_empty_prob_list.append(result["probability_of_optimized_program_with_enmpty_result"])
    final_empty_prob += "(%s, %s) " % (conf, result["probability_of_final_program_with_empty_result"])
    total_test_case += "(%s, %s)" % (conf, result["test_case_number"])
    total_test_case_list.append(result["test_case_number"])
print("The results for P_empty: ")
print("probability of optimized program with empty results: ")
print(opt_empty_prob)
# print("probability of final test case in each test iteration with empty results: ")
# print(final_empty_prob)
print("total test iterations number: ")
print(total_test_case)


axs[2, 0].plot(empty_configs, opt_empty_prob_list)
axs[2, 0].set_title("Empty results probability (Figure 8(a)).")

axs[2, 1].plot(empty_configs, total_test_case_list)
axs[2, 1].set_title("Test iterations (Figure 8(b)).")
axs[2, 1].set_ylim(bottom=0)

print()
print()


# probability of duplicate head
rq_path = results_basepath + "p_head/"
rq_configs = [0, 2, 4, 6, 8, 10]
average_circle_number = ""
average_circle_length = ""
average_circle_number_list = []
average_circle_length_list = []
for conf in rq_configs:
    result = read_json(rq_path + str(conf) + "/statis.json")
    average_circle_number += "(%s, %s) " % (conf, result["average_recursive_query_number"])
    average_circle_number_list.append(result["average_recursive_query_number"])
    average_circle_length += "(%s, %s) " % (conf, result["average_recursive_query_length"])
    average_circle_length_list.append(result["average_recursive_query_length"])

print("The results for P_head:")
print("average cycle number for each test case: ")
print(average_circle_number)
print("average cycle length for each circle: ")
print(average_circle_length)

axs[3, 0].plot(rq_configs, average_circle_number_list)
ax2 = axs[3, 0].twinx()
ax2.plot(rq_configs, average_circle_length_list, 'g-')
axs[3, 0].set_title("Results of P_head (Figure 9(a).")

print()
print()

# max iteration
iteration_path = results_basepath + "max_iter/"
iter_configs = [10, 50, 100, 200, 300]
average_circle_number = ""
average_circle_number_list2 = []
average_circle_length = ""
average_circle_length_list2 = []
for conf in iter_configs:
    result = read_json(iteration_path + str(conf) + "/statis.json")
    average_circle_number += "(%s, %s) " % (conf, result["average_recursive_query_number"])
    average_circle_number_list2.append(result["average_recursive_query_number"])
    average_circle_length += "(%s, %s) " % (conf, result["average_recursive_query_length"])
    average_circle_length_list2.append(result["average_recursive_query_length"])

print("The results for Max_iter: ")
print("average circle number for each test case: ")
print(average_circle_number)
print("average circle length for each circle: ")
print(average_circle_length)

axs[3, 1].plot(iter_configs, average_circle_number_list2)
ax3 = axs[3, 1].twinx()
ax3.plot(iter_configs, average_circle_length_list2, 'g-')
axs[3, 1].set_title("Results of Max_iter (Figure 9(b).")

print()
print()


# compare with random
random_path = results_basepath + "compare_with_random/"
souffle_random_path = random_path + "souffle/"
ddlog_random_path = random_path + "ddlog/"
random_configs = [40, 60, 80]
souffle_inc_total = ""
souffle_inc_valid = ""
souffle_inc_nonempty = ""
souffle_ran_total = ""
souffle_ran_valid = ""
souffle_ran_nonempty = ""
ddlog_inc_total = ""
ddlog_inc_valid = ""
ddlog_inc_nonempty = ""
ddlog_ran_total = ""
ddlog_ran_valid = ""
ddlog_ran_nonempty = ""
souffle_inc_total_list = []
souffle_inc_valid_list = []
souffle_inc_nonempty_list = []
souffle_ran_total_list = []
souffle_ran_valid_list = []
souffle_ran_nonempty_list = []
ddlog_inc_total_list = []
ddlog_inc_valid_list = []
ddlog_inc_nonempty_list = []
ddlog_ran_total_list = []
ddlog_ran_valid_list = []
ddlog_ran_nonempty_list = []
for conf in random_configs:
    result = read_json(souffle_random_path + "normal_" + str(conf) + "/statis.json")
    souffle_inc_total += "(%s, %s) " % (conf, result["test_case_number"])
    souffle_inc_total_list.append(result["test_case_number"])
    souffle_inc_valid += "(%s, %s) " % (conf, result["total_final_program_normal"])
    souffle_inc_valid_list.append(result["total_final_program_normal"])
    souffle_inc_nonempty += "(%s, %s) " % (conf, result["number_of_optimized_prog_with_final_non_empty_result"])
    souffle_inc_nonempty_list.append(result["number_of_optimized_prog_with_final_non_empty_result"])
    result = read_json(souffle_random_path + "random_" + str(conf) + "/statis.json")
    souffle_ran_total += "(%s, %s) " % (conf, result["test_case_number"])
    souffle_ran_total_list.append(result["test_case_number"])
    souffle_ran_valid += "(%s, %s) " % (conf, result["total_final_program_normal"])
    souffle_ran_valid_list.append(result["total_final_program_normal"])
    souffle_ran_nonempty += "(%s, %s) " % (conf, result["number_of_optimized_prog_with_final_non_empty_result"])
    souffle_ran_nonempty_list.append(result["number_of_optimized_prog_with_final_non_empty_result"])

    result = read_json(ddlog_random_path + "normal_" + str(conf) + "/statis.json")
    ddlog_inc_total += "(%s, %s) " % (conf, result["test_case_number"])
    ddlog_inc_total_list.append(result["test_case_number"])
    ddlog_inc_valid += "(%s, %s) " % (conf, result["total_final_program_normal"])
    ddlog_inc_valid_list.append(result["total_final_program_normal"])
    ddlog_inc_nonempty += "(%s, %s) " % (conf, result["number_of_optimized_prog_with_final_non_empty_result"])
    ddlog_inc_nonempty_list.append(result["number_of_optimized_prog_with_final_non_empty_result"])
    result = read_json(ddlog_random_path + "random_" + str(conf) + "/statis.json")
    ddlog_ran_total += "(%s, %s) " % (conf, result["test_case_number"])
    ddlog_ran_total_list.append(result["test_case_number"])
    ddlog_ran_valid += "(%s, %s) " % (conf, result["total_final_program_normal"])
    ddlog_ran_valid_list.append(result["total_final_program_normal"])
    ddlog_ran_nonempty += "(%s, %s) " % (conf, result["number_of_optimized_prog_with_final_non_empty_result"])
    ddlog_ran_nonempty_list.append(result["number_of_optimized_prog_with_final_non_empty_result"])

print("The results for comparing with random test case generation: ")
print("souffle inc total: ")
print(souffle_inc_total)
print("souffle inc valid: ")
print(souffle_inc_valid)
print("souffle inc non-empty: ")
print(souffle_inc_nonempty)
print("souffle random total: ")
print(souffle_ran_total)
print("souffle random valid: ")
print(souffle_ran_valid)
print("souffle random non-empty: ")
print(souffle_ran_nonempty)

print("ddlog inc total: ")
print(ddlog_inc_total)
print("ddlog inc valid: ")
print(ddlog_inc_valid)
print("ddlog inc non-empty: ")
print(ddlog_inc_nonempty)
print("ddlog random total: ")
print(ddlog_ran_total)
print("ddlog random valid: ")
print(ddlog_ran_valid)
print("ddlog random non-empty: ")
print(ddlog_ran_nonempty)

bar_width = 1.0
axs[4, 0].bar([x - 2.5 * bar_width for x in random_configs], souffle_inc_total_list, color='b', width=bar_width)
axs[4, 0].bar([x - 1.5 * bar_width for x in random_configs], souffle_inc_valid_list, color='r', width=bar_width)
axs[4, 0].bar([x - 0.5 * bar_width for x in random_configs], souffle_inc_nonempty_list, color='y', width=bar_width)
axs[4, 0].bar([x + 0.5 * bar_width for x in random_configs], souffle_ran_total_list, color='m', width=bar_width)
axs[4, 0].bar([x + 1.5 * bar_width for x in random_configs], souffle_ran_valid_list, color='b', width=bar_width)
axs[4, 0].bar([x + 2.5 * bar_width for x in random_configs], souffle_ran_nonempty_list, color='g', width=bar_width)



axs[4, 1].bar([x - 2.5 * bar_width for x in random_configs], ddlog_inc_total_list, color='b', width=bar_width)
axs[4, 1].bar([x - 1.5 * bar_width for x in random_configs], ddlog_inc_valid_list, color='r', width=bar_width)
axs[4, 1].bar([x - 0.5 * bar_width for x in random_configs], ddlog_inc_nonempty_list, color='y', width=bar_width)
axs[4, 1].bar([x + 0.5 * bar_width for x in random_configs], ddlog_ran_total_list, color='m', width=bar_width)
axs[4, 1].bar([x + 1.5 * bar_width for x in random_configs], ddlog_ran_valid_list, color='b', width=bar_width)
axs[4, 1].bar([x + 2.5 * bar_width for x in random_configs], ddlog_ran_nonempty_list, color='g', width=bar_width)

# draw the figure
plt.tight_layout()
plt.savefig('result.pdf', format='pdf')
# plt.show()