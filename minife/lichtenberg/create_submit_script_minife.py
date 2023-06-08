def main():

    tasks = [1,2,3,4,5,6,7,8,9,10]  # nr. nodes/gpus
    
    text = ""

    file = open("submit_jobs.sh","w")

    for i in range(len(tasks)):
        t = tasks[i]

        text += "echo \"submitting job with p\""+str(t)+"\nsbatch --array=1-5 job_p"+str(t)+".sh\nsleep 2s\n"

    file.write(text)

    file.close()


if __name__ == '__main__':
    main()
