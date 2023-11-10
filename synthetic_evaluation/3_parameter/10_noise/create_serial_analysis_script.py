import math

def main():

    counter = 0.1

    text = ""
    while counter <= 100.0:

        counter_string = "{:0.1f}".format(counter)

        text += """python3 ../../../synthetic_evaluation.py --nr-parameters 3 --nr-functions 1000 --nr-repetitions 4 --noise 10 --mode budget --budget """+str(counter)+""" --normalization True --plot True --grid-search 3 --base-values 2 --hybrid-switch 20\n"""

        if counter < 0.9:
            counter += 0.1
        else:
            counter += 1.0

    file = open("run_serial_analysis.sh","w")
    file.write(text)

    file.close()

if __name__ == "__main__":
    main()
