def main():

    text = ""

    file = open("submit_analysis_jobs.sh","w")

    counter = 1

    while counter <= 100:

        text += "echo \"submitting job with b="+str(counter)+"\"\nsbatch analysis_job_b"+str(counter)+".sh\n"

        counter += 1
    
    file.write(text)

    file.close()


if __name__ == '__main__':
    main()
