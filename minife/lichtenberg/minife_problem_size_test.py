# minife_problem_size_test

import math

#base_problem_size = (nx * ny * nz)

n = [100,200,300,400,500]
p = [64,128,256,512,1024]

n_e = [600]
p_e = [2048]

<<<<<<< HEAD
base = 90
=======
base = 110
>>>>>>> 88dc6b0680559a7dc7e1c68ed911e75e531f7193

base_nx = base
base_ny = base
base_nz = base

ranks = 2048
x = ((base_nx * base_ny * base_nz) * ranks)
nx = math.pow(x, (1/3))
nx = int(nx)

print("srun ./miniFE.x -nx "+str(nx)+" -ny "+str(nx)+" -nz "+str(nx)+"")


# p = [4,8,16,32,64,128,256,512]


# 50, 64 = 13sec
