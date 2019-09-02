import flight_sim               as flight_sim
import dynamic_models.engine    as engine
import time

J270 = engine.Rocket_Motor(270, 2.6)
st = time.time()
sim = flight_sim.perform_flight(J270, 3, 3, 12, 36, 2686, 0.01)
et = time.time()
print "Sim time %9.6f" % (et - st)

with open("test.csv",'w') as fh:
    fh.write("Time,Altitude,Velocity,Acceleration\n")
    apogee = 0
    for entry in sim:
        fh.write("%f,%f,%f,%f\n" % (entry.time_stamp, (entry.altitude- 2686)*3.28084, entry.velocity, entry.acceleration/9.8))
        if(entry.altitude > apogee):
            apogee = entry.altitude
    print (apogee - 2686)*3.28084
