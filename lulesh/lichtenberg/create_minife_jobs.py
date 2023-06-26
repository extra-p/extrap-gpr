import math

def main():

    # 0-> ranks, 1-> problem size
    configs = [
        (125,10),
        (216,10),
        (343,10),
        (512,10),
        (729,10),
        (125,15),
        (216,15),
        (343,15),
        (512,15),
        (729,15),
        (125,20),
        (216,20),
        (343,20),
        (512,20),
        (729,20),
        (125,25),
        (216,25),
        (343,25),
        (512,25),
        (729,25),
        (125,30),
        (216,30),
        (343,30),
        (512,30),
        (729,30),
        (1000,35),
    ]

    for i in range(len(configs)):

        file = open("job_p"+str(configs[i][0])+"_s"+str(configs[i][1])+".sh","w")

        text = """#!/bin/bash

#SBATCH -A project02089
#SBATCH -t 01:00:00
#SBATCH --mem-per-cpu=1800
#SBATCH -n """+str(configs[i][0])+"""
#SBATCH --exclusive
#SBATCH -o out_p"""+str(configs[i][0])+"""_s"""+str(configs[i][1])+"""_r%a.out
#SBATCH -e er_p"""+str(configs[i][0])+"""_s"""+str(configs[i][1])+"""_r%a.er
#SBATCH -J lulesh_p"""+str(configs[i][0])+"""_s"""+str(configs[i][1])+"""_r%a

ml --force purge
ml restore lulesh

export SCOREP_EXPERIMENT_DIRECTORY=lulesh.p"""+str(configs[i][0])+""".s"""+str(configs[i][1])+""".r$SLURM_ARRAY_TASK_ID

SECONDS=0;

srun ./lulesh2.0 -s """+str(configs[i][1])+"""

echo $SECONDS"""


        file.write(text)

        file.close()

if __name__ == "__main__":
    main()
