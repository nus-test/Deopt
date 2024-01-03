
from abc import ABC, abstractmethod

class BaseRunner(object):

    def __init__(self, params, program):
        self.params = params
        self.path_to_engine = None
        self.program = program
        self.clean_data = ""
        self.program_name = None

    @abstractmethod
    def run_original(self):
        pass

    @abstractmethod
    def run_single_query(self):
        pass

    @abstractmethod
    def process_standard_error(self):
        pass

    @abstractmethod
    def process_standard_output(self):
        pass


    @abstractmethod
    def compile_datalog_into_rust(self):
        pass

    @abstractmethod
    def compile_rust_into_an_executable(self):
        pass

    @abstractmethod
    def run_ddlog_program(self, orig):
        pass

    def set_program_name(self, name):
        self.program_name = name