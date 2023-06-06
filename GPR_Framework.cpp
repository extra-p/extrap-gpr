 // libgp - Gaussian process library for Machine Learning
// Copyright (c) 2013, Manuel Blum <mblum@informatik.uni-freiburg.de>
// All rights reserved.


// Gaussian process includes
#include "gp.h"
#include "gp_utils.h"

#include <Eigen/Dense>

// Function generator includes
#include "EXTRAP_FunctionGenerator.hpp"
#include "EXTRAP_CompoundTerm.hpp"

#include "EXTRAP_DataPoint.hpp"

#include "EXTRAP_Coordinate.hpp"

#include "EXTRAP_ModelGeneratorOptions.hpp"
#include "EXTRAP_Types.hpp"
#include "EXTRAP_ExperimentPoint.hpp"
#include "EXTRAP_MultiParameterSparseFunctionModeler.hpp"

#include "EXTRAP_MultiParamFunctionGenerator.hpp"

#include "EXTRAP_CubeFileReader.hpp"

#include <time.h>
#include <thread>

using namespace libgp;
using namespace EXTRAP;

struct TestCase
{
  enum TestStrategy { BUDGET, ACCURACY };
  enum TestMode { FUNCTION, TEXTFILE, CUBEFILE };
};

std::vector<std::vector<Function*>>
generateAssigmentsForThreads( std::vector<Function*>& function_list, unsigned thread_count, unsigned n )
{
  std::vector<std::vector<Function*>> assigned_functions;
  unsigned functions_per_thread = (unsigned) n / thread_count;
  unsigned additional_function = n % thread_count;
  unsigned current_index = 0;

  for( unsigned i = 0; i < thread_count; ++i)
  {
    std::vector<Function*> func;
    for( unsigned j = 0; j < functions_per_thread; ++j)
    {
      func.push_back( function_list[current_index++] );
    }
    if( i < additional_function )
    {
      func.push_back( function_list[current_index++]);
    }
    assigned_functions.push_back( func );
  }
  return assigned_functions;
}

#TODO
void
addMeasurementsToGPR( GaussianProcess& gp, 
                      ExperimentPointList& exp_list, 
                      ParameterList& param_list, 
                      unsigned reps,  
                      std::map<Parameter, double>& normalisation_factors )
{
  for( unsigned i = 0; i < exp_list.size(); ++i)
  {
    const Coordinate& coord = exp_list[i]->getCoordinate();
    double x[ coord.size() ];
    for( unsigned i = 0; i < coord.size(); ++i )
    {
      double temp = 0;

      if( normalisation_factors.size() != 0 )
      {
        temp = coord.find( param_list[i] )->second * normalisation_factors.find( param_list[i] )->second;
      }
      else
      {
        temp = coord.find( param_list[i] )->second;
        //Fix for GP stability
        while( temp < 1 ) temp = temp * 10;
      }

      x[i]  = temp;
    }
    double y = exp_list[i]->getMean();
    gp.add_pattern( x, y );
    i += reps-1;

    // std::cout << "Added Coord: ";
    // for( unsigned i = 0; i < coord.size(); ++i )
    // {
    //   std::cout << param_list[i].getName() << ": " << x[i] << " ";
    // }
    // std::cout << std::endl;
  }
}

void
fillMeasurements( std::vector<Coordinate>& measurementPoints, std::vector<std::pair<Coordinate, std::vector<Value>>>& measurements,
                  Function* function, unsigned reps, double noise )
{
  for( auto coord : measurementPoints)
  {
    std::vector<Value> vals;
    for(unsigned i = 0; i < reps; ++i)
    {
      Value val = function->evaluate( coord );
      double added_noise = drand48() * noise * val;
      ( drand48() < 0.5 ) ? val += added_noise : val -= added_noise;

      vals.push_back(val);
    }
    measurements.push_back( std::make_pair( coord, vals ));
  }
  // std::cout << "Measurement Count: " << measurements.size() << std::endl;
}

void 
fillMeasurements( std::vector<std::pair<Coordinate, std::vector<Value>>>& measurements, std::ifstream& input_stream )
{
  // std::cout << "start" << std::endl;
  while( true )
  {
    std::vector<Value> param_values;
    Coordinate* coord = new Coordinate();

    //Extract param_names and Values
    std::string line;
    std::getline( input_stream, line );

    if( input_stream.eof() ) return;

    auto pos = line.find( "\"params\"" );
    auto end_pos = line.find( "}", pos );
    auto start_pos = line.find( "{", pos );
    std::size_t cut_pos;

    // std::cout << line << std::endl;

    // std::cout << "start: " << start_pos << std::endl;
    // std::cout << "end: " << end_pos << std::endl;

    while( start_pos < end_pos )
    {
      start_pos = line.find( "\"", start_pos );
      cut_pos = line.find( "\"", start_pos + 1 );

      // std::cout << "start: " << start_pos << std::endl;
      // std::cout << "cut: " << cut_pos << std::endl;
      std::string param_name = line.substr( start_pos+1, cut_pos - start_pos - 1 );

      start_pos = line.find( ":", start_pos);
      cut_pos = line.find( ",", start_pos );

      cut_pos = std::min( cut_pos, end_pos );
      auto value_string = line.substr( start_pos+1, cut_pos - start_pos - 1 );
      // std::cout << "value: " << value_string << std::endl;
      // std::cout << "param_name: " << param_name << std::endl;
      Value param_value = std::stod( value_string );
 
      Parameter param( param_name );

      coord->insert( { param, param_value } );
      start_pos = cut_pos;
    }

    //Extract Measurement Value
    pos = line.find( "\"value\"" );
    start_pos = line.find( ":", pos );
    end_pos = line.find( "}", pos );
    auto value_string = line.substr( start_pos+1, start_pos - end_pos - 1 );
    Value param_value = std::stod( value_string );

    //std::cout << "param_value: " << param_value << std::endl;
 
    param_values.push_back( param_value );

    measurements.push_back( std::make_pair( *coord, param_values ) );
    

    //std::cout << "Measurement: " << coord->toString() << " Value: " << param_value << std::endl;
  }
}

void
generateInitialMeasurements( Experiment& experiment, Function* function, ParameterList param_list,
                             Callpath* callpath, Metric* metric, std::vector<DataPoint>& modeledDataPointList,
                             std::vector<std::pair<Coordinate, std::vector<Value>>>& measurements, unsigned reps,
                             double& budget )
{
  Interval interval;

  //Initial Point
  for( unsigned i = 0; i < reps; ++i )
  {
    Coordinate* coord = new Coordinate( measurements[0].first );
    Value val = measurements[0].second.at( i );

    budget -= val * coord->find(param_list[0])->second;

    ExperimentPoint* exp_point = new ExperimentPoint( coord, 1, val, interval, val, val, interval, val, val, callpath, metric );
    experiment.addCoordinate( coord );
    // std::cout << "Added Coordinate: " << coord->toString() << std::endl;
    experiment.addDataPoint( exp_point, *metric, *callpath );

    if( i == 0 ) modeledDataPointList.emplace_back( new Coordinate( *coord ), 1, val, interval );
  }

  for( unsigned param = 0; param < param_list.size(); ++param )
  {
    for( unsigned i = 1; i < 5; ++i )
    {
      for( unsigned j = 0; j < reps; ++j)
      {
        int index = (int) i * std::pow( 5, param );
        Coordinate* coord = new Coordinate( measurements[index].first );
        Value val = measurements[index].second.at(j);

        budget -= val * coord->find(param_list[0])->second;

        ExperimentPoint* exp_point = new ExperimentPoint( coord, 1, val, interval, val, val, interval, val, val, callpath, metric );
        experiment.addCoordinate( coord );
        // std::cout << "Added Coordinate: " << coord->toString() << std::endl;
        experiment.addDataPoint( exp_point, *metric, *callpath );

        if( j == 0 ) modeledDataPointList.emplace_back( new Coordinate( *coord ), 1, val, interval );
      }
    }
  }
}

void
generateReferenceExperiment( Experiment& experiment, Function* function, ParameterList& param_list,
                             Callpath* callpath, Metric* metric, std::vector<DataPoint>& modeledDataPointList,
                             double& budget, std::vector<std::pair<Coordinate, std::vector<Value>>>& measurements,
                             unsigned reps )
{
  Interval interval;
  // int counter = 0;
  for( auto& measurement : measurements )
  {
    // std::cout << "counter: " << ++counter << std::endl;
    double avg = 0;
    for( unsigned i = 0; i < reps; ++i )
    {
      Coordinate* coord = new Coordinate( measurement.first );
      Value val = measurement.second.at(i);
      budget += val * coord->find(param_list[0])->second;
      ExperimentPoint* exp_point = new ExperimentPoint( coord, 1, val, interval, val, val, interval, val, val, callpath, metric );
      experiment.addCoordinate( coord );
      experiment.addDataPoint( exp_point, *metric, *callpath );

      avg += val;
      if( i == reps-1) modeledDataPointList.emplace_back( coord, reps, (avg / reps), interval );
    }
  }
}

double
findLowestDistance( ParameterList& param_list, Coordinate& coord, std::vector<std::pair<Coordinate, std::vector<Value>>>& measurements,
                    std::vector<unsigned>& takenIndices )
{
  double max_distance = std::numeric_limits<double>::max();
  for( auto& index : takenIndices )
  {
    double distance = 0;
    for( unsigned j = 0; j < coord.size(); ++j )
    {
      double x = coord.find( param_list[j] )->second;
      double y = measurements[index].first.find( param_list[j] )->second;
      // std::cout << "X: " << x << std::endl;
      // std::cout << "Y: " << y << std::endl;
      distance += std::pow( x - y, 2 );
      // std::cout << "distance zwischen: " << distance << std::endl;
    }
    distance = std::sqrt( distance );
    // std::cout << "distance end: " << distance << std::endl;
    if( distance < max_distance && distance != 0 ) max_distance = distance;
  }
  // std::cout << "Distance: " << max_distance << std::endl;
  return max_distance;
}

