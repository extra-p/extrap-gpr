# extrap-gpr

Evaluation code for the GPR journal paper. Contains the code to do a synthetic and case study analysis for different parameter-value selection strategies to study Extra-P's accuracy, predictive power, budget usage/modeling cost, and number of used measurement points.

## Run the evaluation tool for the case studies:

FASTEST: `python .\case_study.py --cube E:\fastest\ --processes 0 --parameters "p","size" --eval_point "512","65536" --filter 1 --budget 30 --plot True --normalization True`

Relearn: `python .\case_study.py --text .\relearn\relearn_data.txt --processes 0 --parameters "p","n" --eval_point "512","9000" --filter 1 --budget 30 --plot True --normalization True`

Kripke: `python .\case_study.py --cube E:\kripke\ --processes 0 --parameters "p","d","g" --eval_point "32768","12","160" --filter 1 --budget 30 --plot True --normalization True`

MiniFE: `python .\case_study.py --cube E:\minife\ --processes 0 --parameters "p","n" --eval_point "2048","350" --filter 1 --plot True --budget 20  --normalization True`

LULESH: `python .\case_study.py --cube E:\lulesh\ --processes 0 --parameters "p","s" --eval_point "1000","35" --filter 1 --plot True --budget 30  --normalization True`

Quicksilver: `python .\case_study.py --cube E:\quicksilver\ --processes 0 --parameters "p","m","n" --eval_point "512","20","60" --filter 1 --plot True --budget 30  --normalization True`

## Run the evaluation tool for the synthetic evaluation:

Using budget mode: `python synthetic_evaluation.py --nr-parameters 2 --nr-functions 10 --nr-repetitions 5 --noise 1 --mode budget --budget 30 --plot True --normalization True`

## Bulding Extra-P from source

1. `cd extrap-counter`
2. `python setup.py sdist bdist_wheel`
3. `cd ..`
4. `pip install -e extrap-counter/`

### Generic Strategy

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

### Notes

* Term contribution: Checking the term contribution makes a difference, since the functions are easier to model then, but there is no difference between the strategies wheter I check it or not. Overall the model accuracy of our approach looks worse if we don't check it.
* Function Building Blocks: Using different building blocks, e.g., (a+b) (a*b) (a*b+a) (a*b+b), for 2,3,4 parameters does also make an impact on the overall model accuracy of our approach, but not on the different strategies. This is the case because it makes the modeling problem harder with a bigger variety of functions to model.
* To make the results more readable in the plots, we generate the functions for evaluation once, and then use them again for the experiments with different budget values. We also set a random seed for the noise generation, so that the noise level generated does not vary for this experiments. Otherwise it looks like the accuracy differs for the baseline modeler that is using the full set of points all the time, even nothing is changed. This comes from the changing noise level on the data in fact.

#### Notes

Add extrap in user installation to path. `export PATH="$HOME/.local/bin:$PATH"`