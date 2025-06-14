import numpy as np
from typing import Tuple, List, Dict
import streamlit as st

# Define advanced cost function with economies of scale
def cost_function(Q: float, params: Dict[str, float]) -> float:
    """Calculate total cost for given production quantity Q with exponential decay term"""
    a = params['a']
    b = params['b']
    c = params['c']
    d = params['d']
    f = params['f']
    return c + b * Q + a * Q**2 + d * np.exp(-f * Q)

# First derivative of the cost function
def cost_derivative(Q: float, params: Dict[str, float]) -> float:
    """Calculate first derivative of the advanced cost function"""
    a = params['a']
    b = params['b']
    d = params['d']
    f = params['f']
    return b + 2 * a * Q - d * f * np.exp(-f * Q)

# Second derivative of the cost function
def cost_second_derivative(Q: float, params: Dict[str, float]) -> float:
    """Calculate second derivative of the advanced cost function"""
    a = params['a']
    d = params['d']
    f = params['f']
    return 2 * a + d * f**2 * np.exp(-f * Q)

def newton_raphson(params: Dict[str, float], initial_guess: float, tolerance: float, max_iter: int) -> Tuple[float, List[Dict], bool]:
    """Newton-Raphson method to find minimum cost for advanced cost function"""
    Q = initial_guess
    iteration_history = []
    converged = False

    for i in range(max_iter):
        # Calculate function values
        f_prime = cost_derivative(Q, params)
        f_double_prime = cost_second_derivative(Q, params)

        # Store iteration data
        iteration_history.append({
            'Iteration': i + 1,
            'Q': Q,
            'Cost': cost_function(Q, params),
            "f'(Q)": f_prime,
            "f''(Q)": f_double_prime
        })

        # Check convergence
        if abs(f_prime) < tolerance:
            converged = True
            break

        # Newton-Raphson update
        if abs(f_double_prime) < 1e-10:
            st.warning("Second derivative too small, stopping iterations")
            break

        Q = Q - f_prime / f_double_prime

        # Ensure Q remains positive
        if Q <= 0:
            Q = 1.0

    return Q, iteration_history, converged