void
generateSparseExperiment( Experiment& experiment, 
                          Function* function, 
                          ParameterList& param_list,
                          Callpath* callpath, 
                          Metric* metric, 
                          std::vector<DataPoint>& modeledDataPointList,
                          std::vector<std::pair<Coordinate, std::vector<Value>>>& measurements, 
                          unsigned reps,
                          double& budget, 
                          std::vector<unsigned>& heatmap, double& additionalPoints, 
                          TestCase::TestStrategy strategy,
                          MultiParameterSparseFunctionModeler* function_modeler, 
                          ModelGeneratorOptions* options,
                          double threshold, 
                          std::pair<Coordinate, Value> accuracy_coodinate )
{
  // std::cout << "enter sparse " << std::endl;
  generateInitialMeasurements( experiment, function, param_list, callpath, metric, modeledDataPointList, measurements, reps, budget );
  std::vector<std::pair<unsigned, double>> costForIndex;
  unsigned counter = 0;
  unsigned expo = 0;
  for( unsigned i = 0; i < std::pow( 5, param_list.size() ); ++i)
  {
    if( i % (int) std::pow(5, expo) == 0)
    {
      counter++;
      if( counter == 5)
      {
        expo++;
        counter = 0;
      }
      continue;
    }
    double cost = 0;
    for( unsigned j = 0; j < reps; ++j)
    {
      cost += measurements[i].second.at(j) * measurements[i].first.find(param_list[0])->second;
    }
    costForIndex.push_back( std::make_pair( i, cost ));
  }

  Interval interval;
  while(true)
  {
    int index = -1;
    double lowest_cost = std::numeric_limits<double>::max();
    for( unsigned i = 0; i < costForIndex.size(); ++i )
    {
      // std::cout << "Index: " << i << " Cost: " << costForIndex[i].second << std::endl;
      if( costForIndex[i].second < lowest_cost )
      {
        lowest_cost = costForIndex[i].second;
        index = i;
      }
    }
    bool cont = false;
    if( strategy == TestCase::TestStrategy::BUDGET )
    {
      if( lowest_cost <= budget && !costForIndex.empty() && index != -1 )
      {
        cont = true;
      }
    }
    else
    {
      if( !costForIndex.empty() && index != -1 )
      {
        cont = true;
      }
    }
    
    if( cont )
    {
      // std::cout << "cont " << std::endl;
      double avg = 0;
      for( unsigned i = 0; i < reps; ++i)
      {
        Coordinate* coord = new Coordinate( measurements[costForIndex[index].first].first );
        Value val = measurements[costForIndex[index].first].second.at(i);

        ExperimentPoint* exp_point = new ExperimentPoint( coord, 1, val, interval, val, val, interval, val, val, callpath, metric );
        experiment.addCoordinate( coord );
        experiment.addDataPoint( exp_point, *metric, *callpath );

        avg += val;
        if( i == reps-1)
        {
          avg = avg / reps;
          modeledDataPointList.emplace_back( coord, reps, avg, interval );
          // std::cout << "Coordinate: " << coord->toString() << std::endl;
        } 
      }
      budget -= lowest_cost;

      //heatmap
      heatmap[costForIndex[index].first]++;

      costForIndex.erase( costForIndex.begin() + index );

      additionalPoints++;

      if( strategy == TestCase::TestStrategy::ACCURACY )
      {
        ModelCommentList comment_list;
        MultiParameterHypothesis hypo = function_modeler->createModel( &experiment, *options, modeledDataPointList,
                                                                       comment_list, nullptr );
        
        double predicted_value = hypo.getFunction()->evaluate( accuracy_coodinate.first );
        double accuracy = std::abs( 1 - ( predicted_value / accuracy_coodinate.second ) );
        // std::cout << "accuracy: " << accuracy << std::endl;
        if( accuracy <= threshold )
        {
          break;
        }
      }
    }
    else
    {
      break;
    }
  }
}

void
generateGPRExperiment( Experiment& experiment,
                       Function* function,
                       ParameterList param_list,
                       Callpath* callpath, 
                       Metric* metric, 
                       std::vector<DataPoint>& modeledDataPointList,
                       std::vector<std::pair<Coordinate, std::vector<Value>>>& measurements, 
                       unsigned reps, 
                       double& budget,
                       GaussianProcess& gp, 
                       std::vector<unsigned>& heatmap, 
                       double& additionalPoints,
                       TestCase::TestStrategy strategy,
                       MultiParameterSparseFunctionModeler* function_modeler,
                       ModelGeneratorOptions* options,
                       double threshold,
                       std::pair<Coordinate, Value>& accuracy_coodinate,
                       std::map<Parameter, double>& normalisation_factors )
{
  generateInitialMeasurements( experiment, function, param_list, callpath, metric, modeledDataPointList, measurements, reps, budget );

  Interval interval;

  double old_value = -1;

  std::vector<std::pair<unsigned, double>> costForIndex;
  unsigned counter = 0;
  unsigned expo = 0;
  for( unsigned i = 0; i < std::pow( 5, param_list.size() ); ++i)
  {
    if( i % (int) std::pow(5, expo) == 0 )
    {
      counter++;
      if( counter == 5)
      {
        expo++;
        counter = 0;
      }
      continue;
    }
    double cost = 0;
    for( unsigned j = 0; j < reps; ++j)
    {
      cost += measurements[i].second.at(j) * measurements[i].first.find(param_list[0])->second;
    }
    costForIndex.push_back( std::make_pair( i, cost ));
  }

  #TODO
  //Train GPR
  ExperimentPointList exp_list = experiment.getPoints( *metric, *callpath );
  addMeasurementsToGPR( gp, exp_list, param_list, reps, normalisation_factors );

  while(true)
  {
    //Filter
    std::vector<unsigned> fittingMeasurements;
    for( unsigned i = 0; i < costForIndex.size(); ++i)
    {
      if( costForIndex[i].second <= budget )
      {
        fittingMeasurements.push_back( i );
      } 
    }

    // std::cout << "fitting: " << fittingMeasurements.size() << std::endl;

    #CONTINUE HERE
    //Find best
    int best_index = -1;
    double best_rated = std::numeric_limits<double>::max();
    for( unsigned& current_index : fittingMeasurements )
    {
      Coordinate& coord = measurements[costForIndex[current_index].first].first;
      double x[ coord.size() ];
      for( unsigned j = 0; j < coord.size(); ++j )
      {
        if( normalisation_factors.size() != 0 )
        {
          x[j] = coord.find( param_list[j] )->second * normalisation_factors.find( param_list[j] )->second;
        }
        else
        {
          x[j] = coord.find( param_list[j] )->second;
        }    
      }
      double rated = std::pow( costForIndex[current_index].second, 2 ) / ( std::pow( std::abs( gp.var( x )), 2 ));
      // std::cout << "rated: " << rated << std::endl;
      // std::cout << "gp: " << gp.var( x ) << std::endl;
      if( rated <= best_rated )
      {
        best_rated = rated;
        best_index = current_index;
      }
    }
    // std::cout << "Best Index: " << best_index << std::endl;
    //Add Measurement
    if( best_index != -1 )
    {
      double avg = 0;
      for( unsigned i = 0; i < reps; ++i)
      {
        Coordinate* coord = new Coordinate( measurements[costForIndex[best_index].first].first );
        Value val = measurements[costForIndex[best_index].first].second.at(i);

        ExperimentPoint* exp_point = new ExperimentPoint( coord, 1, val, interval, val, val, interval, val, val, callpath, metric );
        experiment.addCoordinate( coord );
        experiment.addDataPoint( exp_point, *metric, *callpath );

        avg += val;
        if( i == reps-1)
        {
          // std::cout << "Add to Datapointlist" << std::endl;
          avg = avg / reps;
          modeledDataPointList.emplace_back( coord, reps, avg, interval );

          double x[ coord->size() ];
          for( unsigned i = 0; i < coord->size(); ++i )
          {
            if( normalisation_factors.size() != 0 )
            {
              x[i] = coord->find( param_list[i] )->second * normalisation_factors.find( param_list[i] )->second;
            }
            else
            {
              x[i] = coord->find( param_list[i] )->second;
            }
          }
          gp.add_pattern( x, avg );
        } 
      }

      heatmap[costForIndex[best_index].first]++;
      budget -= costForIndex[best_index].second;
      costForIndex.erase( costForIndex.begin() + best_index );

      additionalPoints++;

      if( strategy == TestCase::TestStrategy::ACCURACY )
      {
        ModelCommentList comment_list;
        MultiParameterHypothesis hypo = function_modeler->createModel( &experiment, *options, modeledDataPointList,
                                                                       comment_list, nullptr );

        Coordinate extraone_coord;
        for( auto& param : param_list )
        {
          extraone_coord.insert( { param, 128 } );
        }
        
        double predicted_value = hypo.getFunction()->evaluate( accuracy_coodinate.first );
        double accuracy = std::abs( 1 - ( predicted_value / accuracy_coodinate.second ) );
        //std::cout << "accuracy: " << accuracy << std::endl;
        if( accuracy <= threshold )
        {
          break;
        }
      }
    }
    else
    {
      break;
    }
  }
}

