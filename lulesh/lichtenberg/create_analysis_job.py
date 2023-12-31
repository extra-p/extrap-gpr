
# min required budget for lulesh modeling ?

import math

def main():

    counter = 13.0

    while counter <= 100.0:
        
        counter_string = "{:0.1f}".format(counter)
        file = open("analysis_job_b"+str(counter_string)+".sh","w")

        text = """#!/bin/bash

#SBATCH -A project02089
#SBATCH -t 00:10:00
#SBATCH --mem-per-cpu=3800
#SBATCH -n 1
#SBATCH --exclusive
#SBATCH -o out_b"""+str(counter_string)+""".out
#SBATCH -e er_b"""+str(counter_string)+""".er
#SBATCH -J lulesh_"""+str(counter_string)+"""

ml --force purge
ml restore lulesh

SECONDS=0;

python ../../case_study.py --cube /work/scratch/mr52jiti/data/lulesh/ --processes 0 --parameters "p","s" --eval_point "1000","35" --filter 0 --budget """+str(counter)+""" --plot True --normalization True --grid-search 3 --base-values 2 --hybrid-switch 20 --repetition 5

echo $SECONDS"""


        file.write(text)

        file.close()
    
        if counter < 0.9:
            counter += 0.1
        else:
            counter += 1.0

if __name__ == "__main__":
    main()
