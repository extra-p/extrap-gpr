
import math
import sympy

#TODO: need to add the number of parameters...
def calculate_term_contributions_multi(function, nr_parameters):

    term_contributions = []

    if nr_parameters == 2:

        # calculate the sum of the function
        a = 4
        b = 10
        function_value = eval(function)
        print("function_value:",function_value)
         
        # create a "symbol" called a, b
        a = sympy.Symbol('a')
        b = sympy.Symbol('b')
        
        # convert the python string into a form that can be used with sympy
        #f2 = function.replace("math.log2(", "sympy.log(")
        f2 = f
        while f2.find("math.log") != -1:
            #print(f2)
            pos = f2.find("math.log")
            #print(pos)
            x = f2[:pos+9]
            x2 = f2[:pos]
            x2 += "sympy.log("
            #print(x2)
            y = f2[pos+10:]
            var = y[0]
            var += ",2"
            #print(y, var)
            f2 = x2+var+f2[pos+11:]
            #print(f2)
            
        # convert the string into a returnable function using eval method
        f2 = eval(f2)
        #f2 = 260.328 + 72.004 * a**1 * sympy.log(a,2)**2 * 961.788 * b**2 * sympy.log(b,2)**1
         
        #Calculating Derivative
        df_da = f2.diff(a)
        df_db = f2.diff(b)
         
        print("df_da:",df_da)
        print("df_db:",df_db)

        df_da = df_da.evalf(subs={a: 4, b:10})

        print("df_da:",df_da)

        df_db = df_db.evalf(subs={a: 4, b: 10})

        print("df_db:",df_db)

        term_contribution = (df_da / function_value) * 100
        term_contributions.append(term_contribution)
        print("term_contribution a:",term_contribution)

        term_contribution = (df_db / function_value) * 100
        term_contributions.append(term_contribution)
        print("term_contribution b:",term_contribution)
        
    elif nr_parameters == 3:
        pass
        
    elif nr_parameters == 4:
        pass
        
    elif nr_parameters == 5:
        pass

    return term_contributions


f = "260.328+72.004*a**1*math.log2(a)**2*961.788*b**2*math.log2(b)**1"
nr_parameters = 2
term_contributions = calculate_term_contributions_multi(f, nr_parameters)
print("term_contributions:",term_contributions)
