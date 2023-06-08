
ranks = [1,2,3,4,5,6,7,8,9,10]  # nr of mpi ranks
problem = [100,200,300,400,500] # base problem size for bx = by = bz
repetitions = 2 # number of repetitions for each configuration

#TODO: should do repetitions with an array...
#TODO: need to calculate actual problem size here from base size!

def main():

    for i in range(len(ranks)):

        for j in range(len(problem)):

            for l in range(repetitions):
        
                file = open("job_p"+str(ranks[i])+"_n"+str(problem[j])+".sh","w")

                text = """#!/bin/bash

#SBATCH -A project02089
#SBATCH -t 01:00:00
#SBATCH --mem-per-cpu=1800
#SBATCH -n """+str(ranks[i])+"""
#SBATCH --exclusive
#SBATCH -o minife_out_p"""+str(ranks[i])+"""_n"""+str(problem[j])+""".out
#SBATCH -e minife_er_p"""+str(ranks[i])+"""_n"""+str(problem[j])+""".er
#SBATCH -J minife_p"""+str(ranks[i])+"""_n"""+str(problem[j])+"""

ml --force purge
ml restore minife

export SCOREP_EXPERIMENT_DIRECTORY=minife.p"""+str(ranks[i])+""".n"""+str(problem[j])+""".r

SECONDS=0;

srun ./miniFE.x -nx """+str(nx)+""" -ny """+str(ny)+""" -nz """+str(nz)+"""

echo $SECONDS"""



        file.write(text)

        file.close()

if __name__ == "__main__":
    main()