void generateHybridExperiment( Experiment& experiment,
                               Function* function,
                               ParameterList param_list,
                               Callpath* callpath, 
                               Metric* metric, 
                               std::vector<DataPoint>& modeledDataPointList,
                               std::vector<std::pair<Coordinate, std::vector<Value>>>& measurements, 
                               unsigned reps, 
                               double& budget,
                               GaussianProcess& gp, 
                               std::vector<unsigned>& heatmap, 
                               double& additionalPoints,
                               TestCase::TestStrategy strategy,
                               MultiParameterSparseFunctionModeler* function_modeler,
                               ModelGeneratorOptions* options,
                               double threshold,
                               std::pair<Coordinate, Value>& accuracy_coodinate,
                               std::map<Parameter, double>& normalisation_factors )
{
  generateInitialMeasurements( experiment, function, param_list, callpath, metric, modeledDataPointList, measurements, reps, budget );

  Interval interval;
  double full_budget = budget;

  int added_points = 0;

  std::vector<std::pair<unsigned, double>> costForIndex;
  unsigned counter = 0;
  unsigned expo = 0;
  for( unsigned i = 0; i < std::pow( 5, param_list.size() ); ++i)
  {
    if( i % (int) std::pow(5, expo) == 0 )
    {
      counter++;
      if( counter == 5)
      {
        expo++;
        counter = 0;
      }
      continue;
    }
    double cost = 0;
    for( unsigned j = 0; j < reps; ++j)
    {
      cost += measurements[i].second.at(j) * measurements[i].first.find(param_list[0])->second;
    }
    costForIndex.push_back( std::make_pair( i, cost ));
  }

  //Train GPR
  ExperimentPointList exp_list = experiment.getPoints( *metric, *callpath );
  addMeasurementsToGPR( gp, exp_list, param_list, reps, normalisation_factors );

  while(true)
  {
    //Filter
    std::vector<unsigned> fittingMeasurements;
    for( unsigned i = 0; i < costForIndex.size(); ++i)
    {
      if( costForIndex[i].second <= budget )
      {
        fittingMeasurements.push_back( i );
      } 
    }

    // std::cout << "fitting: " << fittingMeasurements.size() << std::endl;
    //Find best (Hybrid)
  int swtiching_point = 0;
  if( param_list.size() == 3 )
  {
    swtiching_point = 18;
  }
  if( param_list.size() == 2 )
  {
    swtiching_point = 11;
  }
  if( param_list.size() == 4 )
  {
    swtiching_point = 25;
  }

    int best_index = -1;
    if( added_points > swtiching_point )
    {
      // std::cout << "Switch to GPR at: " << added_points << "  Total Budget: " << full_budget << std::endl; 
      double best_rated = std::numeric_limits<double>::max();
      for( unsigned& current_index : fittingMeasurements )
      {
        Coordinate& coord = measurements[costForIndex[current_index].first].first;
        double x[ coord.size() ];
        for( unsigned j = 0; j < coord.size(); ++j )
        {
          if( normalisation_factors.size() != 0 )
          {
            x[j] = coord.find( param_list[j] )->second * normalisation_factors.find( param_list[j] )->second;
          }
          else
          {
            x[j] = coord.find( param_list[j] )->second;
          }    
        }
        double rated = std::pow( costForIndex[current_index].second, 1 ) / ( std::pow( std::abs( gp.var( x )), 2 ));
        if( rated <= best_rated )
        {
          best_rated = rated;
          best_index = current_index;
        }
      }
    }
    else
    {
      // std::cout << "Switch to Sparse at: " << added_points << "  Total Budget: " << full_budget << std::endl; 
      double lowest_cost = std::numeric_limits<double>::max();
      // for( unsigned i = 0; i < costForIndex.size(); ++i )
      for( unsigned& current_index : fittingMeasurements )
      {
        // std::cout << "Index: " << i << " Cost: " << costForIndex[i].second << std::endl;
        if( costForIndex[current_index].second < lowest_cost )
        {
          lowest_cost = costForIndex[current_index].second;
          best_index = current_index;
        }
      }
    }
    

    // std::cout << "Best Index: " << best_index << std::endl;
    //Add Measurement
    if( best_index != -1 )
    {
      double avg = 0;
      for( unsigned i = 0; i < reps; ++i)
      {
        Coordinate* coord = new Coordinate( measurements[costForIndex[best_index].first].first );
        Value val = measurements[costForIndex[best_index].first].second.at(i);

        ExperimentPoint* exp_point = new ExperimentPoint( coord, 1, val, interval, val, val, interval, val, val, callpath, metric );
        experiment.addCoordinate( coord );
        experiment.addDataPoint( exp_point, *metric, *callpath );

        avg += val;
        if( i == reps-1)
        {
          // std::cout << "Add to Datapointlist" << std::endl;
          avg = avg / reps;
          modeledDataPointList.emplace_back( coord, reps, avg, interval );

          double x[ coord->size() ];
          for( unsigned i = 0; i < coord->size(); ++i )
          {
            if( normalisation_factors.size() != 0 )
            {
              x[i] = coord->find( param_list[i] )->second * normalisation_factors.find( param_list[i] )->second;
            }
            else
            {
              x[i] = coord->find( param_list[i] )->second;
            }
          }
          gp.add_pattern( x, avg );
        } 
      }

      heatmap[costForIndex[best_index].first]++;
      budget -= costForIndex[best_index].second;
      // std::cout << "Cost for point: " << costForIndex[best_index].second << std::endl;
      costForIndex.erase( costForIndex.begin() + best_index );

      additionalPoints++;      
      added_points++;
      // std::cout << "add Point " << additionalPoints << std::endl;

      if( strategy == TestCase::TestStrategy::ACCURACY )
      {
        ModelCommentList comment_list;
        MultiParameterHypothesis hypo = function_modeler->createModel( &experiment, *options, modeledDataPointList,
                                                                       comment_list, nullptr );

        Coordinate extraone_coord;
        for( auto& param : param_list )
        {
          extraone_coord.insert( { param, 128 } );
        }
        
        double predicted_value = hypo.getFunction()->evaluate( accuracy_coodinate.first );
        double accuracy = std::abs( 1 - ( predicted_value / accuracy_coodinate.second ) );
        //std::cout << "accuracy: " << accuracy << std::endl;
        if( accuracy <= threshold )
        {
          break;
        }
      }
    }
    else
    {
      break;
    }
  }
  // std::cout << "Added: " << added_points << std::endl;
  // std::cout << "Budget: " << budget/full_budget << std::endl;
}

void
generateDistanceExperiment( Experiment& experiment,
                            Function* function,
                            ParameterList param_list,
                            Callpath* callpath, Metric* metric,
                            std::vector<DataPoint>& modeledDataPointList,
                            std::vector<std::pair<Coordinate, std::vector<Value>>>& measurements,
                            unsigned reps,
                            double& budget,
                            std::vector<unsigned>& heatmap,
                            double& additionalPoints,
                            TestCase::TestStrategy strategy,
                            MultiParameterSparseFunctionModeler* function_modeler,
                            ModelGeneratorOptions* options,
                            double threshold,
                            std::pair<Coordinate, Value> accuracy_coodinate,
                            std::map<Parameter, double>& normalisation_factors )
{
  generateInitialMeasurements( experiment, function, param_list, callpath, metric, modeledDataPointList, measurements, reps, budget );

  Interval interval;

  std::vector<std::pair<unsigned, double>> costForIndex;
  unsigned counter = 0;
  unsigned expo    = 0;
  std::vector<unsigned> takenIndices;
  for( unsigned i = 0; i < std::pow( 5, param_list.size() ); ++i)
  {
    if( i % (int) std::pow(5, expo) == 0)
    {
      counter++;
      if( counter == 5)
      {
        expo++;
        counter = 0;
      }
      takenIndices.push_back( i );
      continue;
    }
    double cost = 0;
    for( unsigned j = 0; j < reps; ++j)
    {
      cost += measurements[i].second.at(j) * measurements[i].first.find(param_list[0])->second;
    }
    costForIndex.push_back( std::make_pair( i, cost ) );
  }

  while(true)
  {
    //Filter
    std::vector<unsigned> fittingMeasurements;
    for( unsigned i = 0; i < costForIndex.size(); ++i)
    {
      if( strategy == TestCase::TestStrategy::BUDGET )
      {
        if( costForIndex[i].second <= budget )
        {
          fittingMeasurements.push_back( i );
        }
      }
      else
      {
        fittingMeasurements.push_back( i );
      }
    }

    //Find best
    int    best_index = -1;
    double best_rated = std::numeric_limits<double>::max();

    for( unsigned& current_index : fittingMeasurements )
    {
      Coordinate& coord = measurements[costForIndex[current_index].first].first;
      double distance   = findLowestDistance( param_list, coord, measurements, takenIndices );
      double rated      = costForIndex[current_index].second / std::pow( distance, 2 );
      
      if( rated <= best_rated )
      {
        best_rated = rated;
        best_index = current_index;
      }
    }

    //Add Measurement
    if( best_index != -1 )
    {
      takenIndices.push_back( best_index );
      double avg = 0;
      for( unsigned i = 0; i < reps; ++i)
      {
        Coordinate* coord = new Coordinate( measurements[costForIndex[best_index].first].first );
        Value val         = measurements[costForIndex[best_index].first].second.at(i);

        ExperimentPoint* exp_point = new ExperimentPoint( coord, 1, val, interval, val, val, interval, val, val, callpath, metric );
        experiment.addCoordinate( coord );
        experiment.addDataPoint( exp_point, *metric, *callpath );

        avg += val;
        if( i == reps-1)
        {
          avg = avg / reps;
          modeledDataPointList.emplace_back( coord, reps, avg, interval );

          double x[ coord->size() ];
          for( unsigned i = 0; i < coord->size(); ++i )
          {
            x[i]  = coord->find( param_list[i] )->second;
          }
        } 
      }

      heatmap[costForIndex[best_index].first]++;
      budget -= costForIndex[best_index].second;
      costForIndex.erase( costForIndex.begin() + best_index );

      additionalPoints++;

      if( strategy == TestCase::TestStrategy::ACCURACY )
      {
        ModelCommentList comment_list;
        MultiParameterHypothesis hypo = function_modeler->createModel( &experiment, *options, modeledDataPointList,
                                                                       comment_list, nullptr );

        Coordinate extraone_coord;
        for( auto& param : param_list )
        {
          extraone_coord.insert( { param, 128 } );
        }
        
        double predicted_value = hypo.getFunction()->evaluate( accuracy_coodinate.first );
        double accuracy = std::abs( 1 - ( predicted_value / accuracy_coodinate.second ) );
        //std::cout << "accuracy: " << accuracy << std::endl;
        if( accuracy <= threshold )
        {
          break;
        }
      }
    }
    else
    {
      break;
    }
  }
}

