from deopt.runner.base_runner import BaseRunner
import subprocess
from termcolor import colored
import os
from deopt.utils.file_operations import create_fact_file_with_data
import shutil

class DDlogRunner(BaseRunner):

    def __init__(self, params, program):
        super().__init__(params, program)
        self.execution_path = os.path.join("/".join(self.program.get_program_path().split("/")[:-3]), "program_execution")
        if not os.path.exists(self.execution_path):
            os.mkdir(self.execution_path)

    def process_output(self, standard_output, orig):
        def parse_ddlog_standard_output(std_output):
            """
                JTKG{.a = "4Dumgdnpgi", .b = "1e3PUPow3z", .c = "4Dumgdnpgi"}
                JTKG{.a = "4Dumgdnpgi", .b = "o54nS4Dumg", .c = "4Dumgdnpgi"}
                JTKG{.a = "Pow3z", .b = "1e3PUPow3z", .c = "Pow3z"}
                JTKG{.a = "Pow3z", .b = "o54nS4Dumg", .c = "Pow3z"}
                YJXZ{.a = "lm1xdGq3R0", .b = "lm1xdGq3R0", .c = "C75fA"}
                OAZM{.a = "vOYyDVIa2Z", .b = "vOYyDVIa2Z"}
                UKVN{.a = "390742D3SH", .b = "5OZ6H"}
                UKVN{.a = "390742D3SH", .b = "KVIP8Q2UP7"}
                UKVN{.a = "A90vPkOAKF", .b = "5OZ6H"}
                UKVN{.a = "A90vPkOAKF", .b = "KVIP8Q2UP7"}
                UKVN{.a = "tRtCTj7Ygx", .b = "5OZ6H"}
                UKVN{.a = "tRtCTj7Ygx", .b = "KVIP8Q2UP7"}
                KVRW{.a = "KDhAk"}
                KVRW{.a = "eQZOpBTRBT"}
            """
            lines = std_output.split("\n")
            clean_data = list()
            for line in lines:
                if line.find("{") == -1:
                    # This is not a data row. ignore this
                    continue
                data_line = line.replace("\t", "")
                data_line = data_line.replace(" ", "")
                data_line = data_line[data_line.find("{") + 1:data_line.find("}")]
                data_row = data_line.split(",")
                for i in range(len(data_row)):
                    data_row[i] = data_row[i][data_row[i].find("=") + 1:]
                row_string = "".join(i + "\t" for i in data_row)
                clean_data.append(row_string)
            for i in clean_data:
                print(colored(i, "green", attrs=["bold"]))
            print(colored("length of rows = " + str(len(clean_data)), "yellow", attrs=["bold"]))
            return clean_data        


        parsed_result = parse_ddlog_standard_output(standard_output)
        if orig: 
            results_file_name = os.path.join(self.program.get_program_path(), "orig.facts")
        else:
            results_file_name = os.path.join(self.program.get_program_path(), "single_query.facts")            
    
        print("####### Exporting (as .facts) ddlog's stdout result to : ", end="")
        print(colored(results_file_name, "blue", attrs=["bold"]))
        create_fact_file_with_data(parsed_result, results_file_name)



    def process_standard_error(self, standard_error, file_type):
        if standard_error.find("is mutually recursive with") != -1 and standard_error.find("and therefore cannot appear negated in this rule") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: negative a recursive query")
            return 3

        if standard_error.find("not a float PosStruct") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: inf")
            return 3 # inf
        
        if standard_error.find("not a double PosStruct") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: inf")
            return 3 # inf

        if standard_error.find("Invalid input: ") != -1 and standard_error.find("inf") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: inf")
            return 3 # inf

        if standard_error.find("attempt to divide by zero") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: attempt to divide by zero")
            return 3 # divide-by-zero

        if standard_error.find("input relation") != -1 and standard_error.find("cannot appear in the head of a rule") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: input relation cannot appear in the head of a rule")
            return 3

        if standard_error.find("is both declared and used inside relational atom") != -1:
            # We are tolerating this for now
            print(colored(standard_error, "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: use the same variable in a relation")
            return 3

        if standard_error.find("spurious network error") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: network error")
            return 3

        if standard_error.find("Bus error") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: bus error")
            return 3

        if standard_error.find("unexpected reserved word") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: unexpected reserved wordd")
            return 3

        if standard_error.find("panicked") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            return 1

        if standard_error.find("Failed to parse input file") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            return 1

        if standard_error.find("No such file or directory") != -1 or standard_error.find("failed to run command") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            return 1

        if standard_error.find("Unknown constructor") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            return 1

        if standard_error.find("Unknown variable") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            return 3

        if standard_error.find("Multiple definitions of type") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            return 3

        if standard_error.find("ddlog: Module ddlog_rt imported by") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            print(colored("RUN: export DDLOG_HOME=/home/numair/differential-datalog/", "red", attrs=["bold"]))
            return 1

        if standard_error.find("Killed") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            print(colored("EXPERIENCED A TIMEOUT", "red", attrs=["bold"]))
            return 3

        if standard_error.find("Error") != -1 or standard_error.find("error") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            return 1
        return 0
    

    def compile_datalog_into_rust(self, orig, program_file_path):
        TIMEOUT = 600
        command = "export DDLOG_HOME=" + self.params["path_to_ddlog_home_dir"] + " && "
        command += "timeout -s SIGKILL " + str(TIMEOUT) + "s " + self.path_to_engine + " -i " + program_file_path
        
        self.program.add_log_text("\tCommand: " + command)
        self.program.dump_program_log_file()
        
        print("\tDDLOG -> RUST   COMMAND = " + command)
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        signal = self.process_standard_error(standard_error=standard_error, file_type=orig)
        if signal != 0:
            self.program.add_log_text(standard_error)
            self.program.dump_program_log_file()
            if orig:
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
        return signal


    def compile_rust_into_an_executable(self, orig, program_file_path):
        # command = 'cd ' + program_file_path[:-3] + '_ddlog/ && cargo clean && timeout -s SIGKILL 1500s cargo build --release'
        command = 'cd ' + program_file_path[:-3] + '_ddlog/ && timeout -s SIGKILL 1500s cargo build --release'
        self.program.add_log_text("\tCommand: " + command)
        self.program.dump_program_log_file()
                
        print("running:")
        print("\tRUST -> EXE   COMMAND = " + command)
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()

        self.program.add_log_text("\nSTANDARD ERROR: " + standard_error)
        self.program.add_log_text("\nSTANDARD OUTPUT: " + standard_output)
        self.program.dump_program_log_file()
        signal = self.process_standard_error(standard_error, orig)
        if signal != 0:
            self.program.add_log_text(standard_error)
            self.program.dump_program_log_file()
            if orig:
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
        return signal



    def run_ddlog_program(self, orig, program_file_path):
        TIMEOUT = 600
        if orig:
            self.program_name = "orig_rules"
        else:
            self.program_name = "single_query"
        command = "timeout -s SIGKILL " + str(TIMEOUT) + "s " + program_file_path[:-3] + "_ddlog/target/release/" + self.program_name + "_cli < " + self.program.get_program_path() + "facts.dat"
        print("RUN command -> " + command)
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        signal = self.process_standard_error(standard_error, orig)

        if signal != 0:
            self.program.add_log_text(standard_error)
            self.program.dump_program_log_file()
            if orig:
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return signal
        print(colored(standard_output, "green", attrs=["bold"]))
        print(colored(standard_error, "red", attrs=["bold"]))
        self.process_output(standard_output=standard_output, orig=orig)
        
        
        if orig: 
            output_file_path = os.path.join(self.program.get_program_path(), "orig.facts")
        else:
            output_file_path = os.path.join(self.program.get_program_path(), "single_query.facts")
        
        if not os.path.exists(output_file_path):
            print(colored("NO OUTPUT FILE PRODUCED", "red", attrs=["bold"]))
            self.program.add_log_text("WARNING: NO OUTPUT FILE PRODUCED")
            self.program.dump_program_log_file()
            return 1

        if orig:
            self.program.set_output_result_path(output_file_path)
        else:
            self.program.set_single_query_result_path(output_file_path)
        self.program.add_log_text("Everything seems to be ok")
        self.program.dump_program_log_file()
        return 0


    def run_original(self, engine_options):
        self.program.add_log_text(" ================== ")
        self.program.add_log_text("  Running Original ")
        self.program.add_log_text(" ================== ")

        # copy the file to a union execution dict
        file_name = self.program.get_program_file_path().split("/")[-1]
        execution_file_path = os.path.join(self.execution_path, file_name)
        cp_command = "cp " + self.program.get_program_file_path() + " " + execution_file_path
        p = subprocess.Popen(cp_command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        print(cp_command)
        print(p.stderr.read().decode())
        
        self.path_to_engine = self.params["path_to_ddlog_engine"]
        signal = self.compile_datalog_into_rust(orig=True, program_file_path=execution_file_path)
        if signal != 0: return signal
        signal = self.compile_rust_into_an_executable(orig=True, program_file_path=execution_file_path)
        if signal != 0: return signal
        signal = self.run_ddlog_program(orig=True, program_file_path=execution_file_path)
        # shutil.rmtree(os.path.join(self.program.get_program_path(), "orig_rules_ddlog"))
        return signal


    def run_single_query(self, engine_options):
        self.program.add_log_text(" ====================== ")
        self.program.add_log_text("  Running Single Query ")
        self.program.add_log_text(" ====================== ")

        # copy the file to a union execution dict
        file_name = self.program.get_single_query_file_path().split("/")[-1]
        execution_file_path = os.path.join(self.execution_path, file_name)
        cp_command = "cp " + self.program.get_single_query_file_path() + " " + execution_file_path
        p = subprocess.Popen(cp_command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        print(cp_command)
        print(p.stderr.read().decode())

        self.path_to_engine = self.params["path_to_ddlog_engine"]
        signal = self.compile_datalog_into_rust(orig=False, program_file_path=execution_file_path)
        if signal != 0: return signal
        signal = self.compile_rust_into_an_executable(orig=False, program_file_path=execution_file_path)
        if signal != 0: return signal
        signal = self.run_ddlog_program(orig=False, program_file_path=execution_file_path)

        # shutil.rmtree(os.path.join(self.program.get_program_path(), "single_query_ddlog") )
        return signal