from function_generator import FunctionGenerator


class SyntheticBenchmark():

    def __init__(self, nr_parameters, nr_functions):
        self.nr_parameters = nr_parameters
        self.nr_functions = nr_functions
        self.parameter_values_a = [4,8,16,32,64]
        self.parameter_values_b = [10,20,30,40,50]
        self.parameter_values_c = [1000,2000,3000,4000,5000]
        self.parameter_values_d = [10,12,14,16,18]
        
    def run(self):
        generator = FunctionGenerator(self.parameter_values_a, self.parameter_values_b, self.parameter_values_c, self.parameter_values_d, nr_parameters=self.nr_parameters)
        functions = []
        for _ in range(self.nr_functions):
            functions.append(generator.generate_function())
        
        #print("function:",function.function)
        #result = f.evaluate_function(function, 4, 10)
        
        
    
        
        
    
