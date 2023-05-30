from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF
import numpy as np
import matplotlib.pyplot as plt
from synthetic_benchmark import SyntheticBenchmark
import argparse
import math
from math import log2


def main():

    # Parse command line arguments
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
    print("function:",function)


    X = np.linspace(start=1, stop=10, num=1_000).reshape(-1, 1)
    y = np.squeeze(X * np.sin(X))

    y2 = []
    for i in range(len(X)):
        a = X[i]
        result = eval(function)
        y2.append(result)
    y2 = np.asarray(y2)

    print("y:",y)
    print("y2:",y2)



    rng = np.random.RandomState(1)
    training_indices = rng.choice(np.arange(y.size), size=6, replace=False)
    X_train, y_train = X[training_indices], y[training_indices]



    noise_std = 0.75
    y_train_noisy = y_train + rng.normal(loc=0.0, scale=noise_std, size=y_train.shape)

    print(y_train, y_train_noisy)


    #TODO: could use the noise level extracted from the measurements for the alpha value here...
    kernel = 1 * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e2))
    gaussian_process = GaussianProcessRegressor(
        kernel=kernel, alpha=noise_std**2, n_restarts_optimizer=9
    )
    gaussian_process.fit(X_train, y_train_noisy)
    mean_prediction, std_prediction = gaussian_process.predict(X, return_std=True)

    print("X_train, y_train_noisy:",X_train[2], y_train_noisy[2])

    target = [7]

    #nr_processes = (X_train[2])
    XX = [target]
    y_sample2, taylor = gaussian_process.predict(XX, return_std=True)
    y_sample = gaussian_process.sample_y(XX, n_samples=1, random_state=0)
    print("y_sample:",y_sample[0])
    predicted_y = y_sample[0]

    plt.plot(X, y, label=r"$f(x) = x \sin(x)$", linestyle="dotted")
    plt.errorbar(
        X_train,
        y_train_noisy,
        noise_std,
        linestyle="None",
        color="tab:blue",
        marker=".",
        markersize=10,
        label="Observations",
    )
    plt.plot(X, mean_prediction, label="Mean prediction")
    plt.fill_between(
        X.ravel(),
        mean_prediction - 1.96 * std_prediction,
        mean_prediction + 1.96 * std_prediction,
        color="tab:orange",
        alpha=0.5,
        label=r"95% confidence interval",
    )
    plt.plot(XX, predicted_y, marker="X")
    plt.plot(XX, y_sample2[0], marker="X", label="target point")
    plt.legend()
    plt.xlabel("$x$")
    plt.ylabel("$f(x)$")
    _ = plt.title("Gaussian process regression on a noisy dataset")
    plt.show()

    #print("mean_prediction:",mean_prediction)



if __name__ == "__main__":
    main()
