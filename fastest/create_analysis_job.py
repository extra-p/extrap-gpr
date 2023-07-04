import math

def main():

    counter = 1

    while counter <= 100:

        file = open("analysis_job_b"+str(counter)+".sh","w")

        text = """#!/bin/bash

#SBATCH -A project02089
#SBATCH -t 00:29:00
#SBATCH --mem-per-cpu=1800
#SBATCH -n 1
#SBATCH --exclusive
#SBATCH -o out_b"""+str(counter)+""".out
#SBATCH -e er_b"""+str(counter)+""".er
#SBATCH -J fastest_b"""+str(counter)+"""

ml --force purge
ml restore lulesh

SECONDS=0;

python ../case_study.py --cube ../../data/fastest/ --processes 0 --parameters "p","size" --eval_point "512","65536" --filter 0 --budget """+str(counter)+""" --normalization True

echo $SECONDS"""


        file.write(text)

        file.close()
    
        counter += 1

if __name__ == "__main__":
    main()
