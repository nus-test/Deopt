# Sensitivity Analysis & Efficiency

In this directory, `results` folder contains the statistics of all experiments (i.e. `statis.json`) of Section 5.2 and 5.3, as well as the configuration files (i.e. `params.json `). `data_analyzer.py` used to analysis the statistics of testing to generate the Figure 6 - 10 in our paper.

In `results` folder, the directory name indicates the crossponding configuration, in the directory of each configuration, the directory name indicates the value of this configuration. For example, `./results/max_att/70/` means the configuration `Max_{att}` with value `70`, under this directory, there is a config file for our tool `params.json`, and a statistic file for the execution of this experiment `statis.json`.

To execute `data_analyzer.py`, you need to install the necessary dependency with command: `pip3 install matplotlib numpy`. Execute `data_analyzer.py` from this directory, you will get the following results and a `result.pdf` which include the Figure 6 - 10 in our paper:

```
python3 data_analyzer.py
The results for Max_rules: 
execution time ratio for souffle: 
(5, 0.9057515813498641) (10, 1.1507676861266551) (20, 1.6347429594293095) (40, 2.6393253577166886) (60, 3.7318596499297154) (80, 4.852600426070166) (100, 6.119791217354439) 
reference program execution time percentage for souffle: 
(5, 0.7245814749348298) (10, 0.6839994610212473) (20, 0.6127681645416388) (40, 0.5007584871715605) (60, 0.4147357227113309) (80, 0.35069034476825417) (100, 0.30212929661119237) 
optimized program execution time percentage for souffle: 
(5, 0.27541852506517017) (10, 0.3160005389787527) (20, 0.3872318354583611) (40, 0.49924151282843954) (60, 0.585264277288669) (80, 0.6493096552317459) (100, 0.6978707033888076) 
execution time ratio for ddlog: 
(5, 1.0725291956701424) (10, 1.1666607206825208) (20, 1.262242841105534) (40, 1.5822140469618793) (60, 2.6354944016228643) (80, 2.7195156255665194) (100, 3.613117340537328) 
reference program execution time weight for ddlog: 
(5, 0.645700266033879) (10, 0.6804879852578759) (20, 0.5718245595833311) (40, 0.5842462118674555) (60, 0.43599714981743676) (80, 0.4138092780700251) (100, 0.3037125384867105) 
optimized program execution time weight for ddlog: 
(5, 0.354299733966121) (10, 0.3195120147421241) (20, 0.4281754404166689) (40, 0.41575378813254443) (60, 0.5640028501825632) (80, 0.5861907219299749) (100, 0.6962874615132895) 


The results for Max_att: 
number of rules in each test iteration: 
(1, 1.2868231474278757)(10, 73.94749498997996)(20, 96.12779464532156)(30, 98.71420422133485)(40, 99.63258785942492)(50, 99.82206613988879)(60, 99.92974720752498)(70, 99.98029411764706)
total test case number: 
(1, 946144)(10, 4990)(20, 3623)(30, 3506)(40, 3443)(50, 3417)(60, 3402)(70, 3400)


The results for P_empty: 
probability of optimized program with empty results: 
(0, 0.0) (20, 0.3593763676148797) (40, 0.680870265914585) (60, 0.8360516795865633) (80, 0.8952472736495054) (100, 0.927251714503429) 
probability of final test case in each test iteration with empty results: 
(0, 0.0) (20, 0.3990700218818381) (40, 0.765511684125705) (60, 0.9111111111111111) (80, 0.9520669540958661) (100, 0.9766319532639065) 
total test iterations number: 
(0, 3593)(20, 3656)(40, 3723)(60, 3870)(80, 3943)(100, 3937)


The results for P_head:
average cycle number for each test case: 
(0, 0.0) (2, 0.8320337881741391) (4, 2.7260900140646975) (6, 6.932001536688436) (8, 19.06288209606987) (10, 112.57482014388489) 
average cycle length for each circle: 
(0, 0) (2, 3.360796563842249) (4, 4.381787695085773) (6, 6.041010862336511) (8, 7.877926421404682) (10, 11.072897960748726) 


The results for Max_iter: 
average circle number for each test case: 
(10, 0.4552819183408944) (50, 0.8158415841584158) (100, 0.8320337881741391) (200, 0.9128838451268364) (300, 1.016474464579901) 
average circle length for each circle: 
(10, 2.3437722419928826) (50, 3.2091423948220066) (100, 3.360796563842249) (200, 3.3952468007312615) (300, 4.436628849270664) 


The results for comparing with random test case generation: 
souffle inc total: 
(20, 32280) (40, 12932) (60, 7190) (80, 4535) 
souffle inc valid: 
(20, 32280) (40, 12932) (60, 7190) (80, 4535) 
souffle inc non-empty: 
(20, 27511) (40, 11008) (60, 6110) (80, 3901) 
souffle random total: 
(20, 79284) (40, 43503) (60, 31309) (80, 25025) 
souffle random valid: 
(20, 37479) (40, 10647) (60, 4412) (80, 2125) 
souffle random non-empty: 
(20, 3738) (40, 658) (60, 197) (80, 89) 
ddlog inc total: 
(20, 42) (40, 16) (60, 8) (80, 7) 
ddlog inc valid: 
(20, 42) (40, 16) (60, 8) (80, 7) 
ddlog inc non-empty: 
(20, 37) (40, 14) (60, 7) (80, 7) 
ddlog random total: 
(20, 398) (40, 216) (60, 157) (80, 140) 
ddlog random valid: 
(20, 349) (40, 168) (60, 112) (80, 78) 
ddlog random non-empty: 
(20, 54) (40, 20) (60, 6) (80, 5)
```

In each bracket, the first number represents the value of the corresponding configuration, and the second number represents the result. This data is used to draw the Figures in our paper.

## Reproduce the result of each configuration

To generate the Figure 6 - 10, you can directly execute the command `python3 data_analyzer.py`, then there is a file named `result.pdf` generated in this folder, which contains all of Figure 6 - 10.

To reproduce the single results in the `./results` folder, you can copy the corresponding configuration file `params.json` to the root directory of Deopt, then run the command `python3 deopt/__main__.py` for Souffle (or `python3 deopt/__main__.py --engine=ddlog` for DDlog), each experiment will run for 24 hours. When the experiment is completed, you can see the `statis.json` file in the `temp/core_0/` directory, which is the result of this experiment.

We also provide a script `run.py` to reproduce the whole experiment. You should first build the docker [deopt](../../Dockerfile). Then copy the `run.py` to the same directory of deopt and run the command `python3 run.py`. In our experiment, we presented a total of 50 different configurations, each requiring 24 hours to run. If only one thread is used, it would take 50*24 hours in total. We have provided options to run these experiments concurrently. You can execute the command `python3 run.py 8` to specify using 8 threads for concurrent execution. If this configuration is not specified, the default is to run 4 threads concurrently. The `run.py` will automatically execute `data_analyzer.py` to generate the Figures and generate a `result.pdf` file in the same directory.
