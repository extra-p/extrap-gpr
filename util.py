import math
import sympy


def analyze_term_contribution_additive(function, epsilon, a=1, b=1, c=1, d=1):
    """
    Determines if each term in a function contributes at least epsilon percent to the total function value.

    Args:
        function (Function): An object representing the function to analyze.
        epsilon (float): The minimum percentage each term must contribute to the total function value.
        a (float, optional): A coefficient applied to the first term in the function. Defaults to 1.
        b (float, optional): A coefficient applied to the second term in the function. Defaults to 1.
        c (float, optional): A coefficient applied to the third term in the function. Defaults to 1.
        d (float, optional): A coefficient applied to the fourth term in the function. Defaults to 1.

    Returns:
        bool: True if each term in the function contributes at least epsilon percent to the total function value, False otherwise.

    Examples:
        >>> f = Function('x^2 + 3x + 5')
        >>> analyze_term_contribution_additive(f, 10)
        True

        >>> g = Function('x^3 + 4x^2 + 2x + 1')
        >>> analyze_term_contribution_additive(g, 5)
        False
    """
    total_sum = eval(function.function)
    term_contributions = []

    for i in range(len(function.terms)):
        result = eval(function.terms[i])
        percent = (result / total_sum) * 100
        term_contributions.append(percent)

    return all(i >= epsilon for i in term_contributions)


def convert_to_sympy_function(python_function):
    """
    Converts a Python function to a SymPy function.

    Args:
        python_function (str): A string representing a Python function.

    Returns:
        str: A string representing a SymPy function.

    Examples:
        >>> convert_to_sympy_function("x**2 + 2*x + 1")
        'x**2 + 2*x + 1'

        >>> convert_to_sympy_function("math.log(x)")
        'sympy.log(x, 2)'
    """
    sympy_function = python_function

    while sympy_function.find("math.log") != -1:
        pos = sympy_function.find("math.log")
        head = sympy_function[:pos]
        head += "sympy.log("
        log_var = sympy_function[pos + 10:][0]
        log_var += ", 2"
        sympy_function = head + log_var + sympy_function[pos + 11:]

    return sympy_function


def analyze_term_contributions_multiplicative(python_function, epsilon, nr_parameters, x1=1, x2=1, x3=1, x4=1):
    """
    Analyze the term contributions of a Python function by calculating the partial derivatives of each parameter and
    their respective contributions in percentage to the total function value, for a given set of input values.

    Args:
        python_function (str): The Python function to be analyzed in string format.
        epsilon (float): The minimum threshold for the contribution of each parameter to be considered significant.
        nr_parameters (int): The number of parameters of the Python function (must be 2, 3, or 4).
        x1 (float, optional): The value of the first parameter. Defaults to 1.
        x2 (float, optional): The value of the second parameter. Defaults to 1.
        x3 (float, optional): The value of the third parameter (only used if nr_parameters=3 or 4). Defaults to 1.
        x4 (float, optional): The value of the fourth parameter (only used if nr_parameters=4). Defaults to 1.

    Returns:
        bool: True if all the contributions are greater than or equal to the epsilon threshold, False otherwise.
    """
    term_contributions = []

    if nr_parameters == 2:

        # calculate the sum of the python_function
        a = x1
        b = x2
        function_value = eval(python_function)
        
        # create a "symbol" called a, b for calculating the derivative with sympy
        a = sympy.Symbol('a')
        b = sympy.Symbol('b')
        
        # convert python function to sympy function
        sympy_function = convert_to_sympy_function(python_function)
            
        # convert the string into a returnable python_function using eval method
        sympy_function = eval(sympy_function)
         
        # calculating derivative
        df_da = sympy_function.diff(a)
        df_db = sympy_function.diff(b)
         
        # calculate derivative value using df_da, and df_db and the parameter values
        parameter_values = {a: x1, b: x2}
        df_da = df_da.evalf(subs=parameter_values)
        df_db = df_db.evalf(subs=parameter_values)

        # calculate the contribution in percent for each function term
        term_contributions.append((df_da / function_value) * 100)
        term_contributions.append((df_db / function_value) * 100)
        
        return all(i >= epsilon for i in term_contributions)
        
    elif nr_parameters == 3:
                
        # calculate the sum of the python_function
        a = x1
        b = x2
        c = x3
        function_value = eval(python_function)
        
        # create a "symbol" called a, b for calculating the derivative with sympy
        a = sympy.Symbol('a')
        b = sympy.Symbol('b')
        c = sympy.Symbol('c')
        
        # convert python function to sympy function
        sympy_function = convert_to_sympy_function(python_function)
            
        # convert the string into a returnable python_function using eval method
        sympy_function = eval(sympy_function)
         
        # calculating derivative
        df_da = sympy_function.diff(a)
        df_db = sympy_function.diff(b)
        df_dc = sympy_function.diff(c)
         
        # calculate derivative value using df_da, and df_db and the parameter values
        parameter_values = {a: x1, b: x2, c: x3}
        df_da = df_da.evalf(subs=parameter_values)
        df_db = df_db.evalf(subs=parameter_values)
        df_dc = df_dc.evalf(subs=parameter_values)

        # calculate the contribution in percent for each function term
        term_contributions.append((df_da / function_value) * 100)
        term_contributions.append((df_db / function_value) * 100)
        term_contributions.append((df_dc / function_value) * 100)
        
        counter = 0
        for i in range(len(term_contributions)):
            if term_contributions[i] >= epsilon:
                counter += 1
        if counter >= (nr_parameters-1):
            return True
        else:
            return False
    
    elif nr_parameters == 4:
        
        # calculate the sum of the python_function
        a = x1
        b = x2
        c = x3
        d = x4
        function_value = eval(python_function)
        
        # create a "symbol" called a, b for calculating the derivative with sympy
        a = sympy.Symbol('a')
        b = sympy.Symbol('b')
        c = sympy.Symbol('c')
        d = sympy.Symbol('d')
        
        # convert python function to sympy function
        sympy_function = convert_to_sympy_function(python_function)
            
        # convert the string into a returnable python_function using eval method
        sympy_function = eval(sympy_function)
         
        # calculating derivative
        df_da = sympy_function.diff(a)
        df_db = sympy_function.diff(b)
        df_dc = sympy_function.diff(c)
        df_dd = sympy_function.diff(d)
         
        # calculate derivative value using df_da, and df_db and the parameter values
        parameter_values = {a: x1, b: x2, c: x3, d: x4}
        df_da = df_da.evalf(subs=parameter_values)
        df_db = df_db.evalf(subs=parameter_values)
        df_dc = df_dc.evalf(subs=parameter_values)
        df_dd = df_dd.evalf(subs=parameter_values)

        # calculate the contribution in percent for each function term
        term_contributions.append((df_da / function_value) * 100)
        term_contributions.append((df_db / function_value) * 100)
        term_contributions.append((df_dc / function_value) * 100)
        term_contributions.append((df_dd / function_value) * 100)
    
        counter = 0
        for i in range(len(term_contributions)):
            if term_contributions[i] >= epsilon:
                counter += 1
        if counter >= (nr_parameters-1):
            return True
        else:
            return False
