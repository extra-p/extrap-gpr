def main():

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

    text = ""

    file = open("submit_quicksilver_jobs.sh","w")

    for k in range(len(mpi_ranks)):
        r = mpi_ranks[k]

        for l in range(len(m)):
            local_m = m[l]

            for o in range(len(particles)):
                particles_per_mesh_element = particles[o]

                text += "echo \"submitting job for counter with p "+str(r)+" m "+str(local_m)+" n "+str(particles_per_mesh_element)+"\" \nsbatch --array=1-5 job_p"+str(r)+"_m"+str(local_m)+"_n"+str(particles_per_mesh_element)+".sh\n"

    file.write(text)

    file.close()

if __name__ == '__main__':
    main()
              
