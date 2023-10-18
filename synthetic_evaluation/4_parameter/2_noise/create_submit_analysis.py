def main():

    text = ""

    file = open("submit_analysis_jobs.sh","w")

    counter = 96.0

    while counter <= 100.0:

        counter_string = "{:0.1f}".format(counter)
        text += "echo \"submitting job with b="+str(counter_string)+"\"\nsbatch analysis_job_b"+str(counter_string)+".sh\n"

        if counter < 0.9:
            counter += 0.1
        else:
            counter += 1.0
    
    file.write(text)

    file.close()


if __name__ == '__main__':
    main()
