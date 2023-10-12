import math

def main():

    counter = 0.1

    while counter <= 100.0:
        
        counter_string = "{:0.1f}".format(counter)
        file = open("analysis_job_b"+str(counter_string)+".sh","w")

        text = """#!/bin/bash

#SBATCH -A project02089
#SBATCH -t 00:59:00
#SBATCH --mem-per-cpu=1800
#SBATCH -n 1
#SBATCH --exclusive
#SBATCH -o out_b"""+str(counter_string)+""".out
#SBATCH -e er_b"""+str(counter_string)+""".er
#SBATCH -J sn2b"""+str(counter_string)+"""

ml --force purge
ml restore lulesh

SECONDS=0;

python ../../../synthetic_evaluation.py --nr-parameters 3 --nr-functions 1000 --nr-repetitions 4 --noise 2 --mode budget --budget """+str(counter)+""" --normalization True --plot True --grid-search 3 --base-values 2 --hybrid-switch 20

echo $SECONDS"""


        file.write(text)

        file.close()
    
        if counter < 0.9:
            counter += 0.1
        else:
            counter += 1.0

if __name__ == "__main__":
    main()
