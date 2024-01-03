# Bugs found by queryFuzz

## Datalog engines building

Corresponding commit version of Datalog engines for each bug:

| #     | Datalog Engine | commit version | reported issue                                                     |
| ----- | --------------- | -------------- | ------------------------------------------------------------------ |
| bug1  | Souffle         | `4b6b17f`    | [`#1453`](https://github.com/souffle-lang/souffle/issues/1453)      |
| bug2  | Souffle         | `20d76ce`    | [`#1463`](https://github.com/souffle-lang/souffle/issues/1463)      |
| bug3  | Souffle         | `a9ac3cb`    | [`#1467`](https://github.com/souffle-lang/souffle/issues/1467)      |
| bug4  | Souffle         | `2995ff7`    | [`#1679`](https://github.com/souffle-lang/souffle/issues/1679)      |
| bug5  | Souffle         | `fbb4c4b`    | [`#1732`](https://github.com/souffle-lang/souffle/issues/1732)      |
| bug6  | Souffle         | `934f7e3`    | [`#1738`](https://github.com/souffle-lang/souffle/issues/1738)      |
| bug7  | Souffle         | `934f7e3`    | [`#1740`](https://github.com/souffle-lang/souffle/issues/1740)      |
| bug8  | Souffle         | `4bf6d1c`    | [`#1848`](https://github.com/souffle-lang/souffle/issues/1848)      |
| bug9  | μZ             | `6d427d9`    | [`#4844`](https://github.com/Z3Prover/z3/issues/4844)               |
| bug10 | μZ             | `7089610`    | [`#4870`](https://github.com/Z3Prover/z3/issues/4870)               |
| bug11 | μZ             | `fae9481`    | [`#4879`](https://github.com/Z3Prover/z3/issues/4879)               |
| bug12 | μZ             | `7fe8298`    | [`#4893`](https://github.com/Z3Prover/z3/issues/4893)               |
| bug13 | DDlog           | `5b1c9c1`    | [`#878`](https://github.com/vmware/differential-datalog/issues/878) |

The [Dockerfile](../../Dockerfile) in the root directory of deopt contains all source code of Souffle, Z3 (μZ), and DDlog. Build the docker image first.

For bugs of Souffle (bug1 - 8), enter the root directory of Souffle (/tmp/souffle in docker) and check out to the corresponding commit version, compile Souffle with the following command:

```
cd souffle
choutout $version
sh ./bootstrap
./configure
make
```

For bugs of μZ (bug9 - 12), enter the root dictory of Z3 (/tmp/z3 in docker) and checkout to the corresponding commit version, compile z3 with the following command:

```
cd z3
choutout $version
python3 scripts/mk_make.py
cd build
make -j
make install
```

For bug of DDlog, it can be triggered in the last version of DDlog.

## Bug reproduce

In each directory of bug, there is a bug-inducing test case named `bug.dl`, and corresponding reference programs `prefn.dl` and optimized programs `poptn.dl`, `n` indecates the iteration of test case generation.

We also provide the `supplementary_material.pdf` file in main directory to record the result of each step for reproduction.

### Souffle

For bugs of Souffle, you can run the command `souffle -F. -D. file_name.dl` to execute each file.

For bug2, this bug was only triggered when load input facts from input file, which needs `-F` option. As well as `--magic-transform=*` to allow the magic optimization. We put all input facts in its directory. You can directly execute each Datalog files with `souffle -D- --magic-transform=* -F.` `-D-` means to print the output to the command line.

Bug3 need to be triggered with `--disable-transformers=ResolveAliasesTransformer` option. You can execute all the files for this bug with this option.

Bug8 need to be triggered with `--disable-transformers=ResolveAliasesTransformer` option, this bug can not be detected by our test oracle. So you need to add/remove this option to produce different result.

Other bugs don't need any execution options.

### μZ

For bugs of μZ, you can directly run the command `z3 file_name.dl` to execute each file.

### DDlog

Bug13 is a bug found in DDlog, we provide a execution script `ddlog_run.sh` for this bug. Run the script with the following command. The file name is corresponding Datalog program file without suffix.

```
ddlog_run.sh file_name
```
