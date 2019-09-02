###########################################################
#
#   FILENAME:       drag.py
#
#   AUTHOR:         Will B.
# 
#   DESCRIPTION:    Basic drag model
#
###########################################################

import math

#   RETURNS         kg/m^3
def get_air_density_from_altitude(altitude_m):
    # Use NASA's atmospheric model to calculate air pressure
    # https://www.grc.nasa.gov/WWW/k-12/airplane/atmosmet.html

    temperature_c   = 0
    pressure_kpa    = 0

    # Upper Stratosphere Equation
    if(altitude_m > 25000):
        temperature_c   = -131.21 + (0.00299 * altitude_m)
        pressure_kpa    = 2.488 * math.pow( (temperature_c + 273.1)/216.6, -11.388)
    
    # Lower Stratosphere Equation
    elif(altitude_m > 11000):
        temperature_c   = -56.46
        pressure_kpa    = 22.65 * math.pow( math.e, 1.73 - (0.000157 * altitude_m) )
    
    # Troposhere Equation
    elif(altitude_m > 0):
        temperature_c   = 15.04 - (0.00649 * altitude_m)
        pressure_kpa    = 101.29 * math.pow( (temperature_c + 273.1)/288.08, 5.256)

    #Fault Handling
    else:
        raise   ValueError("Altitude cannot be negative")

    #Calculate density from temperature and pressure
    density_kg_p_m3     = pressure_kpa / (0.2869 * (temperature_c + 273.1))

    return density_kg_p_m3


#   RETURNS         N
def calculate_drag_force(coefficient_of_drag, velocity, altitude, reference_surface_area):
    # Use NASA's drag force equation
    # https://www.grc.nasa.gov/www/k-12/airplane/drageq.html

    # Calculate air density
    density_kp_p_m3     = get_air_density_from_altitude(altitude)

    # Calculate drag
    drag_n              = coefficient_of_drag * density_kp_p_m3 * velocity * velocity * reference_surface_area * 0.5
    return drag_n