
# min required budget for relearn modeling 9.483930015258435%

import math

def main():

    counter = 13.0

    while counter <= 100.0:
        
        counter_string = "{:0.1f}".format(counter)
        file = open("analysis_job_b"+str(counter_string)+".sh","w")

        text = """#!/bin/bash

#SBATCH -A l0003015
#SBATCH -t 00:29:00
#SBATCH --mem-per-cpu=1800
#SBATCH -n 1
#SBATCH --exclusive
#SBATCH -o out_b"""+str(counter_string)+""".out
#SBATCH -e er_b"""+str(counter_string)+""".er
#SBATCH -J relearn_"""+str(counter_string)+"""

ml --force purge
ml gcc python

SECONDS=0;

python ../case_study.py --text relearn_data.txt --processes 0 --parameters "p","n" --eval_point "512","9000" --filter 0 --budget """+str(counter)+""" --plot True --normalization True --grid-search 3 --base-values 1 --hybrid-switch 20 --repetition 2 --newonly 1

echo $SECONDS"""


        file.write(text)

        file.close()
    
        if counter < 0.9:
            counter += 0.1
        else:
            counter += 1.0

if __name__ == "__main__":
    main()
