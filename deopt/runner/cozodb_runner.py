from deopt.runner.base_runner import BaseRunner
import subprocess
import os
from termcolor import colored
from pycozo.client import Client
import pandas as pd

class CozoDBRunner(BaseRunner):

    def run_program(self, program, run_type, output_file_path):
        client = Client()

        try:
            r = client.run(program)
        except Exception as e:
            return self.process_standard_error(str(e), run_type), str(e)
        
        r = pd.DataFrame(r).values.tolist()
        f = open(output_file_path, 'w')
        for row in r:
            for i in range(len(row)):
                if str(row[i]) == "None":
                    row[i] = "null"
                elif str(row[i]) == "False":
                    row[i] = "false"
                elif str(row[i]) == "True":
                    row[i] = "true"
            row = [str(x) for x in row]
            f.write("\t".join(row) + "\n")
        f.close()

        return 0, str(r)


    def process_standard_error(self, standard_error, file_type):
        """
            OUTPUT COMMANDS:
                0 : OK
                1 : FATAL ERROR - This can cause the whole system to crash
                2 : RECOVERABLE ERROR - But we will record this. and possibly even the file.
                3 : DONT CARE - An error but we don't care about this
                4 : IGNORE IN SINGLE QUERY BUT CATCH IN WHOLE PROGRAM
        """
        # input relation can not appear in recursive query, we just ignore this error
        if standard_error.find("cannot have multiple definitions since it contains non-Horn clauses") != -1:
            print(colored("Input relation appear in recursive query", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Input relation appear in recursive query")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3

        # a bug
        # if standard_error.find("The query parser has encountered unexpected input / end of input at") != -1:
        #     print(colored("A known bug", "red", attrs=["bold"]))
        #     self.program.add_log_text("\tError Type: A known bug")
        #     if file_type == "opt":
        #         self.program.statis.add_total_optimized_errors()
        #     else:
        #         self.program.statis.add_total_reference_errors()
        #     return 3
        
        # this one is same with the before one
        # if standard_error.find("Encountered unsafe negation, or empty rule definition") != -1:
        #     print(colored("A known bug", "red", attrs=["bold"]))
        #     self.program.add_log_text("\tError Type: A known bug")
        #     if file_type == "opt":
        #         self.program.statis.add_total_optimized_errors()
        #     else:
        #         self.program.statis.add_total_reference_errors()
        #     return 3
        
        # duplicate head with different arity
        # if standard_error.find("has multiple definitions with conflicting heads") != -1:
        #     print(colored("Duplicate definition of relation", "red", attrs=["bold"]))
        #     self.program.add_log_text("\tError Type: Duplicate definition of relation")
        #     if file_type == "opt":
        #         self.program.statis.add_total_optimized_errors()
        #     else:
        #         self.program.statis.add_total_reference_errors()
        #     return 3
        
        # recursive query with negation
        if standard_error.find("Query is unstratifiable") != -1:
            print(colored("Recursive query with negation", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Recursive query with negation")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3
        
        # a bug won't be fixed
        if standard_error.find("Evaluation of expression failed") != -1:
            print(colored("Evaluation of expression failed", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Evaluation of expression failed")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3
        # Seems like everything is OK 
        return 1


    def run_single_query(self, program):
        
        self.program.add_log_text(" ====================== ")
        self.program.add_log_text("  Running Single Query  ")
        self.program.add_log_text(" ====================== ")

        output_file_path = os.path.join(self.program.get_program_path(), "single_query.facts")
        signal, res = self.run_program(program, "ref", output_file_path)

        self.program.add_log_text("\tSignal = " + str(signal))
        self.program.add_log_text("\n\tSTANDARD OUTPUT: " + str(res))
        self.program.dump_program_log_file()

        if signal != 0:
            self.program.add_log_text(" XXX Something went wrong XXX")
            self.program.dump_program_log_file()
            return signal

        # Check if output file produced
        if not os.path.exists(output_file_path):
            print(colored("NO OUTPUT FILE PRODUCED", "red", attrs=["bold"]))
            self.program.add_log_text(" ERROR. No output file produced !")
            self.program.dump_program_log_file()
            self.program.statis.add_total_reference_errors()
            return 1

        self.program.set_single_query_result_path(output_file_path)
        return 0
    
    def run_original(self, program):
        
        self.program.add_log_text(" ======================= ")
        self.program.add_log_text("  Running Original Query  ")
        self.program.add_log_text(" ======================= ")

        output_file_path = os.path.join(self.program.get_program_path(), "orig_query.facts")
        signal, res = self.run_program(program, "opt", output_file_path)

        self.program.add_log_text("\tSignal = " + str(signal))
        self.program.add_log_text("\n\tSTANDARD OUTPUT: " + res)
        self.program.dump_program_log_file()

        if signal != 0:
            self.program.add_log_text(" XXX Something went wrong XXX")
            self.program.dump_program_log_file()
            return signal

        # Check if output file produced
        if not os.path.exists(output_file_path):
            print(colored("NO OUTPUT FILE PRODUCED", "red", attrs=["bold"]))
            self.program.add_log_text(" ERROR. No output file produced !")
            self.program.dump_program_log_file()
            self.program.statis.add_total_reference_errors()
            return 1

        self.program.set_output_result_path(output_file_path)
        return 0