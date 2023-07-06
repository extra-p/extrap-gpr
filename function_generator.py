import random
import math
from math import log2
from function import Function
from util import analyze_term_contribution_additive
from util import analyze_term_contributions_multiplicative


class FunctionGenerator():

    def __init__(self, parameter_values_a, parameter_values_b, parameter_values_c, parameter_values_d, nr_parameters=1, coefficient_min=0, coefficient_max=1000, epsilon=1, seed=1, reproducable=False):
    
        self.epsilon = epsilon # the minimum contribution each term must have to the overall function value
        self.seed = seed # random seed to make results reproducable
        self.reproducable = reproducable
        self.nr_parameters = nr_parameters
        self.log_exponents = [0,1,2]
        self.poly_exponents = [0,1/4,1/3,1/2,1,2/3,3/4,4/5,5/4,4/3,3/2,5/3,7/4,9/4,7/3,5/2,8/3,11/4,2,3]
        self.parameter_placeholders = ["a","b","c","d"]
        self.coefficient_min = coefficient_min
        self.coefficient_max = coefficient_max
        self.parameter_values_a = parameter_values_a
        self.parameter_values_b = parameter_values_b
        self.parameter_values_c = parameter_values_c
        self.parameter_values_d = parameter_values_d
        
        if reproducable == True:
            random.seed(self.seed)
        
    def evaluate_function(self, function, a=1, b=1, c=1, d=1):
        return eval(function.function)
    
    def generate_function(self, inputs):

        counter = inputs[0]
        shared_dict = inputs[1]
    
        options = ["additive", "multiplicative"]
        
        # generate an additive function
        if random.choice(options) == "additive":
            valid_function = False
            while valid_function != True:
                f = Function("")
                function = ""
                c_0 = str(format(random.uniform(self.coefficient_min, self.coefficient_max), '.3f'))
                function += c_0
                for i in range(self.nr_parameters):
                    c_k = str(format(random.uniform(self.coefficient_min, self.coefficient_max), '.3f'))
                    e_poly = str(random.choice(self.poly_exponents))
                    e_log = str(random.choice(self.log_exponents))
                    term = c_k+"*"+self.parameter_placeholders[i]+"**"+e_poly+"*math.log2("+self.parameter_placeholders[i]+")**"+e_log
                    function += "+"+term
                    f.add_term(term)
                f.set_function(function)
                if self.nr_parameters > 1:
                    valid_function_min = analyze_term_contribution_additive(f, self.epsilon, a=min(self.parameter_values_a), b=min(self.parameter_values_b), c=min(self.parameter_values_c), d=min(self.parameter_values_d))
                    valid_function_max = analyze_term_contribution_additive(f, self.epsilon, a=max(self.parameter_values_a), b=max(self.parameter_values_b), c=max(self.parameter_values_c), d=max(self.parameter_values_d))
                    if valid_function_min == True and valid_function_max == True:
                        valid_function = True
                    else:
                        valid_function = False
                else:
                    valid_function = True
            shared_dict[counter] = f
        
        # generate a multiplicative function
        else:
            valid_function = False
            while valid_function != True:
                f = Function("")
                function = ""
                c_0 = str(format(random.uniform(self.coefficient_min, self.coefficient_max), '.3f'))
                function += c_0
                for i in range(self.nr_parameters):
                    c_k = str(format(random.uniform(self.coefficient_min, self.coefficient_max), '.3f'))
                    e_poly = str(random.choice(self.poly_exponents))
                    e_log = str(random.choice(self.log_exponents))
                    if i == 0:
                        term = c_k+"*"+self.parameter_placeholders[i]+"**"+e_poly+"*math.log2("+self.parameter_placeholders[i]+")**"+e_log
                        function += "+"+term
                    else:
                        term = c_k+"*"+self.parameter_placeholders[i]+"**"+e_poly+"*math.log2("+self.parameter_placeholders[i]+")**"+e_log
                        function += "*"+term
                    f.add_term(term)
                f.set_function(function)
                if self.nr_parameters > 1:
                    valid_function_min = analyze_term_contributions_multiplicative(f.function, self.epsilon, self.nr_parameters, x1=min(self.parameter_values_a), x2=min(self.parameter_values_b), x3=min(self.parameter_values_c), x4=min(self.parameter_values_d))
                    valid_function_max = analyze_term_contributions_multiplicative(f.function, self.epsilon, self.nr_parameters, x1=max(self.parameter_values_a), x2=max(self.parameter_values_b), x3=max(self.parameter_values_c), x4=max(self.parameter_values_d))
                    if valid_function_min == True and valid_function_max == True:
                        valid_function = True
                    else:
                        valid_function = False
                else:
                    valid_function = True
            shared_dict[counter] = f
        