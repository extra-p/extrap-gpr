# minife_problem_size_test

import math

#base_problem_size = (nx * ny * nz)

base_nx = 100
base_ny = 100
base_nz = 100

ranks = 256
x = ((base_nx * base_ny * base_nz) * ranks)
nx = math.pow(x, (1/3))
nx = int(nx)

print("srun ./miniFE.x -nx "+str(nx)+" -ny "+str(nx)+" -nz "+str(nx)+"")