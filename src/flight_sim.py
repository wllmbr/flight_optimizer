###########################################################
#
#   FILENAME:       flight_sim.py
#
#   AUTHOR:         Will B.
#
#   DESCRIPTION:    Contains main subroutine for simulating
#                       a vehicle's flight
#
###########################################################

import src.dynamic_models.drag      as drag
import src.dynamic_models.engine    as engine
import src.static_models.nose_cone  as nose_cone

import math
import time
import numpy

class Vehicle_State:

    Flight_phases = {
        "powered_boost"     : 0,
        "coast"             : 1,
        "drogue_descent"    : 2,
        "main_descent"      : 3,
        "on_ground"         : 4
    }

    def __init__(self, time_stamp):
        self.altitude       = 0
        self.velocity       = 0
        self.acceleration   = 0
        self.time_stamp     = time_stamp
        self.phase          = Vehicle_State.Flight_phases["on_ground"]

def validate_sim_time(start_time):
    if(time.time() > (start_time + 1)):
        return False
    return True

def perform_flight(motor_model, rocket_diameter_in, rocket_mass, drogue_size, main_size, start_altitude, delta_t_s):

    # Only give the sim a little bit of time to run
    sim_start_time      = time.time()
    flight_model        = []

    # Check to make sure the input parameters make sense
    if(rocket_diameter_in == 0):
        return flight_model
    elif(rocket_mass == 0):
        return flight_model
    elif(delta_t_s == 0):
        return flight_model

    current_timestep    = 0

    # Add in first Vehicle State
    flight_model.append(Vehicle_State(current_timestep))
    start_altitude /= 3.28084
    flight_model[-1].altitude = start_altitude 

    # Estimate vehicle coefficient of drag
    rocket_diameter_m   = rocket_diameter_in * 0.0254
    drogue_diameter_m   = drogue_size * 0.0254
    main_diameter_m     = main_size * 0.0254

    coefficient_of_drag = nose_cone.get_cd_for_nosecone_type("vonkarman")
    rocket_area         = (rocket_diameter_m / 2.0 ) * (rocket_diameter_m / 2.0 ) * math.pi
    drogue_area         = (drogue_diameter_m / 2.0 ) * (drogue_diameter_m / 2.0 ) * math.pi
    main_area           = (main_diameter_m / 2.0 ) * (main_diameter_m / 2.0 ) * math.pi

    # print("Rocket Area %f" % surface_area)

    # Run full model
    current_state = Vehicle_State.Flight_phases["powered_boost"]
    while(flight_model[-1].altitude >= start_altitude):

        #Progress to new timestamp
        current_timestep += delta_t_s

        # Gather Forces
        motor_force = 0
        drag_force = 0

        # Add in Motor Thrust
        if(current_state == Vehicle_State.Flight_phases["powered_boost"]):
            motor_force = motor_model.get_thrust(current_timestep)
        else:
            motor_force = 0

        # Get Drag force
        if((current_state == Vehicle_State.Flight_phases["powered_boost"]) or (current_state == Vehicle_State.Flight_phases["coast"])):
            # If we're powered or coast only the drag of the vehicle is applied
            drag_force = drag.calculate_drag_force(coefficient_of_drag,
                                                    flight_model[-1].velocity,
                                                    flight_model[-1].altitude,
                                                    rocket_area)

        if((current_state == Vehicle_State.Flight_phases["drogue_descent"]) or (current_state == Vehicle_State.Flight_phases["main_descent"])):
            # If we're descending always have the drogue force applied
            drag_force = drag.calculate_drag_force(coefficient_of_drag,
                                                    flight_model[-1].velocity,
                                                    flight_model[-1].altitude,
                                                    drogue_area)

        if((current_state == Vehicle_State.Flight_phases["main_descent"])):
            # Add the main to the force of the drogue
            drag_force += drag.calculate_drag_force(coefficient_of_drag,
                                                    flight_model[-1].velocity,
                                                    flight_model[-1].altitude,
                                                    main_area)


        # Drag force is always applied in the opposite direction of velocity
        drag_direction = numpy.sign(flight_model[-1].velocity) * -1

        net_force = motor_force + (drag_direction *drag_force)

        # Calculate acceleration
        net_acceleration    = (net_force / rocket_mass) - 9.8

        # Estimate new state
        net_velocity        = flight_model[-1].velocity + (net_acceleration * delta_t_s)
        net_altitude        = flight_model[-1].altitude + (net_velocity * delta_t_s)

        # print("Force: %9.3f\tAcceleration: %9.3f\tVelocity %9.3f\tAltitude %9.3f" % (net_force,net_acceleration, net_velocity, net_altitude))

        # Make a new state
        flight_model.append(Vehicle_State(current_timestep))
        flight_model[-1].acceleration   = net_acceleration
        flight_model[-1].velocity       = net_velocity
        flight_model[-1].altitude       = net_altitude
        flight_model[-1].phase          = current_state

        # Determine Next State
        if(current_state == Vehicle_State.Flight_phases["powered_boost"]):
            #Check if the motor is still burning
            if(current_timestep <= motor_model.burn_time_s):
                # We're still in boost phase
                current_state = Vehicle_State.Flight_phases["powered_boost"]
            else:
                # Transition to coast phase
                current_state = Vehicle_State.Flight_phases["coast"]

        elif(current_state == Vehicle_State.Flight_phases["coast"]):
            # Check if we've started descending 
            if(flight_model[-1].velocity >= 0):
                # Stay
                current_state = Vehicle_State.Flight_phases["coast"]
            else:
                # Transition to drogue phase
                current_state = Vehicle_State.Flight_phases["drogue_descent"]

        elif(current_state == Vehicle_State.Flight_phases["drogue_descent"]):
            # Check if we're above main deployment
            if(flight_model[-1].altitude > (228.6+start_altitude)):
                # Stay
                current_state = Vehicle_State.Flight_phases["drogue_descent"]
            else:
                # Transition to main_descent phase
                current_state = Vehicle_State.Flight_phases["main_descent"]

        elif(current_state == Vehicle_State.Flight_phases["main_descent"]):
            #Check if we've hit the ground
            if(flight_model[-1].altitude >= start_altitude):
                # Stay
                current_state = Vehicle_State.Flight_phases["main_descent"]
            else:
                # Transition to drogue phase
                current_state = Vehicle_State.Flight_phases["on_ground"]


    # The last step put the model under start altitude, make this not possible
    flight_model[-1].altitude       = start_altitude
    flight_model[-1].velocity       = 0
    flight_model[-1].acceleration   = 0
    flight_model[-1].phase          = Vehicle_State.Flight_phases["on_ground"]

    # print("Flight Complete")

    return flight_model

if __name__ == '__main__':
    motor_model = engine.Rocket_Motor(270, 2.6)
    with open("test.csv",'w') as fh:
        sim = perform_flight( motor_model,
                             3.0,
                             1.5,
                             15,
                             48,
                             8801,
                             0.1
                             )
        for entry in sim:
            fh.write("%9.6f,%9.6f,%9.6f,%9.6f,%d\n" % (entry.altitude, entry.velocity, entry.acceleration, entry.time_stamp, entry.phase))