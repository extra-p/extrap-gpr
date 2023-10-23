# extrap-gpr

Evaluation code for the GPR journal paper. Contains the code to do a synthetic and case study analysis for different parameter-value selection strategies to study Extra-P's accuracy, predictive power, budget usage/modeling cost, and number of used measurement points.

## Run the evaluation tool for the case studies

For all case studies, besides RELEARN, the path to the data needs to be changed. The data can be found at: [Link](#).

### RELEARN:

1. `cd relearn`
2. (single run) `python ../case_study.py --text relearn_data.txt --processes 0 --parameters "p","n" --eval_point "512","9000" --filter 1 --budget 30 --plot True --normalization True --grid-search 3 --base-values 1 --hybrid-switch 20 --repetition 2`
3. `./run_analysis.sh`
4. `./process.sh`
5. `./archive.sh final`
6. `python single_plot.py --path final/analysis_results/ --name results_final --reps 2`
7. `python budget_usage_plot.py --path final/analysis_results/ --name budget_usage --reps 2`

### LULESH:

1. `cd lulesh/lichtenberg`
2. (single run) `python ../../case_study.py --cube /work/scratch/mr52jiti/data/lulesh/ --processes 0 --parameters "p","s" --eval_point "1000","35" --filter 1 --budget 1 --plot True --normalization True --grid-search 3 --base-values 2 --hybrid-switch 20 --repetition 5`
3. `./run_analysis.sh`
4. `./process.sh`
5. `./archive.sh final`
6. `python single_plot.py --path final/analysis_results/ --name results_final --reps 5`
7. `python budget_usage_plot.py --path final/analysis_results/ --name budget_usage --reps 5`

### MiniFE:

1. `cd minife/lichtenberg`
2. (single run) `python ../../case_study.py --cube /work/scratch/mr52jiti/data/minife/ --processes 0 --parameters "p","n" --eval_point "2048","350" --filter 1 --budget 1 --plot True --normalization True --grid-search 3 --base-values 2 --hybrid-switch 20 --repetition 5`
3. `./run_analysis.sh`
4. `./process.sh`
5. `./archive.sh final`
6. `python single_plot.py --path final/analysis_results/ --name results_final --reps 5`
7. `python budget_usage_plot.py --path final/analysis_results/ --name budget_usage --reps 5`

### FASTEST:

1. `cd fastest`
2. (single run) `python ../case_study.py --cube /work/scratch/mr52jiti/data/fastest/ --processes 0 --parameters "p","size" --eval_point "512","65536" --filter 1 --budget 1 --plot True --normalization True --grid-search 3 --base-values 2 --hybrid-switch 20 --repetition 5`
3. `./run_analysis.sh`
4. `./process.sh`
5. `./archive.sh final`
6. `python single_plot.py --path final/analysis_results/ --name results_final --reps 5`
7. `python budget_usage_plot.py --path final/analysis_results/ --name budget_usage --reps 5`

#########

FASTEST: `python .\case_study.py --cube E:\fastest\ --processes 0 --parameters "p","size" --eval_point "512","65536" --filter 1 --budget 30 --plot True --normalization True`

Kripke: `python .\case_study.py --cube E:\kripke\ --processes 0 --parameters "p","d","g" --eval_point "32768","12","160" --filter 1 --budget 30 --plot True --normalization True`

Quicksilver: `python .\case_study.py --cube E:\quicksilver\ --processes 0 --parameters "p","m","n" --eval_point "512","20","60" --filter 1 --plot True --budget 30  --normalization True`

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

## Bulding Extra-P from source

1. `git clone https://github.com/extra-p/extrap.git`
2. `cd extrap`
3. `python setup.py sdist bdist_wheel`
4. `cd ..`
5. `pip install -e extrap/`

After installation add extrap in user installation to path if necessary: `export PATH="$HOME/.local/bin:$PATH"`.

### CPF (cheapest points first) Strategy

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

### GPR strategy

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


### Hybrid strategy

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

### Notes

* Term contribution: Checking the term contribution makes a difference, since the functions are easier to model then, but there is no difference between the strategies wheter I check it or not. Overall the model accuracy of our approach looks worse if we don't check it.
* Function Building Blocks: Using different building blocks, e.g., (a+b) (a*b) (a*b+a) (a*b+b), for 2,3,4 parameters does also make an impact on the overall model accuracy of our approach, but not on the different strategies. This is the case because it makes the modeling problem harder with a bigger variety of functions to model.
* To make the results more readable in the plots, we generate the functions for evaluation once, and then use them again for the experiments with different budget values. We also set a random seed for the noise generation, so that the noise level generated does not vary for this experiments. Otherwise it looks like the accuracy differs for the baseline modeler that is using the full set of points all the time, even nothing is changed. This comes from the changing noise level on the data in fact.
