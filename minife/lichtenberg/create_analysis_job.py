def main():

    counter = 100

    while counter <= 100:

        file = open("analysis_job_b"+str(counter)+".sh","w")

        text = """#!/bin/bash

#SBATCH -A project02089
#SBATCH -t 23:00:00
#SBATCH --mem-per-cpu=1800
#SBATCH -n 1
#SBATCH --exclusive
#SBATCH -o out_b"""+str(counter)+""".out
#SBATCH -e er_b"""+str(counter)+""".er
#SBATCH -J minife_b"""+str(counter)+"""

ml --force purge
ml restore lulesh

SECONDS=0;

python ../../case_study.py --cube /work/scratch/mr52jiti/data/minife/ --processes 0 --parameters "p","n" --eval_point "2048","350" --filter 1 --budget """+str(counter)+""" --plot True --normalization True --grid-search 3 --base-values 2 --hybrid-switch 20 --repetition 5

echo $SECONDS"""


        file.write(text)

        file.close()
    
        counter += 1

if __name__ == "__main__":
    main()
