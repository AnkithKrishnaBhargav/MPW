import numpy as np
import cvxpy as cp
from typing import List, Dict, Any

class NSWAllocationError(Exception):
    pass

def min_max_normalized(arr: np.ndarray) -> np.ndarray:
    arr = np.array(arr, dtype=float)
    mn = arr.min()
    mx = arr.max()
    if np.isclose(mx, mn):
        return np.ones_like(arr)
    return (arr - mn) / (mx - mn)

def jain_index(x: np.ndarray) -> float:
    x = np.array(x, dtype=float)
    if np.allclose(x, 0):
        return 0.0
    num = (x.sum() ** 2)
    den = len(x) * (x ** 2).sum()
    return float(num / den)

def solve_nsw_allocation(
        firms: List[Dict[str, Any]],
        cap: float,
        alpha: float = 0.6,
        beta: float = 0.1,
        epsilon: float = 1e-6,
) -> Dict[str, Any]:

    cap = float(cap)
    if cap <= 0:
        raise NSWAllocationError("Cap C must be positive")

    n = len(firms)
    if n == 0:
        raise NSWAllocationError("Number of firms cannot be zero")

    d = np.array([float(f.get("demand_d", 0.0)) for f in firms], dtype=float)
    r = np.array([float(f.get("responsibility_r", 0.0)) for f in firms], dtype=float)

    if np.any(d < 0) or np.any(r < 0):
        raise NSWAllocationError("Demand and Responsibility must be non-negative")

    L = beta * d          # equity floors
    U = d.copy()          # capacity upper bounds = demand

    if L.sum() > cap:
        raise NSWAllocationError("Equity floors infeasible: sum(beta * d) > cap")

    # Compute weights from normalized need/responsibility
    d_norm = min_max_normalized(d)
    r_norm = min_max_normalized(r)
    w = alpha * d_norm + (1.0 - alpha) * r_norm
    if np.allclose(w, 0):
        w = np.ones_like(w)

   
    x = cp.Variable(n, nonneg=True)

    objective = cp.Maximize(cp.sum(cp.multiply(w, cp.log(x + epsilon))))

    constraints = [
        cp.sum(x) <= cap,
        x >= L,
        x <= U,
    ]

    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.SCS, verbose=False)

    if problem.status not in ("optimal", "optimal_inaccurate"):
        raise NSWAllocationError(f"Solver status: {problem.status}")

    x_opt = np.maximum(np.array(x.value).astype(float).flatten(), 0.0)

    if d.sum() > 0:
        x_prop = cap * d / d.sum()
    else:
        x_prop = np.zeros_like(d)

    x_equal = np.full_like(d, cap / n)

    metrics = {
        "jain_nsw": jain_index(x_opt),
        "jain_prop": jain_index(x_prop),
        "jain_equal": jain_index(x_equal),
        "total_alloc_nsw": float(x_opt.sum()),
        "total_cap": float(cap),
    }

    firm_results = []
    for i, f in enumerate(firms):
        coverage = float(x_opt[i] / d[i]) if d[i] > 0 else None
        firm_results.append({
            "id": f.get("id"),
            "name": f.get("name"),
            "sector": f.get("sector"),
            "demand_d": float(d[i]),
            "responsibility_r": float(r[i]),
            "weight": float(w[i]),
            "alloc_nsw": float(x_opt[i]),
            "alloc_prop": float(x_prop[i]),
            "alloc_equal": float(x_equal[i]),
            "coverage_nsw": coverage,
        })

    return {
        "cap": float(cap),
        "alpha": float(alpha),
        "beta": float(beta),
        "epsilon": float(epsilon),
        "firm_results": firm_results,
        "metrics": metrics,
        "status": problem.status,
    }
