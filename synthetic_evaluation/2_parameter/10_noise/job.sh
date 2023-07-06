#!/bin/bash

#SBATCH -A project02089
#SBATCH -t 00:29:00
#SBATCH --mem-per-cpu=1800
#SBATCH -n 1
#SBATCH --exclusive
#SBATCH -o out.out
#SBATCH -e er.er
#SBATCH -J analysis

ml --force purge
ml restore lulesh

SECONDS=0;

python ../../../synthetic_evaluation.py --nr-parameters 2 --nr-functions 1000 --nr-repetitions 5 --noise 10 --mode budget --budget 30 --normalization True --plot True

echo $SECONDS