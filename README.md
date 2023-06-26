# extrap-gpr

Evaluation code for the GPR journal paper. Contains the code to do a synthetic and case study analysis for different parameter-value selection strategies to study Extra-P's accuracy, predictive power, budget usage/modeling cost, and number of used measurement points.

## Run the evaluation tool for the case studies:

FASTEST: `python .\case_study.py --budget 20 --cube D:\fastest\ --processes 0 --parameters "p","size" --eval_point "512","65536" --filter 1 --plot True --normalization True`

Relearn: `python .\case_study.py --text .\relearn\relearn_data.txt --processes 0 --parameters "p","n" --eval_point "512","9000" --filter 1 --budget 30 --plot True --normalization True`

Kripke: ``

MiniFE: `python .\case_study.py --cube E:\minife\ --processes 0 --parameters "p","n" --eval_point "2048","100" --filter 1 --plot True --budget 20  --normalization True`



## Run the evaluation tool for the synthetic evaluation:

`python .\synthetic_evaluation.py --nr-parameters 2 --nr-functions 10 --nr-repetitions 5 --noise 1`

## Bulding Extra-P from source

1. `cd extrap-counter`
2. `python setup.py sdist bdist_wheel`
3. `cd ..`
4. `pip install -e extrap-counter/`

## Notes:

* we need to identify how many and which points are available atm
    * not enough for modeling -> advice finishing the lines of 5 points for each parameter
    * enough for modeling -> advice additional points from the matrix of possible points (decide based on estimated cost from our created model)


### Generic Strategy

1. Measure the cheapest available lines of five points per
parameter. Use these points to create a first model using
the sparse modeling technique.
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
2. Use these points as input to the GPR.
3. Train the GPR.
4. Suggest a new point using the trained GPR.
5. Take this measurement and add it to the experiment. Create a new model.
6. Add the new point to the GPR. Train the GPR again.
7. Continue this process until budget for modeling is exhausted. Steps: 4-6.

### Hybrid strategy

1. Measure the cheapest available lines of five points per
parameter. Use these points to create a first model using
the sparse modeling technique.
2. uses generic strategy until a swtiching_point is hit, e.g. 11 selected points (base points + additional points) for 2 parameters.
3. then uses gpr strategy to select points
4. continues selecting points with 2. and 3. until the given budget is exhausted


### CLANG

ml Stages/2022 GCC/11.2.0 ParaStationMPI/5.5.0-1 Clang/13.0.1 libtool/.2.4.6 Python/3.9.6

export PATH=/p/project/deepsea/demorais1/scorep-llvm/build/install/bin/:$PATH
export MPICH_CC=clang MPICH_CXX=clang++
mpicxx --version
export SCOREP_TIMER=logical_basicblocks