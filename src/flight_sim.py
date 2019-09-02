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

import dynamic_models.drag      as drag
import dynamic_models.engine    as engine
import static_models.nose_cone  as nose_cone

import math

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

def perform_flight(motor_model, rocket_diameter_in, rocket_mass, drogue_size, main_size, start_altitude, delta_t_s):

    flight_model        = []
    current_timestep    = 0

    # Add in first Vehicle State
    flight_model.append(Vehicle_State(current_timestep))
    flight_model[-1].altitude = start_altitude

    # Estimate vehicle coefficient of drag
    rocket_diameter_m   = rocket_diameter_in * 0.0254
    drogue_diameter_m   = drogue_size * 0.0254
    main_diameter_m     = main_size * 0.0254

    coefficient_of_drag = nose_cone.get_cd_for_nosecone_type("vonkarman")
    surface_area        = (rocket_diameter_m / 2.0 ) * (rocket_diameter_m / 2.0 ) * math.pi
    drogue_area         = (drogue_diameter_m / 2.0 ) * (drogue_diameter_m / 2.0 ) * math.pi
    main_area           = (main_diameter_m / 2.0 ) * (main_diameter_m / 2.0 ) * math.pi

    # print "Rocket Area %f" % surface_area

    # Perform the boost phase simulation
    while(current_timestep <= motor_model.burn_time_s):
        #Progress to new timestamp
        current_timestep += delta_t_s

        # Sum all forces

        # Start with motor thrust
        net_force   = motor_model.get_thrust(current_timestep)
        # Subtract force due to gravity
        net_force  -= rocket_mass * 9.8
        # Subtract drag force
        net_force  -= drag.calculate_drag_force(coefficient_of_drag,
                                                flight_model[-1].velocity,
                                                flight_model[-1].altitude,
                                                surface_area)

        # Estimate new state
        net_acceleration    = (net_force / rocket_mass)
        net_velocity        = flight_model[-1].velocity + (net_acceleration * delta_t_s)
        net_altitude        = flight_model[-1].altitude + (net_velocity * delta_t_s)

        # print "Force: %9.3f\tAcceleration: %9.3f\tVelocity %9.3f\tAltitude %9.3f" % (net_force,net_acceleration, net_velocity, net_altitude)

        # Make a new state
        flight_model.append(Vehicle_State(current_timestep))
        flight_model[-1].acceleration   = net_acceleration
        flight_model[-1].velocity       = net_velocity
        flight_model[-1].altitude       = net_altitude
        flight_model[-1].phase          = Vehicle_State.Flight_phases["powered_boost"]

    # print "Boost Complete"

    # Perform coast phase simulation
    while(flight_model[-1].velocity >= 0):
        #Progress to new timestamp
        current_timestep += delta_t_s

        # Sum all forces

        # Start with motor thrust
        net_force   = 0
        # Subtract force due to gravity
        net_force  -= rocket_mass * 9.8
        # Subtract drag force
        net_force  -= drag.calculate_drag_force(coefficient_of_drag,
                                                flight_model[-1].velocity,
                                                flight_model[-1].altitude,
                                                surface_area)

        # Estimate new state
        net_acceleration    = (net_force / rocket_mass)
        net_velocity        = flight_model[-1].velocity + (net_acceleration * delta_t_s)
        net_altitude        = flight_model[-1].altitude + (net_velocity * delta_t_s)

        # Make a new state
        flight_model.append(Vehicle_State(current_timestep))
        flight_model[-1].acceleration   = net_acceleration
        flight_model[-1].velocity       = net_velocity
        flight_model[-1].altitude       = net_altitude
        flight_model[-1].phase          = Vehicle_State.Flight_phases["coast"]
        # print "Acceleration: %9.3f\tVelocity %9.3f\tAltitude %9.3f" % (net_acceleration, net_velocity, net_altitude)



    # print "Coast Complete"

    # Perform drogue phase descent
    while(flight_model[-1].altitude < 228.6):
        #Progress to new timestamp
        current_timestep += delta_t_s

        # Sum all forces

        # Start with motor thrust
        net_force   = 0
        # Subtract force due to gravity
        net_force  -= rocket_mass * 9.8
        # Subtract drag force
        net_force  += drag.calculate_drag_force(0.8,
                                                flight_model[-1].velocity,
                                                flight_model[-1].altitude,
                                                drogue_size)

        # Estimate new state
        net_acceleration    = (net_force / rocket_mass)
        net_velocity        = flight_model[-1].velocity + (net_acceleration * delta_t_s)
        net_altitude        = flight_model[-1].altitude + (net_velocity * delta_t_s)

        # Make a new state
        flight_model.append(Vehicle_State(current_timestep))
        flight_model[-1].acceleration   = net_acceleration
        flight_model[-1].velocity       = net_velocity
        flight_model[-1].altitude       = net_altitude
        flight_model[-1].phase          = Vehicle_State.Flight_phases["drogue_descent"]
        # print "Acceleration: %9.3f\tVelocity %9.3f\tAltitude %9.3f" % (net_acceleration, net_velocity, net_altitude)



    # print "Drogue Complete"

    # Perform main chute phase descent
    while(flight_model[-1].altitude >= start_altitude):
        #Progress to new timestamp
        current_timestep += delta_t_s

        # Sum all forces

        # Start with motor thrust
        net_force   = 0
        # Subtract force due to gravity
        net_force  -= rocket_mass * 9.8
        # Subtract drag force
        net_force  += drag.calculate_drag_force(0.8,
                                                flight_model[-1].velocity,
                                                flight_model[-1].altitude,
                                                drogue_area) + \
                      drag.calculate_drag_force(0.8,
                                                flight_model[-1].velocity,
                                                flight_model[-1].altitude,
                                                main_area)
        # Estimate new state
        net_acceleration    = (net_force / rocket_mass)
        net_velocity        = flight_model[-1].velocity + (net_acceleration * delta_t_s)
        net_altitude        = flight_model[-1].altitude + (net_velocity * delta_t_s)

        # Make a new state
        flight_model.append(Vehicle_State(current_timestep))
        flight_model[-1].acceleration   = net_acceleration
        flight_model[-1].velocity       = net_velocity
        flight_model[-1].altitude       = net_altitude
        flight_model[-1].phase          = Vehicle_State.Flight_phases["main_descent"]
        # print "Acceleration: %9.3f\tVelocity %9.3f\tAltitude %9.3f" % (net_acceleration, net_velocity, net_altitude)



    # The last step put the model under start altitude, make this not possible
    flight_model[-1].altitude       = start_altitude
    flight_model[-1].velocity       = 0
    flight_model[-1].acceleration   = 0
    flight_model[-1].phase          = Vehicle_State.Flight_phases["on_ground"]

    # print "Flight Complete"

    return flight_model