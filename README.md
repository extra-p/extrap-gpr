# extrap-gpr

## Bulding Extra-P from source

1. `cd extrap-counter`
2. `python setup.py sdist bdist_wheel`
3. `cd ..`
4. `pip install -e extrap-counter/`

## Notes:

* create a new side panel for the measurement point selection and cost analysis

* add student as developer to extra-p github

* the user needs to specify which variable is the number of processes, as we use it to calculate the cost, cost = runtime * nr_processes = core hours

* we need to identify how many and which points are available atm
    * not enough for modeling
    * enough for modeling
    * enough for starting adding points using the generic strategy
    * enough to use gpr strategy