from deopt.runner.base_runner import BaseRunner
import subprocess
import os
from termcolor import colored
from deopt.utils.file_operations import create_fact_file_with_data


class Z3Runner(BaseRunner):
    def process_output(self, standard_output, orig):
        """
            parse z3's output and export the results as a csv at the specified location
        """
        def parse_z3_standard_output(std_output):
            lines = std_output.split("\n")
            clean_data = list()
            for line in lines:
                if line.find("Tuples") != -1: continue
                if line.find("Time") != -1: continue
                if line.find("Parsing") != -1: continue
                if line == "": continue
                data_line = line.replace("\t", "") # remove tabs
                data_line = data_line[1:-1] # remove first and last brackets
                data_row = data_line.split(",")
                for i in range(len(data_row)):
                    # data_row[i] = data_row[i][data_row[i].find("=")+1 : data_row[i].find("(")]
                    data_row[i] = data_row[i][data_row[i].find("(")+1 : data_row[i].find(")")]
                    #if output_data_type == "unsigned":
                    #    data_row[i] = int(data_row[i])
                #print(data_row)
                # convert rata row to a string
                row_string = "".join(i + "\t" for i in data_row )
                row_string = row_string[:-1]
                clean_data.append(row_string)
                # print(colored(row_string, "green", attrs=["bold"]))
            self.clean_data = clean_data
            return clean_data

        parsed_result = parse_z3_standard_output(standard_output)
        if orig: 
            # Orig result
            results_file_name = os.path.join(self.program.get_program_path(), "orig.facts")
            self.program.set_output_result_path(results_file_name)
        else:
            # Single query result
            results_file_name = os.path.join(self.program.get_program_path(), "single_query.facts")
            self.program.set_single_query_result_path(results_file_name)
        create_fact_file_with_data(parsed_result, results_file_name)


    def generate_command(self, time_out, options, dl_file_path):
        command = "timeout -s SIGKILL " + str(time_out) + "s "
        command += self.path_to_engine
        command += options
        command += " " + dl_file_path
        return command


    def run_original(self, engine_options):
        self.path_to_engine = self.params["path_to_z3_engine"]
        command = self.generate_command(time_out=self.params["original_timeout"], options=engine_options, dl_file_path=self.program.get_program_file_path())
        self.program.add_log_text(" ================== ")
        self.program.add_log_text("  Running Original ")
        self.program.add_log_text(" ================== ")
        self.program.add_log_text("\tCommand: " + command)
        self.program.dump_program_log_file()

        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode(errors='ignore')
        standard_output = p.stdout.read().decode(errors='ignore')

        self.program.add_log_text("\nSTANDARD ERROR: " + standard_error)
        self.program.add_log_text("\nSTANDARD OUTPUT: " + standard_output)
        self.program.dump_program_log_file()
        error_signal = self.process_standard_error(standard_error=standard_error)
        self.program.add_log_text("\tSignal = " + str(error_signal))
        self.program.dump_program_log_file()
        if error_signal != 0:
            self.program.add_log_text(" XXX Something went wrong XXX")
            self.program.dump_program_log_file()
            return error_signal
        self.process_output(standard_output=standard_output, orig=True)
        output_file_path = os.path.join(self.program.get_program_path(), "orig.facts")
        if not os.path.exists(output_file_path):
            print(colored("NO OUTPUT FILE PRODUCED", "red", attrs=["bold"]))
            self.program.add_log_text("WARNING: NO OUTPUT FILE PRODUCED")
            self.program.dump_program_log_file()
            return 1
        if "too many arguments passed to predicate" in standard_error or "too few arguments passed to predicate" in standard_error:
            return 3
        
        self.program.set_output_result_path(output_file_path)
        self.program.add_log_text("Everything seems to be ok")
        self.program.dump_program_log_file()
        # print(colored(standard_error, "red", attrs=["bold"])) 
        #print(colored(self.clean_data, "yellow", attrs=["bold"]))
        return 0


    def run_single_query(self, engine_options):
        self.path_to_engine = self.params["path_to_z3_engine"]
        command = self.generate_command(time_out=self.params["original_timeout"], options=engine_options, dl_file_path=self.program.get_single_query_file_path())
        self.program.add_log_text(" ====================== ")
        self.program.add_log_text("  Running Single Query ")
        self.program.add_log_text(" ====================== ")
        self.program.add_log_text("\n\tCurrent rule: " + self.program.output_rule.string + "\n")
        self.program.add_log_text("\tCommand: " + command)
        self.program.dump_program_log_file()
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode(errors='ignore')
        standard_output = p.stdout.read().decode(errors='ignore')
        self.program.add_log_text("\nSTANDARD ERROR: " + standard_error)
        self.program.add_log_text("\nSTANDARD OUTPUT: " + standard_output)
        self.program.dump_program_log_file()
        error_signal = self.process_standard_error(standard_error=standard_error)
        self.program.add_log_text("\tSignal = " + str(error_signal))
        self.program.dump_program_log_file()
        if error_signal != 0:
            self.program.add_log_text(" XXX Something went wrong XXX")
            self.program.dump_program_log_file()
            return error_signal
        self.process_output(standard_output=standard_output, orig=False)
        output_file_path = os.path.join(self.program.get_program_path(), "single_query.facts")
        if not os.path.exists(output_file_path):
            print(colored("NO OUTPUT FILE PRODUCED", "red", attrs=["bold"]))
            self.program.add_log_text("WARNING: NO OUTPUT FILE PRODUCED")
            self.program.dump_program_log_file()
            return 1
        self.program.set_output_result_path(output_file_path)
        self.program.add_log_text("Everything seems to be ok")
        self.program.dump_program_log_file()
        # print(colored(standard_error, "red", attrs=["bold"]))
        return 0


    def process_standard_error(self, standard_error):
        if standard_error.find("Killed") != -1:
            print(colored("TIMEOUT", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Timeout")
            return 3    # We don't care about this        
        return 0
