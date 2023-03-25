import random
import math
from math import log2
from function import Function

class FunctionGenerator():

    def __init__(self, nr_parameters=1, coefficient_min=0, coefficient_max=1000, epsilon=1, seed=1, reproducable=False):
    
        self.epsilon = epsilon # the minimum contribution each term must have to the overall function value
        self.seed = seed # random seed to make results reproducable
        self.reproducable = reproducable
        self.nr_parameters = nr_parameters
        self.log_exponents = [0,1,2]
        self.poly_exponents = [0,1,2,3]
        self.parameter_placeholders = ["a","b","c","d","e","f"]
        self.coefficient_min = coefficient_min
        self.coefficient_max = coefficient_max
        
        if reproducable == True:
            random.seed(self.seed)
            
    def check_term_contribution(self, function, a=1, b=1, c=1, d=1, e=1, f=1):
        sum = eval(function.function)
        term_contributions = []
        for i in range(self.nr_parameters):
            result = eval(function.terms[i])
            print("result:",result)
            #percent = (sum-result)/(sum/100.0)
            percent = (result/sum)*100
            term_contributions.append(percent)
        print("term_contributions %:",term_contributions)
        return all(i >= self.epsilon for i in term_contributions)
        
    def calculate_term_contributions(self, original_function, **kwargs):
        """
        Calculates the contribution of each term in a function as a percentage of the total function value.

        Args:
            original_function (str): The function to be evaluated as a string.
            **kwargs: Keyword arguments representing the values of the function variables.

        Returns:
            dict: A dictionary containing the contribution of each term in the function as a percentage of the total function value.
        """
        # Define the namespace for the eval() function
        namespace = {'math': math}

        # Calculate the function value
        print("original_function:",original_function)
        function_value = eval(original_function, namespace, kwargs)
        print("function_value:",function_value)

        # Calculate the contribution of each term
        term_contributions = {}
        for term, value in kwargs.items():
            if value != 0:
                namespace[term] = value
                partial_derivative = (eval(original_function, namespace, {term: value + 0.001, **kwargs}) - function_value) / (0.001 * value)
                print("partial_derivative:",partial_derivative)
                term_contribution = (value * partial_derivative / function_value) * 100
                print("term_contribution:",term_contribution)
                term_contributions[term] = term_contribution
                
        print("term_contributions:",term_contributions)

        return term_contributions
    
    
    
        
    def check_term_contribution2(self, function, a=1, b=1, c=1, d=1, e=1, f=1):
        sum = eval(function.function)
        term_contributions = []
        temp_sums = []
        for i in range(self.nr_parameters):
            result = eval(function.terms[i])
            temp_sums.append(result)
        max_value = max(temp_sums)
        for i in range(self.nr_parameters):
            percentage = (temp_sums[i]/max_value)*100
            term_contributions.append(percentage)
            
        print("term_contributions %:",term_contributions)
            
        #print("result:",result)
        #percent = (sum-result)/(sum/100.0)
        #percent = (result/sum)*100
        #term_contributions.append(percent)
        #print("term_contributions %:",term_contributions)
        return all(i >= self.epsilon for i in term_contributions)
        
        
    def evaluate_function(self, function, a=1, b=1, c=1, d=1, e=1, f=1):
        return eval(function.function)
    
    def generate_function(self):
    
        options = ["additive", "multiplicative"]
        
        if random.choice(options) == "additive":
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
                valid = self.check_term_contribution(f, 4, 10)
            else:
                valid = True
            print("valid:",valid)
            return f
        
        else:
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
                #valid = self.check_term_contribution2(f, 4, 10)
                term_contributions = self.calculate_term_contributions(f.function, a=4, b=10)
                for term, contribution in term_contributions.items():
                    print(f"The contribution of {term} is {contribution:.2f}%")
                
                valid = False
            else:
                valid = True
            print("valid:",valid)
            return f
        
        # y = c+c*x^e*log(x)^e + ...
        # y = c+c*x^e*log(x)^e * ...
        
    