void
testExperiment( Experiment* experiment,
                MultiParameterSparseFunctionModeler& function_modeler,
                Function* real_function,
                std::vector<DataPoint>& modeledDataPointList,
                ModelGeneratorOptions& options, ParameterList param_list,
                std::vector<double>& exp_points,
                double noise,
                std::vector<std::vector<unsigned>>& buckets,
                std::vector<double>& test_data,
                std::vector<MultiParameterHypothesis>& hypo_container )
{
  ModelCommentList comment_list;
  MultiParameterHypothesis hypo = function_modeler.createModel( experiment, options, modeledDataPointList,
                                                                comment_list, nullptr );
  MultiParameterFunction* hypo_function = hypo.getFunction();

  for( unsigned i = 0; i < exp_points.size(); ++i )
  {
    Coordinate extraone_coord;
    for( auto& param : param_list )
    {
      extraone_coord.insert( { param, exp_points[i] } );
    }

    double predicted_value = hypo_function->evaluate( extraone_coord );
    double real_value = real_function->evaluate( extraone_coord );

    // std::cout << extraone_coord.toString() << std::endl;
    // std::cout << "Real: " << real_value << std::endl;
    // std::cout << "Predicted " << predicted_value << std::endl;

    test_data.push_back( predicted_value );
    //test_data.push_back( real_value );

    double accuracy = 1 - ( predicted_value / real_value );

    //std::cout << "Model: " << hypo_function->getAsString( param_list ) << std::endl;
    //std::cout << "RSS: " << hypo.getrRSS() << std::endl;
    // std::cout << "Accuracy: " << accuracy << std::endl << std::endl;

    if( accuracy < 0.05 * (noise + 1) )
    {
      buckets[0][i]++;
    } 
    else if( accuracy < 0.1 * (noise + 1) )
    {
      buckets[1][i]++;
    }
    else if( accuracy < 0.15 * (noise + 1) )
    {
      buckets[2][i]++;
    }
    else if( accuracy < 0.2 * (noise + 1) )
    {
      buckets[3][i]++;
    }
    else
    {
      buckets[4][i]++;
    }
  }
  hypo_container.push_back( hypo );
}

void testExperimentAtSpecificCoordinate( Experiment* experiment,
                                         MultiParameterSparseFunctionModeler& function_modeler,
                                         std::vector<DataPoint>& modeledDataPointList,
                                         ModelGeneratorOptions& options,
                                         std::pair<Coordinate, Value> test_point,
                                         std::vector<std::vector<unsigned>>& buckets,
                                         std::vector<double>& test_data,
                                         std::vector<MultiParameterHypothesis>& hypo_container,
                                         ParameterList& param_list  )
{
  ModelCommentList comment_list;
  MultiParameterHypothesis hypo = function_modeler.createModel( experiment, options, modeledDataPointList,
                                                                comment_list, nullptr );
  // std::cout << "Before 1" << std::endl;
  MultiParameterFunction* hypo_function = hypo.getFunction();
  // std::cout << "Before 2" << std::endl;
  double predicted_value = hypo_function->evaluate( test_point.first );
  // std::cout << "Before 3" << std::endl;
  // test_data.push_back( predicted_value );
  // std::cout << "Before 4" << std::endl;

  
  double accuracy = 1 - ( predicted_value / test_point.second );
  accuracy = std::abs( accuracy );
  std::cout << "Model: " << hypo_function->getAsString( param_list ) << std::endl;
  std::cout << "RSS: " << hypo.getrRSS() << std::endl;
  std::cout << "Acc: " << accuracy << std::endl << std::endl;

  // std::cout << "Before Buckets" << std::endl;

  if( accuracy < 0.05 )
  {
   buckets[0][0]++;
  } 
  else if( accuracy < 0.1 )
  {
    buckets[1][0]++;
  }
  else if( accuracy < 0.15 )
  {
    buckets[2][0]++;
  }
  else if( accuracy < 0.2 )
  {
    buckets[3][0]++;
  }
  else
  {
    buckets[4][0]++;
  }
  // std::cout << "Before pushback" << std::endl;
  hypo_container.push_back( hypo );
  // std::cout << "Done" << std::endl;
}

void
generateModels( std::vector<Function*>& function_list, 
                std::vector<std::vector<std::vector<unsigned>>>& buckets,
                std::vector<std::vector<unsigned>>& heat_maps,
                std::vector<double>& additional_points, 
                std::vector<std::vector<std::vector<double>>>& test_data,
                std::vector<std::vector<MultiParameterHypothesis>>& hypothesis,
                std::vector<std::vector<double>>& budget_collection,
                unsigned reps,
                double noise, 
                unsigned dim, 
                ParameterList& param_list, 
                ModelGeneratorOptions& options,
                std::vector<Coordinate>& measurementPoints,
                TestCase::TestStrategy strategy,
                double threshold,
                double relative_budget,
                bool normalisation )
{ 
  auto function_modeler = MultiParameterSparseFunctionModeler();

  // unsigned gpr_additionalPoints    = 0;
  // unsigned sparse_additionalPoints = 0;
  // unsigned dist_additionalPoints   = 0;

  std::map<Parameter, double> normalisation_factors;

  #NORM
  if( normalisation )
  {
    for( auto& param : param_list )
    {
      double param_value_max = -1;
      // double param_value_min = std::numeric_limits<double>::max();
      for( unsigned i = 0; i < measurementPoints.size(); ++i )
      {
        Coordinate& coord = measurementPoints[i];
        auto const& temp = coord.find( param.getName() );

        if( param_value_max < temp->second )
        {
          param_value_max = temp->second;
        }

        // if( param_value_min > temp->second )
        // {
        //   param_value_min = temp->second;
        // }
      }
      param_value_max = 100 / param_value_max ;
      std::cout << "Normalisation Factor for " << param.getName() << ": " << param_value_max << std::endl;
      normalisation_factors.insert( { param, param_value_max } );
    }
  }

  for( unsigned i = 0; i < function_list.size(); ++i )
  //for( auto& function : function_list )
  {
    test_data.push_back( std::vector<std::vector<double>>( 6, std::vector<double>() ) );

    hypothesis.push_back( std::vector<MultiParameterHypothesis>() );

    budget_collection.push_back( std::vector<double>() );

    std::vector<double> extrapolation_points{ 128, 256, 512 };

    //fill in ground truth values
    for( auto exp_p : extrapolation_points )
    {
      Coordinate extraone_coord;
      for( auto& param : param_list )
      {
        extraone_coord.insert( { param, exp_p } );
      }
      double real_value = function_list[i]->evaluate( extraone_coord );
      test_data[i][0].push_back( real_value );
    }
    
    //Generate Accuracy Coodinate    
    Coordinate coord;
    for( auto& param : param_list )
    {
      coord.insert( { param, 256 } );
    }
    std::pair<Coordinate, Value> accuracy_point( coord, function_list[i]->evaluate( coord ) );
    
    double budget = 0;
    std::vector<std::pair<Coordinate, std::vector<Value>>> measurements;
    fillMeasurements( measurementPoints, measurements, function_list[i], reps, noise );
    
    //Reference Experiment
    Experiment ref_experiment;
    Metric*    ref_metric   = new Metric( "x", "t" );
    Region*    ref_region   = new Region( "r", "file", 1 );
    Callpath*  ref_callpath = new Callpath( ref_region, nullptr );

    ref_experiment.addMetric( ref_metric );
    ref_experiment.addRegion( ref_region );
    ref_experiment.addCallpath( ref_callpath );

    std::vector<DataPoint> refDataPointList;

    for( auto& param : param_list )
    {
      ref_experiment.addParameter( param );
    }
  
    generateReferenceExperiment( ref_experiment, function_list[i], param_list, ref_callpath, ref_metric, refDataPointList, budget, measurements, reps );

    testExperiment( &ref_experiment, function_modeler, function_list[i], refDataPointList, options, param_list, extrapolation_points, noise, buckets[0], test_data[i][1], hypothesis[i] );

    //testExperimentAtSpecificCoordinate( &ref_experiment, function_modeler, refDataPointList, options, test_value, test_coord, buckets[0], test_data[i][1], hypothesis[i] );
    budget_collection[i].push_back( budget );

    double ref_budget;
    double total_budget = budget;

    if( strategy == TestCase::TestStrategy::BUDGET )
    {
      ref_budget = budget * relative_budget;
    }
    else
    {
      ref_budget = budget;
    }  

    //Sparse Experiment
    Experiment sparse_experiment;
    Metric*   metric   = new Metric( "x", "t" );
    Region*   region   = new Region( "r", "file", 1 );
    Callpath* callpath = new Callpath( region, nullptr );

    sparse_experiment.addMetric( metric );
    sparse_experiment.addRegion( region );
    sparse_experiment.addCallpath( callpath );

    budget = ref_budget;

    std::vector<DataPoint> sparseDataPointList;

    for( auto& param : param_list)
    {
      sparse_experiment.addParameter( param );
    }

    generateSparseExperiment( sparse_experiment, function_list[i], param_list, callpath, metric,
                              sparseDataPointList, measurements, reps, budget, heat_maps[0],
                              additional_points[0], strategy, &function_modeler, &options, threshold,
                              accuracy_point );
    
    testExperiment( &sparse_experiment, function_modeler, function_list[i], sparseDataPointList, options, param_list, extrapolation_points, noise, buckets[1], test_data[i][2], hypothesis[i] );
    // std::cout << "Budget Sparse: " << total_budget - ( ref_budget - budget ) << std::endl;
    //testExperimentAtSpecificCoordinate( &sparse_experiment, function_modeler, sparseDataPointList, options, test_value, test_coord, buckets[1], test_data[i][2], hypothesis[i] );
    budget_collection[i].push_back( ref_budget - budget );

    //GPR Experiment
    Experiment gpr_experiment;

    Metric*   gpr_metric   = new Metric( "x", "t" );
    Region*   gpr_region   = new Region( "r", "file", 1 );
    Callpath* gpr_callpath = new Callpath( gpr_region, nullptr );

    gpr_experiment.addMetric( gpr_metric );
    gpr_experiment.addRegion( gpr_region );
    gpr_experiment.addCallpath( gpr_callpath );

    //Setup GPR
    std::string cov = "CovMatern5iso";
    GaussianProcess gp( dim, cov );
    Eigen::VectorXd gpr_params( gp.covf().get_param_dim() );
    gpr_params << 5.0, 0.0;
    gp.covf().set_loghyper( gpr_params );

    std::vector<DataPoint> gprDatapointList;

    for( auto& param : param_list)
    {
      gpr_experiment.addParameter( param );
    }

    budget = ref_budget;

    generateGPRExperiment( gpr_experiment, function_list[i], param_list, gpr_callpath, gpr_metric,
                           gprDatapointList, measurements, reps, budget, gp, heat_maps[1],
                           additional_points[1], strategy, &function_modeler, &options, threshold,
                           accuracy_point, normalisation_factors );

    testExperiment( &gpr_experiment, function_modeler, function_list[i], gprDatapointList, options, param_list, extrapolation_points, noise, buckets[2], test_data[i][3], hypothesis[i] );

    //testExperimentAtSpecificCoordinate( &gpr_experiment, function_modeler, gprDatapointList, options, test_value, test_coord, buckets[2], test_data[i][3], hypothesis[i] );
    // std::cout << "Budget GPR: " << total_budget - ( ref_budget - budget ) << std::endl;
    budget_collection[i].push_back( ref_budget - budget );

    budget = ref_budget;

    //Distance Experiment
    Experiment hybrid_experiment;

    Metric*   hybrid_metric   = new Metric( "x", "t" );
    Region*   hybrid_region   = new Region( "r", "file", 1 );
    Callpath* hybrid_callpath = new Callpath( hybrid_region, nullptr );

    hybrid_experiment.addMetric( hybrid_metric );
    hybrid_experiment.addRegion( hybrid_region );
    hybrid_experiment.addCallpath( hybrid_callpath );

    std::vector<DataPoint> hybridDatapointList;

    //Setup GPR
    // std::string cov = "CovMatern5iso";
    GaussianProcess gp_h( dim, cov );
    Eigen::VectorXd gpr_params_h( gp_h.covf().get_param_dim() );
    // gpr_params << 5.0, 0.0;
    gpr_params_h << 5.0, 0.0;
    gp_h.covf().set_loghyper( gpr_params_h );

    for( auto& param : param_list)
    {
      hybrid_experiment.addParameter( param );
    }

    budget = ref_budget;

    generateHybridExperiment( hybrid_experiment, function_list[i], param_list, hybrid_callpath, hybrid_metric,
                              hybridDatapointList, measurements, reps, budget, gp_h, heat_maps[2],
                              additional_points[2], strategy, &function_modeler, &options, threshold,
                              accuracy_point, normalisation_factors );
  

    testExperiment( &hybrid_experiment, function_modeler, function_list[i], hybridDatapointList, options, param_list, extrapolation_points, noise, buckets[3], test_data[i][4], hypothesis[i] );

    // std::cout << "Budget Hyb: " << total_budget - ( ref_budget - budget ) << std::endl;
    // std::cout << "Total Sparse: " << total_budget << std::endl;
    // std::cout << "Budget Sparse rel: " <<  (total_budget - ( ref_budget - budget )) / total_budget << std::endl;

    budget_collection[i].push_back( ref_budget - budget );

    //Distance Experiment
    Experiment dist_experiment;

    Metric*   dist_metric   = new Metric( "x", "t" );
    Region*   dist_region   = new Region( "r", "file", 1 );
    Callpath* dist_callpath = new Callpath( dist_region, nullptr );

    dist_experiment.addMetric( dist_metric );
    dist_experiment.addRegion( dist_region );
    dist_experiment.addCallpath( dist_callpath );

    std::vector<DataPoint> distDatapointList;

    for( auto& param : param_list)
    {
      dist_experiment.addParameter( param );
    }

    budget = ref_budget;

    generateDistanceExperiment( dist_experiment, function_list[i], param_list, dist_callpath, dist_metric,
                                distDatapointList, measurements, reps, budget, heat_maps[3],
                                additional_points[3], strategy, &function_modeler, &options, threshold,
                                accuracy_point, normalisation_factors );
  

    testExperiment( &dist_experiment, function_modeler, function_list[i], distDatapointList, options, param_list, extrapolation_points, noise, buckets[4], test_data[i][5], hypothesis[i] );

    //testExperimentAtSpecificCoordinate( &dist_experiment, function_modeler, distDatapointList, options, test_value, test_coord, buckets[3], test_data[i][4], hypothesis[i] );

    budget_collection[i].push_back( ref_budget - budget );

    std::cout << "Done with function_number: " << i << std::endl;
  }
  std::cout << "Thread done " << std::endl;
}

