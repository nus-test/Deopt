# Bugs found by Deopt

## Detailed information of logic bugs

Corresponding commit version of Datalog engines for each bug:

| #     | Datalog Engine | commit version       | bug report link                                                                                         | bug status  |
| ----- | -------------- | --------------------- | ------------------------------------------------------------------------------------------------------- | ----------- |
| bug1  | Souffle        | `3cd802d`           | [https://github.com/souffle-lang/souffle/issues/2311](https://github.com/souffle-lang/souffle/issues/2311) | confirmed   |
| bug2  | Souffle        | `3cd802d`           | [https://github.com/souffle-lang/souffle/issues/2375](https://github.com/souffle-lang/souffle/issues/2375) | unconfirmed |
| bug3  | Souffle        | `29c5921`           | [https://github.com/souffle-lang/souffle/issues/2322](https://github.com/souffle-lang/souffle/issues/2322) | confirmed   |
| bug4  | Souffle        | `29c5921`           | [https://github.com/souffle-lang/souffle/issues/2323](https://github.com/souffle-lang/souffle/issues/2323) | unconfirmed |
| bug5  | Souffle        | `29c5921`           | [https://github.com/souffle-lang/souffle/issues/2327](https://github.com/souffle-lang/souffle/issues/2327) | unconfirmed |
| bug6  | Souffle        | `29c5921`           | [https://github.com/souffle-lang/souffle/issues/2337](https://github.com/souffle-lang/souffle/issues/2337) | unconfirmed |
| bug7  | Souffle        | `29c5921`           | [https://github.com/souffle-lang/souffle/issues/2343](https://github.com/souffle-lang/souffle/issues/2343) | unconfirmed |
| bug8  | Souffle        | `3cd802d`           | [https://github.com/souffle-lang/souffle/issues/2385](https://github.com/souffle-lang/souffle/issues/2385) | unconfirmed |
| bug9  | Souffle        | `29c5921`           | [https://github.com/souffle-lang/souffle/issues/2382](https://github.com/souffle-lang/souffle/issues/2382) | unconfirmed |
| bug10 | μZ            | `cbc5b1f`           | [https://github.com/Z3Prover/z3/issues/6446](https://github.com/Z3Prover/z3/issues/6446)                   | fixed       |
| bug11 | μZ            | `cbc5b1f`           | [https://github.com/Z3Prover/z3/issues/6447](https://github.com/Z3Prover/z3/issues/6447)                   | confirmed   |
| bug12 | CozoDB         | release version 0.7.0 | [https://github.com/cozodb/cozo/issues/101](https://github.com/cozodb/cozo/issues/101)                     | fixed       |
| bug13 | CozoDB         | release version 0.7.0 | [https://github.com/cozodb/cozo/issues/122](https://github.com/cozodb/cozo/issues/122)                     | confirmed   |

The [Dockerfile](../../Dockerfile) in the root directory of deopt will contains all source code of Souffle, Z3 (μZ), and DDlog. Build the docker image first.

For bugs of Souffle (bug1 - bug9), enter the root directory of Souffle (/tmp/souffle in docker) and check out to the corresponding commit version, compile Souffle with command shown in [here](https://souffle-lang.github.io/build), or follow the command shown in [Dockerfile](../../Dockerfile).

For bugs of μZ (bug10 and bug11), enter the root dictory of Z3 (/tmp/z3 in docker) and checkout to the corresponding commit version, compile z3 with command shown in [here](https://github.com/Z3Prover/z3#build-status), or follow the command shown in [Dockerfile](../../Dockerfile).

For bugs of CozoDB, I use the python driver to run the program, which can be found at [pycozo](https://github.com/cozodb/pycozo).

### Logic bug reproduce

For bug1-6, 9-11, in each directory of these bugs, there is a bug-inducing test case named `bug.dl`, and corresponding reference programs `prefn.dl` and optimized programs `poptn.dl`, `n` indicates the iteration of test case generation. You can directly execute these files with `souffle -D- file_name.dl` for Souffle bugs (`-D-` means to print the output to the command line.) or `z3 file_name.dl` for μZ bugs. All of these bugs don't need additional execution options.

For bug7 and bug8, there is only `bug.dl` in their directory, as these two bugs were triggered by different execution options. Bug7 only occurred in synthesizer mode, which need `-c` in execution options. The execution will produce different result when remove `-c` option. Bug8 needs `-t none --disable-transformers=ExpandEqrelsTransformer`, and can produce different result when remove `-t none`.

We also provide the `supplementary_material.pdf` file in main directory to record the result of each step for reproduction.

## Detailed information of other bugs

| #     | Datalog Engine | commit version       | bug report link                                                                                         | bug status  |
| ----- | -------------- | --------------------- | ------------------------------------------------------------------------------------------------------- | ----------- |
| bug1  | Souffle        | `3cd802d`           | [https://github.com/souffle-lang/souffle/issues/2318](https://github.com/souffle-lang/souffle/issues/2318) | unconfirmed |
| bug2  | Souffle        | `3cd802d`           | [https://github.com/souffle-lang/souffle/issues/2320](https://github.com/souffle-lang/souffle/issues/2320) | confirmed   |
| bug3  | Souffle        | `3cd802d`           | [https://github.com/souffle-lang/souffle/issues/2321](https://github.com/souffle-lang/souffle/issues/2321) | confirmed   |
| bug4  | Souffle        | `3cd802d`           | [https://github.com/souffle-lang/souffle/issues/2324](https://github.com/souffle-lang/souffle/issues/2324) | confirmed   |
| bug5  | Souffle        | `3cd802d`           | [https://github.com/souffle-lang/souffle/issues/2326](https://github.com/souffle-lang/souffle/issues/2326) | confirmed   |
| bug6  | Souffle        | `29c5921`           | [https://github.com/souffle-lang/souffle/issues/2338](https://github.com/souffle-lang/souffle/issues/2338) | unconfirmed |
| bug7  | Souffle        | `29c5921`           | [https://github.com/souffle-lang/souffle/issues/2339](https://github.com/souffle-lang/souffle/issues/2339) | unconfirmed |
| bug8  | Souffle        | `29c5921`           | [https://github.com/souffle-lang/souffle/issues/2340](https://github.com/souffle-lang/souffle/issues/2340) | confirmed   |
| bug9  | Souffle        | `29c5921`           | [https://github.com/souffle-lang/souffle/issues/2346](https://github.com/souffle-lang/souffle/issues/2346) | fixed       |
| bug10 | Souffle        | `1fc233d`           | [https://github.com/souffle-lang/souffle/issues/2351](https://github.com/souffle-lang/souffle/issues/2351) | fixed       |
| bug11 | Souffle        | `15b114a`           | [https://github.com/souffle-lang/souffle/issues/2355](https://github.com/souffle-lang/souffle/issues/2355) | confirmed   |
| bug12 | Souffle        | `b8b1d69`           | [https://github.com/souffle-lang/souffle/issues/2369](https://github.com/souffle-lang/souffle/issues/2369) | unconfirmed |
| bug13 | Souffle        | `3cd802d`           | [https://github.com/souffle-lang/souffle/issues/2379](https://github.com/souffle-lang/souffle/issues/2379) | confirmed   |
| bug14 | Souffle        | `0ad4109`           | [https://github.com/souffle-lang/souffle/issues/2426](https://github.com/souffle-lang/souffle/issues/2426) | confirmed   |
| bug15 | CozoDB         | release version 0.7.0 | [https://github.com/cozodb/cozo/issues/97](https://github.com/cozodb/cozo/issues/97)                       | fixed       |
| bug16 | CozoDB         | release version 0.7.0 | [https://github.com/cozodb/cozo/issues/99](https://github.com/cozodb/cozo/issues/99)                       | fixed       |
| bug17 | CozoDB         | release version 0.7.0 | [https://github.com/cozodb/cozo/issues/113](https://github.com/cozodb/cozo/issues/113)                     | confirmed   |
