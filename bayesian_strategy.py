from scipy.stats import norm
import numpy as np
from scipy.optimize import minimize

def expected_improvement(X_candidates, gpr, y_train, xi=0.01):
    #print("DEBUG X_candidates:", X_candidates)
    #x = [x]
    if X_candidates.ndim == 1:
        X_candidates = X_candidates.reshape(1, -1)
    mu, sigma = gpr.predict(X_candidates, return_std=True)
    mu_sample_opt = np.min(y_train)

    with np.errstate(divide='warn'):
        imp = mu_sample_opt - mu - xi
        Z = imp / sigma
        ei = imp * norm.cdf(Z) + sigma * norm.pdf(Z)
        ei[sigma == 0.0] = 0.0

    return ei

def propose_location(acquisition, gpr, X_train, y_train, bounds, n_restarts=25):
    dim = X_train.shape[1]
    best_x = None
    best_acq = -np.inf

    for _ in range(n_restarts):
        x0 = np.random.uniform(bounds[:, 0], bounds[:, 1], size=dim)
        res = minimize(
            lambda x: -acquisition(x.reshape(1, -1), gpr, X_train, y_train),
            x0=x0,
            bounds=bounds,
            method='L-BFGS-B'
        )
        if res.fun < best_acq:
            best_acq = res.fun
            best_x = res.x

    return best_x.reshape(1, -1)