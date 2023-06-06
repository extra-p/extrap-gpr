

def add_measurements_to_gpr(gaussian_process, 
                            selected_coordinates, 
                            measurements, 
                            callpath, 
                            metric,
                            normalization_factors,
                            parameters):

    X = []
    Y = []

    for coordinate in selected_coordinates:
        
        x = []

        parameter_values = coordinate.as_tuple()

        for j in range(len(parameter_values)):

            temp = 0

            if len(normalization_factors) != 0:
                temp = parameter_values[j] * normalization_factors[parameters[j]]

            else:
                temp = parameter_values[j]
                while temp < 1:
                    temp = temp * 10
                    
            x.append(temp)

        for measurement in measurements[(callpath, metric)]:
            if measurement.coordinate == coordinate:
                Y.append(measurement.mean)
                break
        
        X.append(x)

    gaussian_process.fit(X, Y)

    return gaussian_process


def add_measurement_to_gpr(gaussian_process, 
                            coordinate, 
                            measurements, 
                            callpath, 
                            metric,
                            normalization_factors,
                            parameters):

    X = []
    Y = []
    x = []

    parameter_values = coordinate.as_tuple()

    for j in range(len(parameter_values)):

        temp = 0

        if len(normalization_factors) != 0:
            temp = parameter_values[j] * normalization_factors[parameters[j]]

        else:
            temp = parameter_values[j]
            while temp < 1:
                temp = temp * 10
                
        x.append(temp)

    for measurement in measurements[(callpath, metric)]:
        if measurement.coordinate == coordinate:
            Y.append(measurement.mean)
            break
    
    X.append(x)

    gaussian_process.fit(X, Y)

    return gaussian_process



    


