def main():

    # 0-> ranks, 1-> base problem size nx/base_nx
    configs = [
        (64,70),
        (64,75),
        (64,80),
        (64,85),
        (64,90),
        (128,75),
        (128,80),
        (128,85),
        (128,90),
        (128,95),
        (256,80),
        (256,85),
        (256,90),
        (256,95),
        (256,100),
        (512,85),
        (512,90),
        (512,95),
        (512,100),
        (512,105),
        (1024,90),
        (1024,95),
        (1024,100),
        (1024,105),
        (1024,110),
        (2048,100),
    ]

    text = ""

    file = open("submit_jobs.sh","w")

    for i in range(len(configs)):

        text += "echo \"submitting job with p="+str(configs[i][0])+" and n="+str(configs[i][1])+"\"\nsbatch --array=1-5 job_p"+str(configs[i][0])+"_n"+str(configs[i][1])+".sh\nsleep 1s\n"

    file.write(text)

    file.close()


if __name__ == '__main__':
    main()