void
generateModelsWithMeasurements( std::vector<std::vector<std::vector<unsigned>>>& buckets,
                                std::vector<std::vector<unsigned>>& heat_maps,
                                std::vector<double>& additional_points, 
                                std::vector<std::vector<std::vector<double>>>& test_data,
                                std::vector<std::vector<MultiParameterHypothesis>>& hypothesis,
                                std::vector<std::vector<double>>& budget_collection,
                                std::vector<std::vector<std::pair<Coordinate, std::vector<Value>>>>& measurement_list,
                                unsigned reps,
                                unsigned dim, 
                                ParameterList& param_list, 
                                ModelGeneratorOptions& options,
                                double threshold,
                                double relative_budget,
                                unsigned& filter_count,
                                bool normalisation,
                                TestCase::TestStrategy strategy ) 
{
  auto function_modeler = MultiParameterSparseFunctionModeler();

  std::map<Parameter, double> normalisation_factors;

  if( normalisation )
  {
    for( auto& param : param_list )
    {
      double param_value_max = -1;
      // double param_value_min = std::numeric_limits<double>::max();
      for( unsigned i = 0; i < measurement_list[0].size(); ++i )
      {
        Coordinate& coord = measurement_list[0][i].first;
        auto const& temp = coord.find( param.getName() );

        if( param_value_max < temp->second )
        {
          param_value_max = temp->second;
        }

        // if( param_value_min > temp->second )
        // {
        //   param_value_min = temp->second;
        // }
      }
      param_value_max = 100 / param_value_max;
      std::cout << "Normalisation Factor for " << param.getName() << ": " << param_value_max << std::endl;
      normalisation_factors.insert( {param, param_value_max} );
    }

    // for( auto& measurements : measurement_list )
    // {
    //   for( auto& measurement : measurements )
    //   {
    //     Coordinate& coord = measurement.first;
    //     for( auto& factor : normalisation_factors )
    //     {
    //       coord.find( factor.first )->second *= factor.second;
    //     }
    //   }
    // }
  }
  
  for( unsigned i = 0; i < measurement_list.size(); ++i )
  {
    std::vector<std::pair<Coordinate, std::vector<Value>>> measurements = measurement_list[i];
    test_data.push_back( std::vector<std::vector<double>>( 5, std::vector<double>() ) );

    hypothesis.push_back( std::vector<MultiParameterHypothesis>() );

    budget_collection.push_back( std::vector<double>() );

    for( auto& measurement : measurements )
    {
      std::cout << measurement.first.toString() << "    Value: " << measurement.second[0] << std::endl;
    }

    int index = 0;
    bool invalid = false;
    bool zero = true;
    for( int j = 1; j < measurements.size(); ++j )
    {
      // std::cout << "Measurement: " << measurements[j].first.toString() << " Value: " << measurements[j].second[0] << std::endl;
      if( measurements[j].second[0] < 0 ) invalid = true;
      zero &= ( measurements[j].second[0] == 0 );

      if( measurements[j].second[0] > measurements[index].second[0] )
      {
        index = j;
      }
    }

    if( invalid || zero ) 
    {
      std::cout << "filtered!" << std::endl;
      filter_count++;
      budget_collection[i].push_back( 0 );
      continue;
    }

    if( measurements.size() < std::pow(5, dim) )
    {
      std::cout << "Not enough measurements: Filtered" << std::endl;
      std::cout << "Measurement Count: " << measurements.size() << std::endl;
      budget_collection[i].push_back( 0 );
      filter_count++;
      continue;
    }

    double cost = 0;
    for( unsigned j = 0; j < measurements[index].second.size(); ++j )
    {
      cost += measurements[index].second.at(j);
    }

    std::pair<Coordinate, Value> test_point = std::make_pair( measurements[index].first, cost );
    measurements.erase( measurements.begin() + index );

    // std::cout << "found test point: " << test_point.first.toString() << " Value: " << test_point.second << std::endl;

    // std::vector<double> extrapolation_points{ 128, 256, 512 };

    //fill in ground truth values
    // for( auto exp_p : extrapolation_points )
    // {
    //   Coordinate extraone_coord;
    //   for( auto& param : param_list )
    //   {
    //     extraone_coord.insert( { param, exp_p } );
    //   }
    //   double real_value = function_list[i]->evaluate( extraone_coord );
    //   test_data[i][0].push_back( real_value );
    // }
    
    
    double budget = 0;
    // std::vector<std::pair<Coordinate, std::vector<Value>>> measurements;
    // fillMeasurements( measurementPoints, measurements, function_list[i], reps, noise );

    //Reference Experiment
    Experiment ref_experiment;
    Metric*    ref_metric   = new Metric( "x", "t" );
    Region*    ref_region   = new Region( "r", "file", 1 );
    Callpath*  ref_callpath = new Callpath( ref_region, nullptr );

    ref_experiment.addMetric( ref_metric );
    ref_experiment.addRegion( ref_region );
    ref_experiment.addCallpath( ref_callpath );

    std::vector<DataPoint> refDataPointList;

    for( auto& param : param_list )
    {
      ref_experiment.addParameter( param );
    }
  
    generateReferenceExperiment( ref_experiment, nullptr, param_list, ref_callpath, ref_metric, refDataPointList, budget, measurement_list[i], reps );

    // testExperiment( &ref_experiment, function_modeler, function_list[i], refDataPointList, options, param_list, extrapolation_points, noise, buckets[0], test_data[i][1], hypothesis[i] );
    testExperimentAtSpecificCoordinate( &ref_experiment, function_modeler, refDataPointList, options, test_point, buckets[0], test_data[i][1], hypothesis[i], param_list );

    budget_collection[i].push_back( budget );

    double ref_budget;

    ref_budget = budget * relative_budget;    

    //Sparse Experiment
    Experiment sparse_experiment;
    Metric*   metric   = new Metric( "x", "t" );
    Region*   region   = new Region( "r", "file", 1 );
    Callpath* callpath = new Callpath( region, nullptr );

    sparse_experiment.addMetric( metric );
    sparse_experiment.addRegion( region );
    sparse_experiment.addCallpath( callpath );

    budget = ref_budget;

    std::vector<DataPoint> sparseDataPointList;

    for( auto& param : param_list)
    {
      sparse_experiment.addParameter( param );
    }
    generateSparseExperiment( sparse_experiment, nullptr, param_list, callpath, metric,
                              sparseDataPointList, measurement_list[i], reps, budget, heat_maps[0],
                              additional_points[0], strategy, &function_modeler, &options, threshold,
                              test_point );
    
    // testExperiment( &sparse_experiment, function_modeler, function_list[i], sparseDataPointList, options, param_list, extrapolation_points, noise, buckets[1], test_data[i][2], hypothesis[i] );

    testExperimentAtSpecificCoordinate( &sparse_experiment, function_modeler, sparseDataPointList, options, test_point, buckets[1], test_data[i][2], hypothesis[i], param_list );

    budget_collection[i].push_back( ref_budget - budget );

    #TODO
    //GPR Experiment
    Experiment gpr_experiment;

    Metric*   gpr_metric   = new Metric( "x", "t" );
    Region*   gpr_region   = new Region( "r", "file", 1 );
    Callpath* gpr_callpath = new Callpath( gpr_region, nullptr );

    gpr_experiment.addMetric( gpr_metric );
    gpr_experiment.addRegion( gpr_region );
    gpr_experiment.addCallpath( gpr_callpath );

    //Setup GPR
    std::string cov = "CovMatern5iso";
    GaussianProcess gp( dim, cov );
    Eigen::VectorXd gpr_params( gp.covf().get_param_dim() );
    gpr_params << 5.0, 0.0;
    gp.covf().set_loghyper( gpr_params );

    std::vector<DataPoint> gprDatapointList;

    for( auto& param : param_list)
    {
      gpr_experiment.addParameter( param );
    }

    budget = ref_budget;

    generateGPRExperiment( gpr_experiment, nullptr, param_list, gpr_callpath, gpr_metric,
                              gprDatapointList, measurement_list[i], reps, budget, gp, heat_maps[1],
                              additional_points[1], strategy, &function_modeler, &options, threshold,
                              test_point, normalisation_factors );

    // testExperiment( &gpr_experiment, function_modeler, function_list[i], gprDatapointList, options, param_list, extrapolation_points, noise, buckets[2], test_data[i][3], hypothesis[i] );

    testExperimentAtSpecificCoordinate( &gpr_experiment, function_modeler, gprDatapointList, options, test_point, buckets[2], test_data[i][3], hypothesis[i], param_list );

    budget_collection[i].push_back( ref_budget - budget );

    budget = ref_budget;


    //Hybrid Experiment
    Experiment hybrid_experiment;

    Metric*   hybrid_metric   = new Metric( "x", "t" );
    Region*   hybrid_region   = new Region( "r", "file", 1 );
    Callpath* hybrid_callpath = new Callpath( hybrid_region, nullptr );

    hybrid_experiment.addMetric( hybrid_metric );
    hybrid_experiment.addRegion( hybrid_region );
    hybrid_experiment.addCallpath( hybrid_callpath );

    //Setup Hybrid
    std::string cov_h = "CovMatern5iso";
    GaussianProcess gp_h( dim, cov_h );
    Eigen::VectorXd hybrid_params( gp_h.covf().get_param_dim() );
    hybrid_params << 5.0, 0.0;
    gp_h.covf().set_loghyper( hybrid_params );

    std::vector<DataPoint> hybridDatapointList;

    for( auto& param : param_list)
    {
      hybrid_experiment.addParameter( param );
    }

    budget = ref_budget;

    generateHybridExperiment( hybrid_experiment, nullptr, param_list, hybrid_callpath, hybrid_metric,
                              hybridDatapointList, measurement_list[i], reps, budget, gp_h, heat_maps[2],
                              additional_points[2], strategy, &function_modeler, &options, threshold,
                              test_point, normalisation_factors );

    // testExperiment( &gpr_experiment, function_modeler, function_list[i], gprDatapointList, options, param_list, extrapolation_points, noise, buckets[2], test_data[i][3], hypothesis[i] );

    testExperimentAtSpecificCoordinate( &hybrid_experiment, function_modeler, hybridDatapointList, options, test_point, buckets[3], test_data[i][4], hypothesis[i], param_list );
    budget_collection[i].push_back( ref_budget - budget );

    budget = ref_budget;

    //Distance Experiment
    Experiment dist_experiment;

    Metric*   dist_metric   = new Metric( "x", "t" );
    Region*   dist_region   = new Region( "r", "file", 1 );
    Callpath* dist_callpath = new Callpath( dist_region, nullptr );

    dist_experiment.addMetric( dist_metric );
    dist_experiment.addRegion( dist_region );
    dist_experiment.addCallpath( dist_callpath );

    std::vector<DataPoint> distDatapointList;

    for( auto& param : param_list)
    {
      dist_experiment.addParameter( param );
    }

    budget = ref_budget;

    generateDistanceExperiment( dist_experiment, nullptr, param_list, dist_callpath, dist_metric,
                                distDatapointList, measurement_list[i], reps, budget, heat_maps[3],
                                additional_points[3], strategy, &function_modeler, &options, threshold,
                                test_point, normalisation_factors );

    // testExperiment( &dist_experiment, function_modeler, function_list[i], distDatapointList, options, param_list, extrapolation_points, noise, buckets[3], test_data[i][4], hypothesis[i] );
    testExperimentAtSpecificCoordinate( &dist_experiment, function_modeler, distDatapointList, options, test_point, buckets[4], test_data[i][5], hypothesis[i], param_list );

    budget_collection[i].push_back( ref_budget - budget );

    std::cout << "Done with function_number: " << i << std::endl;
  }
}                                

