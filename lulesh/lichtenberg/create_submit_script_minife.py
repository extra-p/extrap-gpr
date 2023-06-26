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

    text = ""

    file = open("submit_jobs.sh","w")

    for i in range(len(configs)):

        text += "echo \"submitting job with p="+str(configs[i][0])+" and n="+str(configs[i][1])+"\"\nsbatch --array=1-5 job_p"+str(configs[i][0])+"_n"+str(configs[i][1])+".sh\nsleep 1s\n"

    file.write(text)

    file.close()


if __name__ == '__main__':
    main()
