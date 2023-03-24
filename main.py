from function_generator import FunctionGenerator


def main():
    #print("Hello World")
    
    f = FunctionGenerator()
    function = f.get_function()
    print(function)

if __name__ == "__main__":
    main()
