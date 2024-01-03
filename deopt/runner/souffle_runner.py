from deopt.runner.base_runner import BaseRunner
import subprocess
import os
from termcolor import colored


class SouffleRunner(BaseRunner):

    def generate_command(self, time_out, options, dl_file_path):
        command = "timeout -s SIGKILL " + str(time_out) + "s "
        command += self.path_to_engine
        command += " --fact-dir=" + self.program.get_program_path()
        command += " --output-dir=" + self.program.get_program_path()
        command += options
        command += " " + dl_file_path
        return command

    def run_original(self, engine_options):
        self.path_to_engine = self.params["path_to_souffle_engine"]
        
        command_line_options = " -w" + " " + engine_options
        
        # Compiler mode - path for temp CPP file
        if command_line_options.find("-c") != -1:
            command_line_options += " --generate=" + self.program.get_program_path() + "file.cpp"

        command = ""
        # if command_line_options.find("-p") != -1:
        if command_line_options == "-p":
            temp_command_line = self.generate_command(time_out=self.params["original_timeout"], options="", dl_file_path=self.program.get_program_file_path())
            command = temp_command_line + " -p profile.txt --emit-statistics && " + temp_command_line + " --auto-schedule=profile2 -o binary2 && ./binary2"
        else:
            command = self.generate_command(time_out=self.params["original_timeout"], options=command_line_options, dl_file_path=self.program.get_program_file_path())
        #print(command)
        self.program.add_log_text(" ================== ")
        self.program.add_log_text("  Running Original ")
        self.program.add_log_text(" ================== ")
        self.program.add_log_text("\tCommand: " + command)
        self.program.dump_program_log_file()

        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()

        self.program.add_log_text("\nSTANDARD ERROR: " + standard_error)
        self.program.add_log_text("\nSTANDARD OUTPUT: " + standard_output)
        self.program.dump_program_log_file()

        #print(colored(standard_error, "red", attrs=["bold"]))
        error_signal = self.process_standard_error(standard_error=standard_error, file_type="opt")

        self.program.add_log_text("ERROR SIGNAL: " + str(error_signal))
        
        if error_signal != 0:
            self.program.dump_program_log_file()
            return error_signal


        output_file_path = os.path.join(self.program.get_program_path(), self.program.get_output_relation_name() + ".csv")
        
        # Check if output file produced
        if not os.path.exists(output_file_path):
            print(colored("NO OUTPUT FILE PRODUCED", "red", attrs=["bold"]))
            self.program.add_log_text("WARNING: NO OUTPUT FILE PRODUCED")
            self.program.dump_program_log_file()
            self.program.statis.add_total_optimized_errors()
            return 1

        # rename original output file with orig.csv
        new_output_file_path = output_file_path.replace(self.program.get_output_relation_name()+".csv", "orig.facts")
        os.rename(output_file_path, new_output_file_path)
        self.program.set_output_result_path(new_output_file_path)
        self.program.add_log_text("Everything seems to be ok")
        self.program.dump_program_log_file()
        return 0
        

    def run_single_query(self, engine_options, output_relation_name):
        self.path_to_engine = self.params["path_to_souffle_engine"]
        command_line_options = " -w" + " " + engine_options
        
        # Compiler mode - path for temp CPP file
        if command_line_options.find("-c") != -1:
            command_line_options += " --generate=" + self.program.get_program_path() + "file.cpp"
        
        command = self.generate_command(time_out=self.params["single_query_timeout"], options=command_line_options, dl_file_path=self.program.get_single_query_file_path())
        #print(command)
        self.program.add_log_text(" ====================== ")
        self.program.add_log_text("  Running Single Query  ")
        self.program.add_log_text(" ====================== ")
        self.program.add_log_text("\tCommand: " + command)

        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        #print(colored(standard_error, "red", attrs=["bold"]))

        self.program.add_log_text("\n\tSTANDARD ERROR: " + standard_error)
        self.program.add_log_text("\n\tSTANDARD OUTPUT: " + standard_output)
        error_signal = self.process_standard_error(standard_error=standard_error, file_type="ref")

        self.program.add_log_text("\tSignal = " + str(error_signal))
        self.program.dump_program_log_file()

        if error_signal != 0:
            self.program.add_log_text(" XXX Something went wrong XXX")
            self.program.dump_program_log_file()
            return error_signal

        output_file_path = os.path.join(self.program.get_program_path(), output_relation_name + ".csv")

        # Check if output file produced
        if not os.path.exists(output_file_path):
            print(colored("NO OUTPUT FILE PRODUCED", "red", attrs=["bold"]))
            self.program.add_log_text(" ERROR. No output file produced !")
            self.program.dump_program_log_file()
            self.program.statis.add_total_reference_errors()
            return 1

        # rename original output file with orig.csv
        new_output_file_path = output_file_path.replace(output_relation_name + ".csv", "single_query.facts")
        os.rename(output_file_path, new_output_file_path)
        self.program.set_single_query_result_path(new_output_file_path)
        return 0


    def process_standard_error(self, standard_error, file_type):
        """
            OUTPUT COMMANDS:
                0 : OK
                1 : FATAL ERROR - This can cause the whole system to crash
                2 : RECOVERABLE ERROR - But we will record this. and possibly even the file.
                3 : DONT CARE - An error but we don't care about this
                4 : IGNORE IN SINGLE QUERY BUT CATCH IN WHOLE PROGRAM
        """
        # KEYWORDS
        if standard_error.find("Redefinition") != -1 or \
            standard_error.find("lxor") != -1 or \
            standard_error.find("lnot") != -1 or \
            standard_error.find("brie") != -1 or \
            standard_error.find("land") != -1 or \
            standard_error.find("bxor") != -1 or \
            standard_error.find("bnot") != -1 or \
            standard_error.find("mean") != -1 or \
            standard_error.find("bshr") != -1 or \
            standard_error.find("true") != -1 or \
            standard_error.find("band") != -1 or \
            standard_error.find("bshl") != -1:
            
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()

            return 3

        # TIMEOUT
        if standard_error.find("Killed") != -1:
            print(colored("TIMEOUT", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Timeout")

            if file_type == "opt":
                self.program.statis.add_total_optimized_timeouts()
            else:
                self.program.statis.add_total_reference_timeouts()

            return 3    # We don't care about this

        if standard_error.find("assertion") != -1 or standard_error.find("Assertion") != -1:
            if file_type == "opt":
                self.program.statis.add_total_optimized_assertion_failures()
            else:
                self.program.statis.add_total_reference_assertion_failures()

        # The following are assertion failure
        if standard_error.find("functor type not set") != -1:
            print(colored("KNOWN ASSERTION FAILURE", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: KNOWN ASSERTION FAILURE: functor type not set")
            return 3       # a bug we have reported, only occurs in whole program execution

        if standard_error.find("variable not grounded") != -1:
            print(colored("KNOWN ASSERTION FAILURE", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: KNOWN ASSERTION FAILURE: variable not grounded")
            return 3       # a bug we have reported, only occurs in whole program execution, this is the most occur assertion failure

        if standard_error.find("Requested arity not yet supported. Feel free to add it.") != -1:
            print(colored("KNOWN ASSERTION FAILURE", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: KNOWN ASSERTION FAILURE: -t none")
            return 3       # not a bug, but a feature of soufle in provenance

        if standard_error.find("relation not found") != -1:
            print(colored("KNOWN ASSERTION FAILURE", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: relation not found")
            return 3       # a bug that subsumption have not been supported in provenance system

        if standard_error.find("src/include/souffle/utility/MiscUtil.h:217") != -1:
            print(colored("KNOWN ASSERTION FAILURE", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: auto tuning assertion failure")
            return 3       # a bug in auto tuning we have report

        if standard_error.find("numeric constant type not set") != -1:
            print(colored("KNOWN ASSERTION FAILURE", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: numeric constant type not set")
            return 3       # a bug with inline we have reported

        if standard_error.find("Ignored execution plan for non-recursive clause in file") != -1:
            print(colored("KNOWN ERROR", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Ignored execution plan for non-recursive clause in file")
            return 3       # a bug with inline and query plan we have reported

        if standard_error.find("Invalid execution order in plan (expected") != -1:
            print(colored("KNOWN ERROR", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Invalid execution order in plan")
            return 3       # a bug with inline and query plan we have reported

        # ASSERTION FAILURE
        if standard_error.find("assertion") != -1 or standard_error.find("Assertion") != -1:
            if standard_error.find("ast2ram/ValueTranslator.cpp:52") != -1 or \
                    standard_error.find("ast/transform/MaterializeAggregationQueries.cpp:309") != -1 or \
                    standard_error.find("src/ast/transform/MaterializeAggregationQueries.cpp:311") != -1 or \
                    standard_error.find("src/ram/analysis/Relation.cpp:30") != -1:
                # Known assertion failure in souffle
                print(colored("KNOWN ASSERTION FAILURE", "red", attrs=["bold"]))
                self.program.add_log_text("\tError Type: Known assertion failure")   
                return 1 
            print(colored("ASSERTION FAILURE", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Assertion Failure")
            return 2

        # the following are crash
        if standard_error.find("syntax error") != -1:
            print(colored("SYNTAX ERROR", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: syntax error")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3

        if standard_error.find("Segmentation fault") != -1 or standard_error.find("segmentation fault") != -1:
            print(colored("SEGFAULT", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Segmentation fault")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3

        if standard_error.find("Error: Unable to stratify relation(s)") != -1:
            print(colored("Error: Unable to stratify relation(s)", "red", attrs=["bold"]))
            self.program.add_log_text("\tError: Unable to stratify relation(s)")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3

        # UNGROUNDED VARIABLE ERROR
        if standard_error.find("Error: Ungrounded variable") != -1:
            print(colored("Error: Ungrounded variable", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Error: Ungrounded variable")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3          # this means a variable not appears in any positive subgoal, we have found a bug about this.

        if standard_error.find("Floating-point arithmetic exception") != -1:
            print(colored("Floating-point arithmetic exception", "red", attrs=["bold"]))
            self.program.add_log_text("\tError : Floating-point arithmetic exception")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3          # A/0, A is a unsigned/number variable, ignore this, we have reported

        if standard_error.find("Unable to stratify") != -1:
            print(colored("unable to stratify error", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Unable to stratify")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 1

        if standard_error.find("Cannot inline cyclically dependent relations") != -1:
            print(colored("Cannot inline cyclically dependent relations", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Cannot inline cyclically dependent relations")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3    # We dont care about this

        if standard_error.find("Cannot inline negated relation which may introduce new variables") != -1:
            print(colored("KNOWN ERROR: inline negated", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Cannot inline negated relation which may introduce new variables")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3    # We dont care about this

        if standard_error.find("Cannot inline negated atom containing an unnamed variable unless the variable is within an aggregator") != -1:
            print(colored("KNOWN ERROR: inline negated", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Cannot inline negated atom containing an unnamed variable unless the variable is within an aggregator")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3    # We dont care about this

        if standard_error.find("Cannot inline relations that appear in aggregator") != -1:
            print(colored("KNOWN ERROR: inline relations in aggregator", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Cannot inline relations that appear in aggregator")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3    # We dont care about this

        # if standard_error.find("Argument in fact is not constant") != -1:
        #     print(colored("KNOWN ERROR: Not constant argument", "red", attrs=["bold"]))
        #     self.program.add_log_text("\tError Type: Argument in fact is not constant")
        #     return 3    # -nan/inf appear in fact

        if standard_error.find("Unable to deduce type for variable") != -1:
            print(colored("KNOWN ERROR: can not to deduce type", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Unable to deduce type for variable")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3    # type of fact is different from type of variable

        if standard_error.find("_Map_base::at") != -1:
            print(colored("KNOWN ERROR: _Map_base::at", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: _Map_base::at")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3    # This is a bug we have report

        if standard_error.find("Atom's argument type is not a subtype of its declared type") != -1:
            print(colored("KNOWN ERROR: error variable type", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: error variable type")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3    # We dont care about this

        if standard_error.find("terminate called after throwing an instance of 'std::out_of_range'") != -1:
            print(colored("terminate called after throwing an instance of 'std::out_of_range'", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: terminate called after throwing an instance of 'std::out_of_range'")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3    # A bug has been reported but not been fixed

        if standard_error.find("has one or more subsumptive rules and relational representation") != -1:
            print(colored("subsumption must be btree_delete", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: subsumption must be btree_delete")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3    # A syntax error

        if standard_error.find("Too long source line") != -1:
            print(colored("Too long source line", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Too long source line")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3    # Too long source line

        if standard_error.find("Pre-processors command failed with code 36096") != -1:
            print(colored("Pre-processors command failed with code 36096", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Pre-processors command failed with code 36096")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3    # Too long source line

        if standard_error.find("Undefined relation") != -1:
            print(colored("Undefined relation", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Undefined relation")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3    # The relation name is part of keywords

        if standard_error.find("Mismatching arity of relation") != -1:
            print(colored("Mismatching arity of relation", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Mismatching arity of relation")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 3    # Duplicate relation

        if standard_error.find("Error") != -1 or standard_error.find("error") != -1:
            print(colored("Some unknown error", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: UNKNOWN ERROR. Please investigate!")
            if file_type == "opt":
                self.program.statis.add_total_optimized_errors()
            else:
                self.program.statis.add_total_reference_errors()
            return 1

        # Seems like everything is OK 
        return 0
