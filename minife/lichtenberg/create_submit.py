def main():

    # 0-> ranks, 1-> base problem size nx/base_nx
    configs = [
        (2048,300),
    ]

    #ranks = [64,128,256,512,1024]  # nr of mpi ranks
    #problem = [90] # base problem size for bx = by = bz
    
    text = ""

    file = open("submit_jobs.sh","w")

    for i in range(len(configs)):

        text += "echo \"submitting job with p="+str(configs[i][0])+" and n="+str(configs[i][1])+"\"\nsbatch --array=1-5 job_p"+str(configs[i][0])+"_n"+str(configs[i][1])+".sh\nsleep 1s\n"

    file.write(text)

    file.close()


if __name__ == '__main__':
    main()

