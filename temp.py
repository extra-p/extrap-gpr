import math

def calculate_term_contributions(original_function, **kwargs):
    """
    Calculates the contribution of each term in a function as a percentage of the total function value.

    Args:
        original_function (str): The function to be evaluated as a string.
        **kwargs: Keyword arguments representing the values of the function variables.

    Returns:
        dict: A dictionary containing the contribution of each term in the function as a percentage of the total function value.
    """
    # Define the namespace for the eval() function
    namespace = {'math': math}

    # Calculate the function value
    function_value = eval(original_function, namespace, kwargs)

    # Calculate the contribution of each term
    term_contributions = {}
    for term, value in kwargs.items():
        print("term:",term)
        
        ### THE problem is that not the real function terms are used, instead: a,b from the kwargs
        # need to use function.terms and iterate over that...
        
        if value != 0:
            namespace[term] = value
            partial_derivative = (eval(original_function, namespace, {term: value + 0.001, **kwargs}) - function_value) / (0.001 * value)
            term_contribution = (value * partial_derivative / function_value) * 100
            term_contributions[term] = term_contribution

    return term_contributions

original_function = '260.328+72.004*a**1*math.log2(a)**2*961.788*b**2*math.log2(b)**1'

term_contributions = calculate_term_contributions(original_function, a=4, b=10)
for term, contribution in term_contributions.items():
    print(f"The contribution of {term} is {contribution:.2f}%")

