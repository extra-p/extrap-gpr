# TODO LIST:

* especially for 3 and more parameters the interesting part of the cost, accuracy analysis is going to be the area between 0 and 1%...

I need to analyze that...

* make sure that the mean_budget for the strategies can not be bigger than the allowed budget

* if for a function no model can be created with budget x, do not consider it in the average calculation...
-> this should be also considered for the line indicating the model accuracy when using a full matrix, basically it should not be a straight line anymore...

* this way I should get more realistic results for the strategies

* Could also create a heatmap that visualizes which points are taken in average, by specific functions...

* Monte Carlo Simulation run for each individual modeling problem (function) could work better...
* Could also combine that with Reinforcement learning...

* run synthetic analysis for 2,3,4 parameters with different budgets and noise levels and make the plots

* do kripke analysis
* create kripke plots
* make quicksilver analysis
* create quicksilver plots

* make presentation with all results