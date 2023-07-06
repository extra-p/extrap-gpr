from extrap.entities.coordinate import Coordinate

def add_measurements_to_gpr(gaussian_process, 
                            selected_coordinates, 
                            measurements, 
                            callpath, 
                            metric,
                            normalization_factors,
                            parameters,
                            eval_point):

    X = []
    Y = []

    for coordinate in selected_coordinates:
        
        x = []

        eval_cord = None
        if len(parameters) == 2:
            eval_cord = Coordinate(float(eval_point[0]), float(eval_point[1]))
        elif len(parameters) == 3:
            eval_cord = Coordinate(float(eval_point[0]), float(eval_point[1]), float(eval_point[2]))
        elif len(parameters) == 4:
            eval_cord = Coordinate(float(eval_point[0]), float(eval_point[1]), float(eval_point[2]), float(eval_point[3]))
        else:
            return 1

        if coordinate != eval_cord:

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
