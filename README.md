# Cost-Effective Empirical Performance Modeling with Extra-P using Gaussian Process Regression (GPR)

Evaluation code for the paper "Cost-Effective Empirical Performance Modeling." This repository contains the code that was used to run the synthetic analysis and the case study analysis to study Extra-P's accuracy, predictive power, budget usage/modeling cost, and number of used measurement points when using different measurement point selection strategies. The evaluated strategies are: Cheapest Point First (CPF), measurement point prediction via Gaussian Process Regression (GPR), and Hybrid (a combination of the CPF+GPR strategy). The code in this repository can be used to reproduce the results and plots.

## Quick setup using Docker

For a quick setup of the evaluation environment, we provide a Dockerfile that can be used to build an image that has all dependencies installed to run the evaluation scripts. The Dockerfile also downloads the required performance measurement dataset automatically.

Steps: 

1. Build a docker image from the provided Dockerfile: `docker build -t extrap-gpr .`
2. Run the image in a container: `docker run -it extrap-gpr /bin/bash`
3. Run the analysis scripts inside the Docker container.

NOTE: Building the image from the Dockerfile might take several minutes to half an hour as many dependencies have to be installed including tex to generate the plots, the datasets, Extra-P, pycubexr, ...

NOTE: Ideally you do the manual setup and run the analysis scripts on a HPC system in parallel. The analysis, especially for the case studies and synthetic evaluation runs with 4 parameters and large number of evaluation functions are very slow when run in serial and might take days to finish one config.

### Reproduction of the Evaluation & Case Study results using Docker

xxx

## Performance measurement dataset

