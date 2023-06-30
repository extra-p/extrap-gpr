def main():

    text = ""

    file = open("submit_jobs.sh","w")

    counter = 14

    while counter < 100:

        text += "echo \"submitting job with n="+str(counter)+"\"\nsbatch analysis_job_b"+str(counter)+".sh\n"

        counter += 1
    
    file.write(text)

    file.close()


if __name__ == '__main__':
    main()
