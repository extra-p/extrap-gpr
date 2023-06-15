import math

def main():

    # 0-> ranks, 1-> base problem size nx/base_nx
    configs = [
        (2048,300),
    ]

    for i in range(len(configs)):

        base = configs[i][1]
        base_nx = base
        base_ny = base
        base_nz = base
        x = ((base_nx * base_ny * base_nz) * configs[i][0])
        nx = math.pow(x, (1/3))
        nx = int(nx)
        ny = nx
        nz = nx

        file = open("job_p"+str(configs[i][0])+"_n"+str(configs[i][1])+".sh","w")

        text = """#!/bin/bash

#SBATCH -A project02089
#SBATCH -t 01:00:00
#SBATCH --mem-per-cpu=1800
#SBATCH -n """+str(configs[i][0])+"""
#SBATCH --exclusive
#SBATCH -o out_p"""+str(configs[i][0])+"""_n"""+str(configs[i][1])+"""_r%a.out
#SBATCH -e er_p"""+str(configs[i][0])+"""_n"""+str(configs[i][1])+"""_r%a.er
#SBATCH -J minife_p"""+str(configs[i][0])+"""_n"""+str(configs[i][1])+"""_r%a

ml --force purge
ml restore minife

export SCOREP_EXPERIMENT_DIRECTORY=minife.p"""+str(configs[i][0])+""".n"""+str(configs[i][1])+""".r$SLURM_ARRAY_TASK_ID

SECONDS=0;

srun ./miniFE.x -nx """+str(nx)+""" -ny """+str(ny)+""" -nz """+str(nz)+"""

echo $SECONDS"""


        file.write(text)

        file.close()

if __name__ == "__main__":
    main()

