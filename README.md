# extrap-gpr

## GPR Tests

`python .\gpr.py --nr-parameters 2 --nr-functions 1 --nr-repetitions 5 --noise 1`

## Run the evaluation tool:

FASTEST: `python .\case_study.py --budget 20 --cube C:\Users\ritte\Downloads\fastest\ --processes 0 --parameters "p","size" --eval_point "512","65536" --filter 1`

Relearn:

Kripke:

`python .\case_study.py --budget 20 --extra-p .\fastest.extra-p --processes 0 --parameters "p","size"`

`python .\synthetic_evaluation.py --nr-parameters 2 --nr-functions 10 --nr-repetitions 5 --noise 1`

`python .\case_study.py --budget 20 --cube C:\Users\ritte\Downloads\fastest\ --processes 0 --parameters "p","size"`


## Bulding Extra-P from source

1. `cd extrap-counter`
2. `python setup.py sdist bdist_wheel`
3. `cd ..`
4. `pip install -e extrap-counter/`

## Notes:

* create a new side panel for the measurement point selection and cost analysis

* the user needs to specify which variable is the number of processes, as we use it to calculate the cost, cost = runtime * nr_processes = core hours

* we need to identify how many and which points are available atm
    * not enough for modeling
    * enough for modeling
    * enough for starting adding points using the generic strategy
    * enough to use gpr strategy


### Generic Strategy

1. Measure the cheapest available lines of five points per
parameter. Use these points to create a first model using
the sparse modeling technique.
2. Perform an additional measurement, starting from the
cheapest ones available. Using the model previously determined,
one can assess if the quality of the model is
sufficient (by comparing the accuracy metrics of the two models on the points used for modeling) or if additional points are required.
3. Recreate the model using all available points.
4. If the quality of the model evaluated in step 2 is insufficient,
return to step 2. (or if there is more budget available for modeling...)