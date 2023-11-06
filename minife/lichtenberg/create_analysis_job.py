
# min required budget for lulesh modeling ?

import math

def main():

    counter = 100.0

    while counter <= 100.0:
        
        counter_string = "{:0.1f}".format(counter)
        file = open("analysis_job_b"+str(counter_string)+".sh","w")

        text = """#!/bin/bash

#SBATCH -A project02089
#SBATCH -t 00:29:00
#SBATCH --mem-per-cpu=3800
#SBATCH -n 1
#SBATCH --exclusive
#SBATCH -o out_b"""+str(counter_string)+""".out
#SBATCH -e er_b"""+str(counter_string)+""".er
#SBATCH -J minife_"""+str(counter_string)+"""

ml --force purge
ml restore lulesh

SECONDS=0;

python ../../case_study.py --cube /work/scratch/mr52jiti/data/minife/ --modeler multi-parameter --options single_parameter_modeler='Refining' --processes 0 --parameters "p","n" --eval_point "2048","350" --filter 1 --budget """+str(counter)+""" --plot True --normalization True --grid-search 3 --base-values 2 --hybrid-switch 20 --repetition 5

echo $SECONDS"""

        file.write(text)

        file.close()
    
        if counter < 0.9:
            counter += 0.1
        else:
            counter += 1.0

if __name__ == "__main__":
    main()
