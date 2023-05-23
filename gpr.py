from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF
import numpy as np
import matplotlib.pyplot as plt
from synthetic_benchmark import SyntheticBenchmark
import argparse
import math
from math import log2
import random

def main():

    # parse command line arguments
    parser = argparse.ArgumentParser(description="Run synthetic benchmark.")
    parser.add_argument("--nr-parameters", type=int, choices=[1, 2, 3, 4], required=True,
                        help="Number of parameters for the synthetic benchmark. Must be 2, 3, or 4.")
    parser.add_argument("--nr-functions", type=int, default=1000, required=True,
                        help="Number of synthetic functions used for the evaluation. Must be an integer value.")
    parser.add_argument("--nr-repetitions", type=int, default=5, required=True,
                        help="Number of repetitions for each measurement point. Must be an integer value.")
    parser.add_argument("--noise", type=int, default=1, required=True,
                        help="Percentage of induced noise. Must be an integer value.")
    args = parser.parse_args()

    # create a syntethic function
    benchmark = SyntheticBenchmark(args)
    functions = benchmark.generate_synthetic_functions()
    function = functions[0].function
    
    # x1 is the number of processes
    x1_min = 1
    x1_max = benchmark.parameter_values_a_val[0]+1
    x2_min = 1
    x2_max = benchmark.parameter_values_b_val[0]+1

    X1 = np.linspace(start=x1_min, stop=x1_max, num=1_000).reshape(-1, 1)
    X2 = np.linspace(start=x2_min, stop=x2_max, num=1_000).reshape(-1, 1)

    runtime = []
    for i in range(len(X1)):
        a = X1[i]
        b = X2[i]
        result = eval(function)
        runtime.append(result[0])
    runtime = np.array(runtime)

    # create the training data
    x_train = benchmark.parameter_values_a
    y_train2 = []
    for i in range(len(x_train)):
        a = x_train[i]
        result = eval(function)
        values = []
        for _ in range(5):
            if random.randint(1, 2) == 1:
                noise = random.uniform(0, args.noise)
                result *= ((100-noise)/100)
            else:
                noise = random.uniform(0, args.noise)
                result *= ((100+noise)/100)
            values.append(result)
        y_train2.append(np.mean(values))
    x_train = np.array(x_train)
    y_train2 = np.array(y_train2)
    x_train_plot = x_train
    y_train2_plot = y_train2
    x_train = x_train.reshape(-1, 1)
    y_train2 = y_train2.reshape(-1, 1)
    print("x_train:",x_train)
    print("y_train2:",y_train2)

    # calculate the costs of each of these training points
    nr_cores = 8
    costs = []
    for i in range(len(x_train)):
        nr_processes = x_train[i]
        core_hours = nr_processes * y_train2[i] * nr_cores
        costs.append(core_hours)

    # calculate cost of a not yet conducted experiment


    #rng = np.random.RandomState(1)
    #training_indices = rng.choice(np.arange(y.size), size=6, replace=False)
    #X_train, y_train = X[training_indices], y[training_indices]

    #print(" X_train, y_train:", X_train, y_train)


    #noise_std = 0.75
    noise_std = 1 - (args.noise/100)
    #y_train_noisy = y_train + rng.normal(loc=0.0, scale=noise_std, size=y_train.shape)
    #print("y_train_noisy:",y_train_noisy)

    #TODO: could use the noise level extracted from the measurements for the alpha value here...
    kernel = 1 * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e2))
    gaussian_process = GaussianProcessRegressor(
        kernel=kernel, alpha=noise_std**2, n_restarts_optimizer=9
    )
    gaussian_process.fit(x_train, y_train2)
    mean_prediction, std_prediction = gaussian_process.predict(X1, return_std=True)

    #print("X_train, y_train_noisy:",X_train[2], y_train_noisy[2])

    target = [benchmark.parameter_values_a_val[0]]

    #nr_processes = (X_train[2])
    XX = [target]
    predicted_y, _ = gaussian_process.predict(XX, return_std=True)
    #y_sample = gaussian_process.sample_y(XX, n_samples=1, random_state=0)
    #print("y_sample:",y_sample[0])
    #predicted_y = y_sample[0]

    # plot the baseline function
    plt.plot(X1, runtime, label=r"$f(a)="+str(function)+"$", linestyle="dotted")

    # plot the training points
    plt.errorbar(
        x_train_plot,
        y_train2_plot,
        noise_std,
        linestyle="None",
        color="tab:blue",
        marker=".",
        markersize=10,
        label="Observations",
    )

    # plot mean prediction model created by gpr
    plt.plot(X1, mean_prediction, label="Mean prediction")

    # plot the 95% confidence interval
    plt.fill_between(
        X1.ravel(),
        mean_prediction - 1.96 * std_prediction,
        mean_prediction + 1.96 * std_prediction,
        color="tab:orange",
        alpha=0.5,
        label=r"95% confidence interval",
    )

    # visualize the prediction of the target evaluation point
    #plt.plot(XX, predicted_y, marker="X")
    plt.plot(XX, predicted_y[0], marker="X", label="target point")


    plt.legend()
    plt.xlabel("number of processes $a$")
    plt.ylabel("$f(a)$")
    _ = plt.title("Gaussian process regression on a noisy dataset")
    plt.show()

    #print("mean_prediction:",mean_prediction)



if __name__ == "__main__":
    main()
