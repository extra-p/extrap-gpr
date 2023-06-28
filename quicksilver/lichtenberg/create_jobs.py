#particles = [60,70]
particles = [10,20,30,40,50]
#particles = [10]

# for modeling
#mesh_elements = m*m*m
#m = [20,24]
#mx_factor = [5,6]
m = [2,4,8,12,16]
#m = [2]
mx_factor = [1/2,1,2,3,4]

#tasks = [24,28]
#xDom = [6,7]
#yDom = [2,2]
#zDom = [2,2]
# for modeling
mpi_ranks = [16,32,64,128,256]
# xDom*yDom*zDom=mpi_ranks
xDom = [4,4,4,8,8]
yDom = [2,4,4,4,8]
zDom = [2,2,4,4,4]

# -X,-Y,-Z size of the simulation
# -x,-y,-z number of mesh elements
# -n number of particles
# -I,-J,-K number of mpi ranks

#mx=12
#my=12
#mz=12
#particels_per_mesh=10
#particles=$mx*$my*$mz*$particels_per_mesh
#particels=40960
#echo $particles

def main():

    for k in range(len(mpi_ranks)):
        r = mpi_ranks[k]
        I = xDom[k]
        J = yDom[k]
        K = zDom[k]

        for l in range(len(m)):
            local_m = m[l]

            mxf = mx_factor[l]

            x = r * mxf
            y = local_m
            z = local_m

            mesh_elements_per_node = x * y * z

            for o in range(len(particles)):
                particles_per_mesh_element = particles[o]
                particles_per_node = particles_per_mesh_element * mesh_elements_per_node

                file = open("job_p"+str(r)+"_m"+str(local_m)+"_n"+str(particles_per_mesh_element)+".sh","w")

                text = """#!/bin/bash

#SBATCH -A project02089
#SBATCH -t 00:55:00
#SBATCH --mem-per-cpu=1800
#SBATCH -n """+str(mpi_ranks[k])+"""
#SBATCH -c 4
#SBATCH -o out_p"""+str(mpi_ranks[k])+"""_m"""+str(local_m)+"""_n"""+str(particles_per_mesh_element)+""".r%a.out
#SBATCH -e er_p"""+str(mpi_ranks[k])+"""_m"""+str(local_m)+"""_n"""+str(particles_per_mesh_element)+""".r%a.er
#SBATCH --exclusive
#SBATCH -J quicksilver

ml --force purge
ml restore lulesh

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export SCOREP_EXPERIMENT_DIRECTORY=quicksilver.p"""+str(mpi_ranks[k])+""".m"""+str(local_m)+""".n"""+str(particles_per_mesh_element)+""".r$SLURM_ARRAY_TASK_ID

SECONDS=0;

srun ./qs -i Coral2_P1.inp -X """+str(x)+""" -Y """+str(y)+""" -Z """+str(z)+""" -x """+str(x)+""" -y """+str(y)+""" -z """+str(z)+""" -I """+str(I)+""" -J """+str(J)+""" -K """+str(K)+""" -n """+str(particles_per_node)+"""

echo "runtime:" $SECONDS

"""

                file.write(text)

                file.close()

if __name__ == "__main__":
    main()
