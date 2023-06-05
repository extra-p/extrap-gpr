# extrap-gpr

## GPR Tests

`python .\gpr.py --text .\relearn_scripts\relearn_data.txt --mode case --budget 60 --processes 0 --parameters "p","n" --filter 0 --eval_point 512,9000`

## Run the evaluation tool for the case studies:

FASTEST: `python .\case_study.py --budget 20 --cube C:\Users\ritte\Downloads\fastest\ --processes 0 --parameters "p","size" --eval_point "512","65536" --filter 1`

Relearn: `python .\case_study.py --text .\relearn_scripts\relearn_data.txt --processes 0 --parameters "p","n" --eval_point "512","9000" --filter 1 --budget 30`

Kripke:


-------------------------------------------------------------------------------------------------------------------------

`python .\case_study.py --budget 20 --extra-p .\fastest.extra-p --processes 0 --parameters "p","size"`

`python .\case_study.py --budget 20 --cube C:\Users\ritte\Downloads\fastest\ --processes 0 --parameters "p","size"`

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
sufficient (by comparing the accuracy metrics of the two models on the points used for modeling) or if additional points are required.
3. Recreate the model using all available points.
4. If the quality of the model evaluated in step 2 is insufficient,
return to step 2. (or if there is more budget available for modeling...)

### GPR strategy

### Hybrid strategy