void
printResultsToFile( std::vector<std::vector<Function*>> function_list,
                    // std::vector<std::vector<std::vector<std::vector<unsigned>>>>& assigned_buckets,
                    // std::vector<std::vector<std::vector<unsigned>>>& heat_maps,
                    // std::vector<std::vector<double>>& additional_points,
                    std::vector<std::vector<std::vector<std::vector<double>>>>& test_data,
                    std::vector<std::vector<std::vector<MultiParameterHypothesis>>>& hypothesis,
                    std::string& filename,
                    ParameterList param_list )
{
  std::ofstream outfile ( filename );
  for( unsigned i = 0; i < function_list.size(); ++i )
  {
    for( unsigned j = 0; j < function_list[i].size(); ++j )
    {
      //Print ground truth
      outfile << function_list[i][j]->getAsString( param_list ) << ",";
      for( unsigned k = 0; k < 3; ++k )
      {
        outfile << test_data[i][j][0][k] << ",";
      }

      //Print reference
      outfile << hypothesis[i][j][0].getFunction()->getAsString( param_list ) << ",";
      for( unsigned k = 0; k < 3; ++k )
      {
        outfile << test_data[i][j][1][k] << ",";
      }

      //Print sparse
      outfile << hypothesis[i][j][1].getFunction()->getAsString( param_list ) << ",";
      for( unsigned k = 0; k < 3; ++k )
      {
        outfile << test_data[i][j][2][k] << ",";
      }

      //Print gpr
      outfile << hypothesis[i][j][2].getFunction()->getAsString( param_list ) << ",";
      for( unsigned k = 0; k < 3; ++k )
      {
        outfile << test_data[i][j][3][k] << ",";
      }

      //Print distance
      outfile << hypothesis[i][j][0].getFunction()->getAsString( param_list ) << ",";
      for( unsigned k = 0; k < 3; ++k )
      {
        outfile << test_data[i][j][4][k] << ",";
      }
      outfile << ";" << std::endl;
    }
  }
  outfile.close();
}

