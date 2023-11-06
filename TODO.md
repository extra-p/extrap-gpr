# TODO LIST:

* try different modeler configs for minife to see if results can be improved...

* annotate the paper plots with important infos like in the presentation.

* run unfiltered analysis of all benchmarks

* how to visualize selection paths of actions from a markov chain???

* make heatmap work for all strategies...

* make presentation with all results

modeler_options = {'allow_log_terms': True,
                   'use_crossvalidation': True,
                   'compare_with_RSS': False,
                   'poly_exponents': "0,1,2,3,4,5",
                   'log_exponents': "0,1,2",
                  }


modeler_options = {'allow_log_terms': True,
                   'use_crossvalidation': True,
                   'compare_with_RSS': False,
                   'poly_exponents': [0,1,2,3,4,5],
                   'log_exponents': [0,1,2],
                   'retain_default_exponents': False,
                   'force_combination_exponents': True,
                   'allow_negative_exponents': False,
                   'allow_combinations_of_sums_and_products': False,
                   '#single_parameter_modeler': "default",
                   '#single_parameter_options': {'poly_exponents': "0,1,2,3,4,5",
                   'log_exponents': "0,1,2"},
                  }