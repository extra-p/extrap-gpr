# min required budget for relearn modeling 9.483930015258435%

import math

def main():

    counter = 9.0

    text = ""
    while counter <= 100.0:

        counter_string = "{:0.1f}".format(counter)

        text += """python3 ../case_study.py --text relearn_data.txt --processes 0 --parameters "p","n" --eval_point "512","9000" --filter 1 --budget """+str(counter)+""" --plot True --normalization True --grid-search 3 --base-values 1 --hybrid-switch 20 --repetition 2\n"""

        if counter < 0.9:
            counter += 0.1
        else:
            counter += 1.0

    file = open("run_serial_analysis.sh","w")
    file.write(text)

    file.close()

if __name__ == "__main__":
    main()
