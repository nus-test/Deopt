from termcolor import colored
import time

class MainArgumentParser(object):
    def __init__(self):
        self.parsed_arguments = dict()
        self.verbose = None
        self.engine = None
        self.cores = None

    def parse_arguments(self, parser):
        parser.add_argument("--verbose", nargs='?', const=True, default=False, help="Verbose mode")
        parser.add_argument("--cores", help="Number of cores")
        parser.add_argument("--engine", help="Data log engine to test")

        arguments = vars(parser.parse_args())
        self.verbose = arguments["verbose"]
        self.engine = arguments["engine"] if arguments["engine"] is not None else "souffle"
        self.cores = arguments["cores"]

    def get_arguments(self):
        self.parsed_arguments["verbose"] = self.verbose
        self.parsed_arguments["engine"] = self.engine
        self.parsed_arguments["cores"] = self.cores

        # Use Unix time as seed 
        self.parsed_arguments["seed"] = str(int(time.time()))
        # print arguments
        print("Parsed Arguments:")
        for key in sorted(self.parsed_arguments.keys()):
            print("\t" + colored(key, attrs=["bold"]) + " : " + colored(str(self.parsed_arguments[key]), "cyan", attrs=["bold"]))
        return self.parsed_arguments