To run and reproduce the results for each benchmark, one first needs to obtain the performance measurements that were conducted by us for the evaluation. The performance measurement datasets can be found and downloaded at: [Datasets](https://zenodo.org/records/10085298?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImJlZTI0ZGJhLTExZTktNDFhMi04ZGNjLTBjOTcxOTFiZGRkYSIsImRhdGEiOnt9LCJyYW5kb20iOiI2OWFkMjQyNmVmZGQwMmE2OWYwY2E5YmFlOWQ0OTAyMyJ9.43J0zSoKDZTC6aOI8xLqNP2fIf-AFV4DNvW3AvpW2aHLbz8Rjeq-bvVst2y7WCJY1hcJMkB8wDtB-92hhZh8zA). There is one .tar.gz file for each benchmark. Download and then unpack them.

## Extra-P installation

The code in this repository uses a specific version of Extra-P for the analysis. If not using the provided Dockerfile you have to build this version of Extra-P from source. This specific version of Extra-P can be found at [Extra-P](https://zenodo.org/records/10086772?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImI4ZmMwMjVjLWZkMTEtNGJkMy04NTQwLTBhZWYwYjc1ZDc3YiIsImRhdGEiOnt9LCJyYW5kb20iOiJmNTdiYmEzODc2YTc1Nzg0NjU3NTQwM2I2MTE4ZGFjMSJ9.ZKA8J_7Ejj9GtfaI0M3B50N-6aKwnzvYOk61QtYggdPl47B-7iPEu-6Qq0bTrBSckDcg7afh2XeyjioU3jVl4w). You can do this by following the below steps.

Steps:

1. download the `.zip` file at [Extra-P](https://zenodo.org/records/10086772?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImI4ZmMwMjVjLWZkMTEtNGJkMy04NTQwLTBhZWYwYjc1ZDc3YiIsImRhdGEiOnt9LCJyYW5kb20iOiJmNTdiYmEzODc2YTc1Nzg0NjU3NTQwM2I2MTE4ZGFjMSJ9.ZKA8J_7Ejj9GtfaI0M3B50N-6aKwnzvYOk61QtYggdPl47B-7iPEu-6Qq0bTrBSckDcg7afh2XeyjioU3jVl4w)
2. unzip the downloaded file `unzip extrap.zip -d extrap`
3. `pip install -e extrap/extrap-vNext/`

After installation add extrap in user installation to path if necessary: `export PATH="$HOME/.local/bin:$PATH"`.

If you do not use the Dockerfile for the quick setup you have to install other python packages that are used by the analysis codes in this repo on the fly, e.g., scipy, pandas, if you do not have them installed already.

## pyCubexR installation

The code in this repository uses a specific version of pyCubexR for the analysis. This software is used by Extra-P to read in files in the Cube4 format. If not using the provided Dockerfile you have to build this version of pyCubexR from source. The specific version of pyCubexR is available at [pyCubexR](https://zenodo.org/records/10092353?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6IjczNzY4Njg1LTQ2NDAtNGFhOC05ZGU1LWU3OGU1YmQ0ZWY3ZiIsImRhdGEiOnt9LCJyYW5kb20iOiI4Y2MwMzc5MzQxOTJlZjkwMzllMWZkMDUwMzlmMjdlNSJ9.4r0-tpFyYPOttuUlZkMglPgNS21oqR_AvXpyMRPJuSlr5ZJ-S28MtmcmQUGm7aujNKyDiypwPl8t7qqwNuk_Dw). You can do this by following the below steps.

Steps:

1. download the `.zip` file at [pyCubexR](https://zenodo.org/records/10092353?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6IjczNzY4Njg1LTQ2NDAtNGFhOC05ZGU1LWU3OGU1YmQ0ZWY3ZiIsImRhdGEiOnt9LCJyYW5kb20iOiI4Y2MwMzc5MzQxOTJlZjkwMzllMWZkMDUwMzlmMjdlNSJ9.4r0-tpFyYPOttuUlZkMglPgNS21oqR_AvXpyMRPJuSlr5ZJ-S28MtmcmQUGm7aujNKyDiypwPl8t7qqwNuk_Dw)
2. unzip the downloaded file `unzip pycubexr-master.zip -d pycubexr`
3. `pip install -e pycubexr/pycubexr-master/`

## Manual setup

* install pip package dependencies `pip install sympy,scikit-learn,natsort,pandas`
* install latex (used for plotting) `sudo apt-get install -y texlive-latex-extra`
* https://zenodo.org/records/10092353?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6IjczNzY4Njg1LTQ2NDAtNGFhOC05ZGU1LWU3OGU1YmQ0ZWY3ZiIsImRhdGEiOnt9LCJyYW5kb20iOiI4Y2MwMzc5MzQxOTJlZjkwMzllMWZkMDUwMzlmMjdlNSJ9.4r0-tpFyYPOttuUlZkMglPgNS21oqR_AvXpyMRPJuSlr5ZJ-S28MtmcmQUGm7aujNKyDiypwPl8t7qqwNuk_Dw

### Reproduction of the Evaluation & Case Study results using Manual Setup

To recreate the evaluation and case study results using the manual setup follow the instructions in the following sections.

#### Case Studies

Using the following commands and provided scripts one can reproduce the results shown in the paper. For all case studies, besides RELEARN, the path to the data needs to be changed, depending on to which directory you unpacked/downloaded the datasets.
The `./run_analysis.sh` and `./process.sh` scripts are build for usage on a Cluster or HPC system. The parallelize the analysis process using jobs to speed it up.

##### RELEARN:

1. `cd relearn`
2. (single run) `python ../case_study.py --text relearn_data.txt --processes 0 --parameters "p","n" --eval_point "512","9000" --filter 1 --budget 100 --plot True --normalization True --grid-search 3 --base-values 1 --hybrid-switch 20 --repetition 2`
3. `./run_analysis.sh`
4. `./process.sh`
5. `./archive.sh filtered`
6. `python single_plot.py --path filtered/analysis_results/ --name results_filtered --reps 2 --min 9 --filter 1`
7. `python budget_usage_plot.py --path filtered/analysis_results/ --name budget_usage --reps 2 --min 9`

Use `--min 9` for filtered run with `>1%` runtime kernels. Use `--min 13` for run with all available kernels.

##### LULESH:

1. `cd lulesh/lichtenberg`
2. (single run) `python ../../case_study.py --cube /work/scratch/mr52jiti/data/lulesh/ --processes 0 --parameters "p","s" --eval_point "1000","35" --filter 1 --budget 100 --plot True --normalization True --grid-search 3 --base-values 2 --hybrid-switch 20 --repetition 5`
3. `./run_analysis.sh`
4. `./process.sh`
5. `./archive.sh filtered`
6. `python single_plot.py --path filtered/analysis_results/ --name results_filtered --reps 5`
7. `python budget_usage_plot.py --path filtered/analysis_results/ --name budget_usage_filtered --reps 5`

##### MiniFE:

1. `cd minife/lichtenberg`
2. (single run) `python ../../case_study.py --cube /work/scratch/mr52jiti/data/minife/ --processes 0 --parameters "p","n" --eval_point "2048","350" --filter 1 --budget 100 --plot True --normalization True --grid-search 3 --base-values 2 --hybrid-switch 20 --repetition 5`
3. `./run_analysis.sh`
4. `./process.sh`
5. `./archive.sh filtered`
6. `python single_plot.py --path filtered/analysis_results/ --name results_filtered --reps 5`
7. `python budget_usage_plot.py --path filtered/analysis_results/ --name budget_usage_filtered --reps 5`

##### FASTEST:

1. `cd fastest`
2. (single run) `python ../case_study.py --cube /work/scratch/mr52jiti/data/fastest/ --processes 0 --parameters "p","size" --eval_point "512","65536" --filter 1 --budget 100 --plot True --normalization True --grid-search 3 --base-values 2 --hybrid-switch 20 --repetition 5`
3. `./run_analysis.sh`
4. `./process.sh`
5. `./archive.sh filtered`
6. `python single_plot.py --path filtered/analysis_results/ --name results_filtered --reps 5`
7. `python budget_usage_plot.py --path filtered/analysis_results/ --name budget_usage_filtered --reps 5`

##### Kripke:

1. `cd kripke`
2. (single run) `python ../case_study.py --cube /work/scratch/mr52jiti/data/kripke/ --processes 0 --parameters "p","d","g" --eval_point "32768","12","160" --filter 1 --budget 100 --plot True --normalization True --grid-search 3 --base-values 2 --hybrid-switch 20 --repetition 5`
3. `./run_analysis.sh`
4. `./process.sh`
5. `./archive.sh filtered`
6. `python single_plot.py --path filtered/analysis_results/ --name results_filtered --reps 5`
7. `python budget_usage_plot.py --path filtered/analysis_results/ --name budget_usage_filtered --reps 5`

##### Quicksilver:

1. `cd quicksilver`
2. (single run) `python ../../case_study.py --cube /work/scratch/mr52jiti/data/quicksilver/ --processes 0 --parameters "p","m","n" --eval_point "512","20","60" --filter 1 --budget 100 --plot True --normalization True --grid-search 3 --base-values 2 --hybrid-switch 20 --repetition 5`
3. `./run_analysis.sh`
4. `./process.sh`
5. `./archive.sh filtered`
6. `python single_plot.py --path filtered/analysis_results/ --name results_filtered --reps 5`
7. `python budget_usage_plot.py --path filtered/analysis_results/ --name budget_usage_filtered --reps 5`

To check the number of measurements `ls /work/scratch/mr52jiti/data/quicksilver/ | wc -l`.
Some of the measurements did not run successfully. See with `ls *.er /work/scratch/mr52jiti/data/quicksilver/quicksilver.p*/profile.cubex | wc -l` the ones that actually have a profile.cubex.

#### Create analysis plot for all case studies

After completing the analysis for all of the above case studies you can follow the below steps to recreate the plots containing the results for all case studies.

Steps:

1. `python paper_plot_case_studies.py`

#### Noise analysis for the case studies

To reproduce the noise analysis plot for the case studies use the analysis script provided.

`./analyze_noise.sh`

It will run the noise analysis for each case study and then plot all of the data into a single plot in put everything into a folder `noise_analysis/`.

For individual runs use:

* RELEARN: `python noise_analysis.py --text relearn/relearn_data.txt --total-runtime 31978.682999999997 --name relearn`
* LULESH: `python noise_analysis.py --cube /work/scratch/mr52jiti/data/lulesh/ --name lulesh`
* FASTEST: `python noise_analysis.py --cube /work/scratch/mr52jiti/data/fastest/ --name fastest`
* KRIPKE: `python noise_analysis.py --cube /work/scratch/mr52jiti/data/kripke/ --name kripke`
* MiniFE: `python noise_analysis.py --cube /work/scratch/mr52jiti/data/minife/ --name minife`
* Quicksilver: `python noise_analysis.py --cube /work/scratch/mr52jiti/data/quicksilver/ --name quicksilver`

## Run the evaluation tool for the synthetic evaluation:

Navigate to the folder, the analysis you want to reproduce, e.g., `cd 2_parameters/1_noise/`.

1. `./run_analysis.sh` to run the analysis in parallel on a cluster.
2. `./process.sh` to run the postprocessing after all jobs have finished.
3. `./archive.sh <folder_name>` archive all of the result data into the given foldername.
4. `python single_plot.py --path <folder_name>/analysis_results/ --name results_<folder_name> --reps 4` create a result plot using the data found in the archived experiment folder. 
5. `python budget_usage_plot.py --path final/analysis_results/ --name budget_usage --reps 4` to run the budget analysis. Shows you how efficiently the different point selection strategies utilize the available budgets.

Basic usage for single runs: `python synthetic_evaluation.py --nr-parameters 2 --nr-functions 100 --nr-repetitions 4 --noise 1 --mode budget --budget 10 --plot True --normalization True --grid-search 3 --base-values 2`

Use `--nr-parameters <nr_params>` to set the number of model parameters considered for the evaluation.
Use `--noise <noise_percent>` to set the artificially induced noise (+-) into the measurements in %.
Use `--nr-functions <nr_functions>` the number of synthetically generated functions to run the evalutation for.

Leave all other parameters as is. There values have been carefully selected doing a grid search for the best configurations for all supported number of model parameters and noise levels.


## Quick Introduction of the Measurement Point Selection Strategies

### CPF (Cheapest Points First) Strategy

1. Measure the cheapest available lines of five points per
parameter. Use these points to create a first model using
the sparse modeling technique.
1b. Take at least one additional point not on this axis per dimension, model parameter.
base_points + (nr_dimensions - 1)
2. Perform an additional measurement, starting from the
cheapest ones available. Using the model previously determined,
one can assess if the quality of the model is
sufficient (by comparing the accuracy metrics of the two models on the points used for modeling) or if additional points are required. Or until no more modeling budget is available.
3. Recreate the model using all available points.
4. If the quality of the model evaluated in step 2 is insufficient,
return to step 2. (or if there is more budget available for modeling...)

This strategy always uses 4 repetitions per measurement point. In the previous paper we found that our results showed that 4 repetitions are optimal. 

### GPR (Gaussian Progress Regression) Strategy

1. Measure the cheapest available lines of five points per
parameter. Use these points to create a first model using
the sparse modeling technique. 
1b. Take at least one additional point not on this axis per dimension, model parameter.
base_points + (nr_dimensions - 1)
2. Use these points as input to the GPR.
2b. The noise level on these points is estimated in % divergence from the 
arithmetic mean and then used as input value for a WhiteKernel() that is added to the GPR Matern CovVariance() function.
3. Train the GPR.
4. Suggest a new point using the trained GPR.
5. Take this measurement and add it to the experiment. Create a new model.
6. Add the new point to the GPR. Train the GPR again.
7. Continue this process until budget for modeling is exhausted. Steps: 4-6.

The GPR strategy can if specified start using less repetitions for the basic lines of points (the minimal measurement point set), e.g., only 2 instead of 4, compared to the CPF strategy.
Enabling this feature gives the best results, as it provides the most freedom to the GPR strategy to choose from a larger set of points, gives it more flexibility.
Furthermore the GPR strategy, considers the number of repetitions of a measurement point. This means it always selects 1 repetitions at a time, compared to the 4 of the CPF strategy.
Therefore, it can reason whether it is better to measure a new measurement point or repeat the measurement of a already measured point.
Not always are many repetitions of a point required, they can even reduce model accuracy. Furthermore, giving the GPR strategy this freedom enables a more optimal usage of the allowed modeling budget.

To reason about the trade-off between new points and repetitions the GPR strategy internally uses a heuristic formula / mathematical weight function to calculate what is more appropriate
depending on factors such as the noise level on the measurements, the number of already available repetitions for a specific measurement point, and the cost of the potential additional modeling points.

The weight function looks as follows:

$$w_n=tanh(\frac{1}{4} \cdot n-\frac{5}{2})$$
$$w_r=2^{\frac{1}{2} \cdot r - \frac{1}{2}}$$
$$w=w_n + w_r$$

The weight function is optimized so that at low noise levels taking new points is cheaper, as more repetitions of the same measurement point are less usefull. For high noise levels, repetitions are favored over new points if they are cheaper to counter the effects of noise.

$$h(x) = \frac{cost(x)^2 \cdot w}{gp_{cov}(x,x')^2}$$

where $n$ is the mean noise level found in the measurements,
$w$ is the weight for a points cost, the sum of the individual noise $w_n$ and repetitions weights $w_r$, considering the noise level on the measurements $n$ and the number of repetitions of this point that have already been measured $r$.

$h(x)$ is the cost of a specific measurement point $x$, cost information of the so far
already selected measurement points $cost(x)$, the covariance function of the
Gaussian process $gp_{cov}(x,x')$, which expresses the expectation that points with similar predictor values, $x$ and $x'$ will have similar response values...

$0\leq n \leq 100$

$1\leq r \leq 10$

we use a [Matern](https://en.wikipedia.org/wiki/Mat%C3%A9rn_covariance_function) $K_{Matern}$ covariance function, see also [here](https://scikit-learn.org/stable/modules/gaussian_process.html):

$$K_{Matern}=(x,x')=\frac{2^{1-\nu}}{\Gamma(\nu)}\left(\frac{\sqrt{2\nu|d|}}{\ell}\right) K_{\nu} \left( \frac{\sqrt{2\nu|d|}}{\ell} \right)$$

The distance is $d=x-x'$. $\ell$ is the characteristic length-scale of the process (practically, "how close" two points x and x' have to be to influence each other significantly).

$K_{\nu}$ is the modified [Bessel](https://en.wikipedia.org/wiki/Bessel_function#Modified_Bessel_functions) function of order $\nu$. $\Gamma(\nu)$ is the [gamma](https://en.wikipedia.org/wiki/Gamma_function) function evaluated at $\nu$.

In addition we use a white kernel to explain the noise of the signal as independently and identically normally-distributed. The parameter noise_level equals the variance of this noise.

Our GPR kernel then looks like this:

`kernel = 1.0 * Matern(length_scale=1.0, length_scale_bounds=(1e-5, 1e5), nu=1.5) + WhiteKernel(noise_level=mean_noise)`

### Hybrid Strategy (CPF+GPR)

1. Measure the cheapest available lines of five points per
parameter. Use these points to create a first model using
the sparse modeling technique.
1b. Take at least one additional point not on this axis per dimension, model parameter.
base_points + (nr_dimensions - 1)
2. uses generic strategy until a swtiching_point is hit, e.g. 13 selected points (base points + additional points) for 2 parameters.
3. then uses gpr strategy to select points
4. Use these points as input to the GPR.
4b. The noise level on these points is estimated in % divergence from the 
arithmetic mean and then used as input value for a WhiteKernel() that is added to the GPR Matern CovVariance() function.
5. continues selecting points with 2.-4. until the given budget is exhausted

For the hybrid strategy the same applies as for the GPR strategy regarding the repetitions of measurement points and their selection.

## License

[BSD 3-Clause "New" or "Revised" License](LICENSE)

## Citation

Please cite Extra-P in your publications as follows if it helps your research:

```
@inproceedings{calotoiu_ea:2013:modeling,
  author = {Calotoiu, Alexandru and Hoefler, Torsten and Poke, Marius and Wolf, Felix},
  month = {November},
  title = {Using Automated Performance Modeling to Find Scalability Bugs in Complex Codes},
  booktitle = {Proc. of the ACM/IEEE Conference on Supercomputing (SC13), Denver, CO, USA},
  year = {2013},
  pages = {1--12},
  publisher = {ACM},
  isbn = {978-1-4503-2378-9},
  doi = {10.1145/2503210.2503277}
}
```

Please cite the performance measurement dataset used for this work in your publications if it helps your research using:

```
@dataset{ritter_2023_10085298,
  author       = {Ritter, Marcus and
                  Calotoiu, Alexandru and
                  Rinke, Sebastian and
                  Reimann, Thorsten and
                  Hoefler, Torsten and
                  Wolf, Felix},
  title        = {{Performance Measurement Dataset of the HPC 
                   Benchmarks FASTEST, Kripke, LULESH, MiniFE,
                   Quicksilver, and RELeARN for Scalability Studies
                   with Extra-P}},
  month        = nov,
  year         = 2023,
  publisher    = {Zenodo},
  version      = {1.0},
  doi          = {10.5281/zenodo.10085298},
  url          = {https://doi.org/10.5281/zenodo.10085298}
}
```

Please cite the version of Extra-P used for the evaluation of this work in your publications if it helps your research using:

```
@software{ritter_2023_10086772,
  author       = {Ritter, Marcus and
                  Geiß, Alexander and
                  Calotoiu, Alexandru and
                  Wolf, Felix},
  title        = {{Extra-P: Automated performance modeling for HPC 
                   applications}},
  month        = nov,
  year         = 2023,
  publisher    = {Zenodo},
  version      = {1.0},
  doi          = {10.5281/zenodo.10086772},
  url          = {https://doi.org/10.5281/zenodo.10086772}
}
```

Please cite the version of pyCubexR used for the evaluation of this work in your publications if it helps your research using:

```
@software{ritter_2023_10092353,
  author       = {Ritter, Marcus and
                  Geiß, Alexander},
  title        = {{pyCubexR: a Python package for reading the Cube4 
                   (.cubex) file format}},
  month        = nov,
  year         = 2023,
  publisher    = {Zenodo},
  version      = {1.0},
  doi          = {10.5281/zenodo.10092353},
  url          = {https://doi.org/10.5281/zenodo.10092353}
}
```
