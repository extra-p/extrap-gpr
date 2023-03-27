from function_generator import FunctionGenerator
import copy
from multiprocessing import Manager
import multiprocessing as mp
from multiprocessing import Pool
from tqdm import tqdm


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
        
        # parallelize reading all measurement_files in one folder
        manager = Manager()
        shared_dict = manager.dict()
        cpu_count = mp.cpu_count()

        inputs = []
        for i in range(self.nr_functions):
            inputs.append([i, shared_dict])

        with Pool(cpu_count) as pool:
            _ = list(tqdm(pool.imap(generator.generate_function, inputs), total=self.nr_functions))

        copy_dict = copy.deepcopy(shared_dict)
        
        for i in range(len(copy_dict)):
            print(copy_dict[i].function)


        #TODO: need to create an experiment for each function

        #TODO: induce random noise into the measurements

        #TODO: calculate the cost of the full matric of measurement points

        #TODO: create models for all functions using all measurement points

        #TODO: create models using the generic strategy

        #TODO: calculate the cost of the points used by the generic strategy and the number of additional points

        #TODO: create models using the gpr strategy

        #TODO: calculate the cost of the points used by the gpr strategy and the number of additional points

        #TODO: create models using the hybrid strategy

        #TODO: calculate the cost of the points used by the hybrid strategy and the number of additional points




        
       
    
        
        
    
