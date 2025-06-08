def main():

    text = ""

    file = open("combine_measurements.sh","w")

    counter = 0.1

    while counter <= 100.0:

        counter_string = "{:0.1f}".format(counter)
        text += f"python3 read_measurements.py extended_analysis/analysis_results/result.budget.{counter_string}.json final/analysis_results/result.budget.{counter_string}.json result.budget.{counter_string}.json\n"

        if counter < 0.9:
            counter += 0.1
        else:
            counter += 1.0
    
    file.write(text)

    file.close()


if __name__ == '__main__':
    main()