int
main (int argc, char const *argv[])
{
  //Initialize Variables to default values.
  int n = 100;
  double min = 0, max= 128;
  unsigned thread_count = 0;
  bool debug = false, generate_graph = false, params_set = false, print_results = false, big_test = false, BNMPP=false, normalisation = false;
  std::string      cov        = "CovMatern5iso";
  std::string      gpr_params = "";
  std::string      filename   = "output.csv";
  FunctionCategory category   = FunctionCategory::COMMON_CAT;

  //Default parameter Values
  std::vector<Value>     p1 = {  8, 16, 32, 64, 128 };
  // std::vector<Value> p1 = { 10, 100, 1000, 10000, 100000 };
  std::vector<Value>     p2 = { 8, 16, 32, 64, 128 };
  // std::vector<Value> p2 = { 10, 100, 1000, 10000, 100000 };
  std::vector<Value>     p3 = { 8, 16, 32, 64, 128 };
  std::vector<Value>     p4 = { 8, 16, 32, 64, 128 };

  std::vector<Function*> function_list;

  //List of Parameternames
  ParameterList          param_list;

  //Modeler Data
  std::vector<DataPoint> datapoint_list;
  ModelCommentList       comment_list;
  Function               function;

  unsigned dim        = 2;
  unsigned reps       = 5;
  double   noise      = 0.05;
  double   threshold  = 1000;
  double   relative_budget = 0.15;

  unsigned model_count = 0;

  TestCase::TestStrategy strategy = TestCase::TestStrategy::BUDGET;
  TestCase::TestMode testMode = TestCase::TestMode::FUNCTION;

  ModelGeneratorOptions options;
  options.setSinglePointsStrategy( SparseModelerSingleParameterStrategy::FIRST_POINTS_FOUND );
  options.setUseAddPoints( true );
  options.setMultiPointsStrategy( SparseModelerMultiParameterStrategy::INCREASING_COST );
  options.setNumberAddPoints( 1 );
  options.setGenerateModelOptions( GENERATE_MODEL_MEAN );
  options.setMinNumberPoints( 5 );

  //init some values
  srand( time(0) );
  std::ofstream out( filename );

  //Read out arguments
  for( unsigned i = 1; i < argc; ++i)
  {
    //std::cout << argv[i] << "\n";
    //Number of functions to be generated and tested.
    if( strcmp(argv[i], "-n") == 0 )
    {
      n = std::stoi(argv[++i]);
    } 
    else if( strcmp(argv[i], "-dim") == 0 )
    {
      dim = std::stoi(argv[++i]);
    }
    else if( strcmp(argv[i], "-reps") == 0 )
    {
      reps = std::stoi(argv[++i]);
    }
    else if( strcmp(argv[i], "-noise") == 0 )
    {
      noise = std::stod(argv[++i]);
    }
    else if( strcmp(argv[i], "-thread") == 0 )
    {
      thread_count = std::stoi(argv[++i]);
    }
    else if( strcmp(argv[i], "-thresh") == 0 )
    {
      threshold = std::stod(argv[++i]);
    }
    else if( strcmp(argv[i], "-out") == 0)
    {
      filename = argv[++i];
    }
    else if( strcmp(argv[i], "-b") == 0 )
    {
      relative_budget = std::stod(argv[++i]);
    }
    else if( strcmp(argv[i], "-norm") == 0 || strcmp(argv[i], "-normalisation") == 0)
    {
      normalisation = true;
    }
    else if( strcmp(argv[i], "-strategy") == 0)
    {
      i++;
      if( strcmp( argv[i], "budget" ) == 0 )
      {
        strategy = TestCase::TestStrategy::BUDGET;
      }
      else if( strcmp( argv[i], "accuracy" ) == 0 )
      {
        strategy = TestCase::TestStrategy::ACCURACY;
      }
    }
    else if( strcmp( argv[i], "-mode") == 0 )
    {
      i++;
      if( strcmp( argv[i], "textfile" ) == 0 )
      {
        testMode = TestCase::TestMode::TEXTFILE;
      }
      else if( strcmp( argv[i], "cubefile" ) == 0 )
      {
        testMode = TestCase::TestMode::CUBEFILE;
      }
    }
    else
    {
      std::cout << "Warning: Unregonized parameter: " << argv[i] << std::endl;
    }
  }

  //Init unset params
  for( unsigned i = 0; i < dim; ++i)
  {
    char char_param = 'a';
    std::string param;
    char_param += i;
    param.push_back(char_param);
    param_list.push_back(Parameter(param));
  }



  //Init all values
  auto function_modeler = MultiParameterSparseFunctionModeler();

  //Number of threads
  if( thread_count == 0 )
  {
    thread_count = std::thread::hardware_concurrency();
    std::cout << "number of threads: " << thread_count << std::endl;
  }

  

  //generate return buckets
  std::vector<std::vector<std::vector<std::vector<unsigned>>>> 
    assigned_buckets( thread_count, std::vector<std::vector<std::vector<unsigned>>>( 5, std::vector<std::vector<unsigned>>( 5, std::vector<unsigned>( 4, 0 ))));

  //generate heat maps
  std::vector<std::vector<std::vector<unsigned>>> heat_maps( thread_count, std::vector<std::vector<unsigned>>( 4, std::vector<unsigned> ( (int) std::pow( 5 , dim ), 0 ) ));

  //generate point counter
  std::vector<std::vector<double>> additional_points( thread_count, std::vector<double>( 4, 0 )); 

  //generate test data container
  std::vector<std::vector<std::vector<std::vector<double>>>> test_data( thread_count, std::vector<std::vector<std::vector<double>>>());

  //generate function container
  std::vector<std::vector<std::vector<MultiParameterHypothesis>>> hypothesis( thread_count, std::vector<std::vector<MultiParameterHypothesis>>() );

  //generate budget counter
  std::vector<std::vector<std::vector<double>>> budget_collection( thread_count, std::vector<std::vector<double>>() );
  
  unsigned ref_buckets[5][3]    = { 0 };
  unsigned sparse_buckets[5][3] = { 0 };
  unsigned gpr_buckets[5][3]    = { 0 };
  unsigned hybrid_buckets[5][3] = { 0 };
  unsigned dist_buckets[5][3]   = { 0 };

  unsigned sparse_heat_map[ (int) std::pow( 5 , dim ) ]  = { 0 };
  unsigned gpr_heat_map[ (int) std::pow( 5 , dim ) ]     = { 0 };
  unsigned hybrid_heat_map[ (int) std::pow( 5 , dim ) ]  = { 0 };
  unsigned dist_heat_map[ (int) std::pow( 5 , dim ) ]    = { 0 };

  double sparse_additionalPoints = 0;
  double gpr_additionalPoints    = 0;
  double hybrid_additionalPoints = 0;
  double dist_additionalPoints   = 0;

  //generate all measurementpoints
  std::vector<Coordinate> measurementPoints;

  std::vector<std::vector<Value>> paramValues;
  paramValues.push_back(p1);
  paramValues.push_back(p2);
  paramValues.push_back(p3);
  paramValues.push_back(p4);

    // Switch mode
  // Generate functions
  if( testMode == TestCase::TestMode::FUNCTION )
  {
    model_count = n;

    auto functionGen = MultiParamFunctionGenerator( category, dim, param_list, 0, time(0) );

    for( unsigned i = 0; i<n; ++i)
    {
      function_list.push_back( functionGen.getFunction() );
    }
    //Assign functions to threads
    auto assigned_functions = generateAssigmentsForThreads( function_list, thread_count, n );

    for( unsigned i = 0; i < std::pow( 5, dim ); ++i)
    {
      Coordinate coord;

      for( unsigned j = 0; j < dim; ++j )
      {
        int c = (int) i / std::pow( 5, j );
        c = c % 5;
        double k = paramValues[j][c];
        coord.insert( {param_list[j], k} );
      }
      measurementPoints.push_back(coord);
    }

    if( thread_count > 1 )
    {
      std::vector<std::thread> threads;
      for( unsigned i = 0; i < thread_count; ++i)
      {
        std::cout << "start thread: " << i << std::endl;
        std::thread th( generateModels, std::ref(assigned_functions[i]), std::ref(assigned_buckets[i]), std::ref(heat_maps[i]), std::ref(additional_points[i]),
                        std::ref(test_data[i]), std::ref(hypothesis[i]), std::ref(budget_collection[i]), reps, noise, dim, std::ref(param_list), std::ref(options), std::ref(measurementPoints),
                        strategy, threshold, relative_budget, normalisation );
        threads.push_back( std::move(th) );
      }
      for( auto& th : threads )
      {
        std::cout << "wait to finish" << std::endl;
        th.join();
        std::cout << "joined" << std::endl;
      }
    }
    else
    {
      generateModels( assigned_functions[0], assigned_buckets[0], heat_maps[0], additional_points[0], test_data[0], hypothesis[0], budget_collection[0],
                      reps, noise, dim, param_list, options, measurementPoints, strategy, threshold, relative_budget, normalisation );
    }
    printResultsToFile( assigned_functions, test_data, hypothesis, filename, param_list );
  } 
  else if( testMode == TestCase::TestMode::TEXTFILE )
  {
    unsigned filter_count = 0;

    ParameterList preset_params;
    preset_params.push_back( Parameter( "p" ) );
    preset_params.push_back( Parameter( "size" ) );
    preset_params.push_back( Parameter( "t" ) );

    //Testfile TestCoord
    Coordinate test_coord;
    Parameter param_1( "p" );
    Parameter param_2( "size" );
    Parameter param_3( "t" );
    test_coord.insert( { param_1, 512 } );
    test_coord.insert( { param_2, 9000 } );
    test_coord.insert( { param_3, 0.3 } );

    Value test_value = 2000;

    std::pair<Coordinate, Value> test_point = std::make_pair( test_coord, test_value );

    std::ifstream textfile;
    textfile.open("relearn_results.txt");

    std::vector<std::pair<Coordinate, std::vector<Value>>> measurements;
    fillMeasurements( measurements, textfile );

    std::vector<std::vector<std::pair<Coordinate, std::vector<Value>>>> measurement_list;
    measurement_list.push_back( measurements );

    generateModelsWithMeasurements( assigned_buckets[0], heat_maps[0], additional_points[0], test_data[0], hypothesis[0], budget_collection[0], measurement_list,
                                    reps, dim, preset_params, options, threshold, relative_budget, filter_count, normalisation, strategy );

    model_count = measurement_list.size() - filter_count;
                                    
  }
  else if( testMode == TestCase::TestMode::CUBEFILE )
  {
    // std::string dir = "/home/bn/GPR/Test_Daten/Kripke_3_param";
    // std::string dir = "/home/bn/GPR/Test_Daten/lulesh/scorep/strong";
    std::string dir = "/home/bn/GPR/Test_Daten/milc_scorep_trajecs";
    // std::string dir = "/home/bn/milc/milc_scorep_test";
    std::string prefix = "milc";
    std::string postfix = "";
    std::string cubeFileName = "milc";
    ParameterList parameters;
    std::vector<std::string>      parameterPrefixes;
    std::vector<std::vector<int>> parameterValues;

    // parameters.push_back( Parameter( "p" ) );
    // parameters.push_back( Parameter( "size" ) );

    parameters.push_back( Parameter( "p" ) );
    parameters.push_back( Parameter( "size" ) );
    parameters.push_back( Parameter( "trajecs" ) );

    // parameters.push_back( Parameter( "p" ) );
    // parameters.push_back( Parameter( "d" ) );
    // parameters.push_back( Parameter( "g" ) );

    std::vector<int> param_values_1;

    // param_values_1.push_back(8);
    // param_values_1.push_back(27);
    // param_values_1.push_back(64);
    // param_values_1.push_back(125);
    // param_values_1.push_back(216);
    // param_values_1.push_back(343);

    // param_values_1.push_back(64);
    // param_values_1.push_back(216);
    // param_values_1.push_back(512);
    // param_values_1.push_back(1000);
    // param_values_1.push_back(1728);

    // param_values_1.push_back(256);
    // param_values_1.push_back(512);
    // param_values_1.push_back(1024);
    // param_values_1.push_back(2048);
    // param_values_1.push_back(4096);

    // param_values_1.push_back(16);
    // param_values_1.push_back(32);
    // param_values_1.push_back(64);
    // param_values_1.push_back(128);
    // param_values_1.push_back(256);

    param_values_1.push_back(24);
    param_values_1.push_back(48);
    param_values_1.push_back(96);
    param_values_1.push_back(192);
    param_values_1.push_back(384);

  //  param_values_1.push_back(8);
  //  param_values_1.push_back(64);
  //  param_values_1.push_back(512);
  //  param_values_1.push_back(4096);
  //  param_values_1.push_back(32768);

    std::vector<int> param_values_2;

    // param_values_2.push_back(1);
    // param_values_2.push_back(2);
    // param_values_2.push_back(4);
    // param_values_2.push_back(8);
    // param_values_2.push_back(16);

    // param_values_2.push_back(5);
    // param_values_2.push_back(10);
    // param_values_2.push_back(15);
    // param_values_2.push_back(20);
    // param_values_2.push_back(25);

    param_values_2.push_back(16);
    param_values_2.push_back(32);
    param_values_2.push_back(64);
    param_values_2.push_back(128);
    param_values_2.push_back(256);
    // param_values_2.push_back(512);

    // param_values_2.push_back(2);
  //  param_values_2.push_back(4);
  //  param_values_2.push_back(6);
  //  param_values_2.push_back(8);
  //  param_values_2.push_back(10);
  //  param_values_2.push_back(12);

      // param_values_2.push_back(4);
      // param_values_2.push_back(8);
      // param_values_2.push_back(12);
      // param_values_2.push_back(16);
      // param_values_2.push_back(20);



    std::vector<int> param_values_3;

    // param_values_3.push_back(32);
    // param_values_3.push_back(64);
    // param_values_3.push_back(96);
    // param_values_3.push_back(128);
    // param_values_3.push_back(160);

    // param_values_3.push_back(18);
    // param_values_3.push_back(36);
    // param_values_3.push_back(54);
    // param_values_3.push_back(72);
    // param_values_3.push_back(90);

      param_values_2.push_back(4);
      param_values_2.push_back(8);
      param_values_2.push_back(12);
      param_values_2.push_back(16);
      param_values_2.push_back(20);

    parameterValues.push_back( param_values_1 );
    parameterValues.push_back( param_values_2 );
    parameterValues.push_back( param_values_3 );

    parameterPrefixes.push_back( "" );
    parameterPrefixes.push_back( "" );
    parameterPrefixes.push_back( "" );

    CubeFileReader cube_reader;
    cube_reader.prepareCubeFileReader( 0, dir, prefix, postfix, cubeFileName, parameters, parameterPrefixes, parameterValues, 1 );

    // std::cout << "prepare done" << std::endl;

    Experiment* cube_experiment = cube_reader.readCubeFiles( dim );

    CallpathList const& callpaths = cube_experiment->getAllCallpaths();
    RegionList const& regions = cube_experiment->getRegions();
    MetricList const& metrics = cube_experiment->getMetrics();

    CallpathList const& root_callpaths = cube_experiment->getRootCallpaths();

    Value combined_root_cost = 0;

    for( auto const* metric_temp : metrics )
    {
      std::cout << "metric: " << metric_temp->getName() << std::endl;
      if( strcmp( metric_temp->getName().c_str(), "time" ) == 0 )
      {
        Value root_cost = 0;
        for( auto& root_callpath : root_callpaths )
        {
          ExperimentPointList const& exp_list = cube_experiment->getPoints( *metric_temp, *root_callpath );
          for( auto* exp : exp_list )
          {
            std::cout << "Root Cost Candidate: " << root_cost << std::endl;
            root_cost = ( exp->getMean() > root_cost ) ? exp->getMean() : root_cost;
          }
        }
        std::cout << "Root Cost picked: " << root_cost << std::endl;
        combined_root_cost += root_cost;
      }
    }

    std::cout << "Combined Root Cost: " << combined_root_cost << std::endl;

    std::vector<ExperimentPointList> measurements_exp;

    Value total_runtime = 0;

    for( auto const& call_temp : callpaths )
    {
      for( auto const* metric_temp : metrics )
      {
        // std::cout << "metric: " << metric_temp->getName() << std::endl;
        if( strcmp( metric_temp->getName().c_str(), "time" ) == 0 )
        {
          ExperimentPointList const& exp_list = cube_experiment->getPoints( *metric_temp, *call_temp );
          Value val = 0;
          for( auto* exp : exp_list )
          {
            // val +=exp->getMean();
            val = ( exp->getMean() > val ) ? exp->getMean() : val;
          }
          // std::cout << "Value: " << val << std::endl;
          // if( val > combined_root_cost * 0.10 )
          // {
            // std::cout << "Callpath: " << call_temp->getFullName() << std::endl;
            std::cout << "Inserted Value: " << val << std::endl;
            total_runtime += val;
            measurements_exp.push_back( exp_list );
          // }
        }
      }
    }
    std::cout << "Total Runtime: " << total_runtime << std::endl;
    std::vector<std::vector<std::pair<Coordinate, std::vector<Value>>>> measurements_list;

    for( auto& exp_list : measurements_exp )
    {
      Value val = 0;
      for( auto* exp : exp_list )
      {
        val = ( exp->getMean() > val ) ? exp->getMean() : val;
      }
      if( val >=  total_runtime * 0.01 )
      {
        std::cout << "Val: " << val << std::endl;
        std::vector<std::pair<Coordinate, std::vector<Value>>> measurement;
        for( auto* exp : exp_list )
        {
          std::vector<Value> value;
          value.push_back( exp->getMean() );
          measurement.push_back( { exp->getCoordinate(), value } ); 
        }
      measurements_list.push_back( measurement );
      }
    }

    // return EXIT_SUCCESS;

    // std::cout << "size " << measurements_list.size() << std::endl;

    unsigned filter_count = 0;

    generateModelsWithMeasurements( assigned_buckets[0], heat_maps[0], additional_points[0], test_data[0], hypothesis[0], budget_collection[0], measurements_list,
                                    reps, dim, parameters, options, threshold, relative_budget, filter_count, normalisation, strategy );
    model_count = measurements_list.size() - filter_count;
  }
  
  

  for( unsigned i = 0; i < thread_count; ++i )
    {
      for( unsigned j = 0; j < 5; ++j )
      {
        for( unsigned k = 0; k < 3; ++k )
        {
          ref_buckets[j][k]    += assigned_buckets[i][0][j][k];
          sparse_buckets[j][k] += assigned_buckets[i][1][j][k];
          gpr_buckets[j][k]    += assigned_buckets[i][2][j][k];
          hybrid_buckets[j][k] += assigned_buckets[i][3][j][k];
          dist_buckets[j][k]   += assigned_buckets[i][4][j][k];
        }
      }

      for( unsigned j = 0; j < std::pow( 5, dim ); ++j )
      {
        sparse_heat_map[j] += heat_maps[i][0][j];
        gpr_heat_map[j]    += heat_maps[i][1][j];
        hybrid_heat_map[j] += heat_maps[i][2][j];
        dist_heat_map[j]   += heat_maps[i][3][j];
      }

      sparse_additionalPoints += additional_points[i][0];
      gpr_additionalPoints    += additional_points[i][1];
      hybrid_additionalPoints += additional_points[i][2];
      dist_additionalPoints   += additional_points[i][3];
    }

  //Calculate Average Relative Budget

  double sparse_budget   = 0;
  double gpr_budget      = 0;
  double hybrid_budget   = 0;
  double distance_budget = 0;

  for( unsigned i = 0; i < budget_collection.size(); ++i )
  {
    for( unsigned j = 0; j < budget_collection[i].size(); ++j )
    {
      double ref_budget = budget_collection[i][j][0];
      if( ref_budget == 0 ) continue;
      sparse_budget     += 1 - ( ref_budget - budget_collection[i][j][1] ) / ref_budget;
      gpr_budget        += 1 - ( ref_budget - budget_collection[i][j][2] ) / ref_budget;
      hybrid_budget     += 1 - ( ref_budget - budget_collection[i][j][3] ) / ref_budget;
      distance_budget   += 1 - ( ref_budget - budget_collection[i][j][4] ) / ref_budget;

    }
  }

  sparse_budget   /= model_count;
  gpr_budget      /= model_count;
  hybrid_budget   /= model_count;
  distance_budget /= model_count;

  std::cout << "model count: " << model_count << std::endl;


  std::cout << "Reference Buckets" << std::endl;
  for( int i = 0; i < 5; ++i )
  {
    std::cout << "Bucket " << i << "  contains: " << ref_buckets[i][0] << std::endl;
  }
  std::cout << std::endl;

  std::cout << "Sparse Buckets: Avg Point: " << sparse_additionalPoints/model_count << "  Avg Budget: " << sparse_budget << std::endl;
  for( int i = 0; i < 5; ++i )
  {
    std::cout << "Bucket " << i << "  contains: " << sparse_buckets[i][0] << std::endl;
  }
  std::cout << std::endl;

  std::cout << "GPR Buckets: Avg Point: " << gpr_additionalPoints/model_count << "  Avg Budget: " << gpr_budget << std::endl;
  for( int i = 0; i < 5; ++i )
  {
    std::cout << "Bucket " << i << "  contains: " << gpr_buckets[i][0] << std::endl;
  }
  std::cout << std::endl;

  std::cout << "Hybrid Buckets: Avg Point: " << hybrid_additionalPoints/model_count << "  Avg Budget: " << hybrid_budget << std::endl;
  for( int i = 0; i < 5; ++i )
  {
    std::cout << "Bucket " << i << "  contains: " << hybrid_buckets[i][0] << std::endl;
  }
  std::cout << std::endl;

  std::cout << "Distance Buckets: Avg Point " << dist_additionalPoints/model_count << "  Avg Budget: " << distance_budget << std::endl;
  for( int i = 0; i < 5; ++i )
  {
    std::cout << "Bucket " << i << "  contains: " << dist_buckets[i][0] << std::endl;
  }

  std::cout << "Sparse Heat Map" << std::endl;
  for( unsigned i = 0; i < std::pow(5 ,dim); ++i)
  {
    if( i%5 == 0 && i != 0) std::cout << std::endl;
    std::cout << " " << sparse_heat_map[i] << " ";
  }
  std::cout << std::endl << std::endl;

  std::cout << "GPR Heat Map" << std::endl;
  for( unsigned i = 0; i < std::pow(5 , dim); ++i)
  {
    if( i%5 == 0 && i != 0) std::cout << std::endl;
    std::cout << " " << gpr_heat_map[i] << " ";
  }
  std::cout << std::endl << std::endl;

  std::cout << "Hybrid Heat Map" << std::endl;
  for( unsigned i = 0; i < std::pow(5 , dim); ++i)
  {
    if( i%5 == 0 && i != 0) std::cout << std::endl;
    std::cout << " " << hybrid_heat_map[i] << " ";
  }
  std::cout << std::endl << std::endl;

  std::cout << "Distance Heat Map" << std::endl;
  for( unsigned i = 0; i < std::pow(5 , dim); ++i)
  {
    if( i%5 == 0 && i != 0) std::cout << std::endl;
    std::cout << " " << dist_heat_map[i] << " ";
  }
  std::cout << std::endl;

  return EXIT_SUCCESS;
}

