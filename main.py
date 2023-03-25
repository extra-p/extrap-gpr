from function_generator import FunctionGenerator


def main():
    #print("Hello World")
    
    f = FunctionGenerator(2)
    function = f.generate_function()
    print("function:",function.function)
    result = f.evaluate_function(function, 4, 10)
    print("result:",result)

if __name__ == "__main__":
    main()
