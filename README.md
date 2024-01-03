# Deopt

Datalog Engines OPtimization Tester.

# Getting Start

## Docker

Build the docker file and run Soufflé testing in docker.

```
cd deopt
docker build -t deopt ./
docker run -ti --rm -v $PWD:/tmp/deopt deopt /bin/bash -c "cd deopt; python3 deopt/__main__.py"
```

This Dockerfile will automatically install latest version of source code of Soufflé, z3, DDlog, and latest release version of CozoDB. The default command of DDlog will build DDlog from source code, but for use in China, VPN is needed for using [stack](https://docs.haskellstack.org/en/stable/install_and_upgrade/#china-based-users), we also provide the command in line 47 - 58 to install the latest release version of DDlog, which doesn't need stack.

# Step-by-step

## Testing `Soufflé`

You can immediately start testing `Soufflé` by just typing the following command:

```
docker run --rm -it -v $PWD:/tmp/deopt deopt /bin/bash
cd deopt
python3 deopt/__main__.py
```

The deopt docker file has installed the latest revision of `Soufflé`.

If you want to test a different version of `Soufflé`, please build and install that version
and paste the path to `Soufflé` executable in the `path_to_souffle_engine` field in file
`/path/to/deopt/params.json`, which is generated from `/path/to/deopt/deopt/default_params.json`.

You can also run the following command outside the docker:

```
docker run -ti --rm -v $PWD:/tmp/deopt deopt /bin/bash -c "cd deopt; python3 deopt/__main__.py"
```

After the running process is halted, a `temp\core_0` folder will be generated. This folder contains the test cases that may potentially trigger a bug.
In each `program_N` folder (`N` is the number of current test case), `orig_rules.dl` file contains the optimized program; `single_query.dl` contains a single reference program; `orig_query.facts` contains the results of the optimized program; `single_query.facts` contains the results of the reference program; `orig.log` contains the log of this test iteration.

## Testing CozoDB, DDlog and μZ

The deopt docker file has installed the latest revision of `CozoDB`,  `DDlog `and `z3`.

For `CozoDB`, you can execute the following command:

```
python3 deopt/__main__.py --engine=cozodb
```

For `DDlog`, you can execute the following command:

```
python3 deopt/__main__.py --engine=ddlog
```

For `μZ`, you can execute the following command:

```
python3 deopt/__main__.py --engine=z3
```

## Configurations in `params.json`

| Configuration name                         | Description                                                                                                                                                                                   |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| execution_mode                             | The mode of Deopt. Options:`fuzzing` used to run testing with IRE; `evaluation` run testing but ignore all bug reports; `random` used to run testing with randomly generated test cases |
| path_to_souffle_engine                     | The path of Soufflé                                                                                                                                                                          |
| path_to_ddlog_engine                       | The path of DDlog                                                                                                                                                                             |
| path_to_z3_engine                          | The path of z3                                                                                                                                                                                |
| max_number_rules                           | The maximum number of rules to be generated in a test case. Should bigger than 0.                                                                                                             |
| max_number_of_attempts_for_rule_generation | The maximum number of attempts to generate a new rule if the current rule produces an empty result or results in a semantic error. Should bigger than 0                                       |
| probability_of_empty_result_rule           | Probability to allow empty results for a rule. Should bigger than or equal to 0 and less than or equal to 1.                                                                                  |
| probability_of_recursive_rule              | Probability of choosing an existing relation as head. Should bigger than or equal to 0 and less than or equal to 1.                                                                          |
| max_iterations_for_recursive_query         | Max iterations for recursions. Should bigger than 0.                                                                                                                                          |

# File structure

```

.
├── Dockerfile
├── README.md
├── supplementary_material.pdf # More detailed information about bugs found by deopt and queryFuzz.
├── deopt
│   ├── __init__.py
│   ├── __main__.py
│   ├── datalog               # Basic class for Datalog engines, including the basic algorithm
│   ├── default_params.json   # Default parameters for deopt
│   ├── engines               # Rules generator for different engines
│   │   ├── __init__.py
│   │   ├── cozodb
│   │   ├── ddlog
│   │   ├── souffle
│   │   └── z3
│   ├── home.py
│   ├── parsers
│   ├── runner                # Files used to execute the Datalog program for engines
│   └── utils
└── evaluation
    ├── Q1                    # Contains reference and optimized programs for bugs found by deopt 
    ├── Q2Q3                  # Contains the configuration file and results for sensitivity analysis and efficiency evaluation
    └── Q4                    # Contains reference and optimized programs for bugs found by queryFuzz
```

# Reproduce the evaluation

In each folder within the `evaluation` directory, we provide a detailed `README` explaining how to reproduce our experiments.

For effectiveness evaluation, we provide a [README](./evaluation/Q1/README.md) file to show all of the bug reports. We also provide the bug-inudcing test cases (including the optimized and reference programs) for each logic bug. The `supplementary_material.pdf` file provide the results of each optimized and reference program.

For sensitivity analysis and efficiency evaluation, you can copy the [run.py](./evaluation/Q2Q3/run.py) to the same directory of deopt and install the necessary dependency `pip3 install matplotlib numpy`, then run `python3 run.py`, which will automatically execute all of the experiments and generate the Figure 6 - 10 in our paper. We provide the detailed information in [README](./evaluation/Q2Q3/README.md).
