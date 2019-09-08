import src.flight_sim               as flight_sim
import src.dynamic_models.engine    as engine
import src.grapher.data_input       as data_input
import time
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QSlider, QLabel, QLineEdit)
import pyqtgraph as pg
import time
import threading
import os
import io
import sys

# Surpress STDOUT

# dev_null = io.StringIO()
# sys.stdout = dev_null
# sys.stderr = dev_null

app = QtGui.QApplication([])

window = QtGui.QWidget()
window.setWindowTitle("Flight Designer")

## Create some widgets to be placed inside
plot            = pg.PlotWidget()
global p1
p1              = plot.getPlotItem()
apogee_label    = QLabel()
global apogee_value
apogee_value    = QLabel()
global warning_label
warning_label   = QLabel()

## Create a grid layout to manage the widgets size and position
layout = QtGui.QGridLayout()

## Add widgets to the layout in their proper positions
plot_rows = 16
plot_cols = 6
layout.addWidget(plot, 0, 0, plot_rows, plot_cols)
layout.addWidget(apogee_label,  plot_rows, 0, 1, 1)
layout.addWidget(apogee_value,  plot_rows, 1, 1, 1)
layout.addWidget(warning_label, plot_rows, 2, 4, 1)

apogee_label.setText("Apogee AGL (f)")

p1.setLabel('bottom',text="Time (s)")
p1.setLabel('left',text="Altitude (ft)")
p1.showGrid(True,True)

global die
die = False

global input_list
input_list = []


global sim
sim = []

def update_screen():
    global p1
    global apogee_value
    global warning_label
    global input_list
    global sim

    # Process everything in input_list
    for entry in input_list:
        entry.process()

    if(sim == None):
        warning_label.setText("Sim is taking too long")
        # Sim took too long
    else:
        warning_label.setText("")

        apogee = 0
        # Clear 
        plot.getPlotItem().clear()
        x_vals = []
        a_vals = []
        v_vals = []
        y_vals = []

        for entry in sim:

            #Convert altitude
            alt = entry.altitude * 3.28084
            alt -= input_list[6].cur_val

            #Find Apogee
            if alt > apogee:
                apogee = alt
            # Add point to plot
            x_vals.append(entry.time_stamp)
            y_vals.append(alt)
            a_vals.append(entry.acceleration)
            v_vals.append(entry.velocity)

        #Make a PlotDataItem and add it to the graph
        pdi_altitude = pg.PlotDataItem(x_vals, y_vals)
        pen_altitude = pg.mkPen('b')
        pdi_altitude.setPen(pen_altitude)

        pdi_accel       = pg.PlotDataItem(x_vals, a_vals)
        pen_accel       = pg.mkPen('r')
        pdi_accel.setPen(pen_accel)

        pdi_vel       = pg.PlotDataItem(x_vals, v_vals)
        pen_vel       = pg.mkPen('g')
        pdi_vel.setPen(pen_vel)

        p1.clear()
        p1.addItem(pdi_altitude)
        p1.addItem(pdi_accel)
        p1.addItem(pdi_vel)

        apogee_value.setText("%4.3f" % apogee)

row_index = 0

input_list.append(data_input.Variable_Widget(layout, row_index, plot_cols, "Thrust",            "N",    160,    2560,   update_screen))
row_index += 2
input_list.append(data_input.Variable_Widget(layout, row_index, plot_cols, "Burn Time",         "S",    0.5,    10,     update_screen))
row_index += 2
input_list.append(data_input.Variable_Widget(layout, row_index, plot_cols, "Vehicle Diameter",  "in",   0.7,    6,      update_screen))
row_index += 2
input_list.append(data_input.Variable_Widget(layout, row_index, plot_cols, "Vehicle Mass",      "kg",   0.25,   20,     update_screen))
row_index += 2
input_list.append(data_input.Variable_Widget(layout, row_index, plot_cols, "Drogue Size",       "in",   12,     16,     update_screen))
row_index += 2
input_list.append(data_input.Variable_Widget(layout, row_index, plot_cols, "Main Size",         "in",   0,      49,     update_screen))
row_index += 2
input_list.append(data_input.Variable_Widget(layout, row_index, plot_cols, "Launch Altitude",   "ft",   0,      8868,   update_screen))
row_index += 2

input_list[0].set_val(270)
input_list[1].set_val(2.6)
input_list[2].set_val(3)
input_list[3].set_val(2.9)
input_list[4].set_val(18)
input_list[5].set_val(48)
input_list[6].set_val(8864)

#Force column relative layout
for i in range(0,plot_cols + 5):
    layout.setColumnStretch(i,1)


def execute_simulation(il):
    global die
    global sim
    last_time = time.time()

    while(not(die)):
        # continue
        time.sleep(0.2)
        # Process all of the widgets
        should_process = False
        for w in il:
            # Assume that we don't need to process but if anyone changed we do
            if(w.updated == True):
                should_process = True

        if(should_process):
            # print("Executing Sim")
            # Make the motor model
            motor_model = engine.Rocket_Motor(input_list[0].cur_val, input_list[1].cur_val)

            # Update the sim
            sim = flight_sim.perform_flight(    motor_model,
                                                input_list[2].cur_val,
                                                input_list[3].cur_val,
                                                input_list[4].cur_val,
                                                input_list[5].cur_val,
                                                input_list[6].cur_val,
                                                0.01
                                        )
    

thr = threading.Thread(target=execute_simulation, args=(input_list,))
thr.start()

window.setLayout(layout)
## Display the widget as a new window
window.show()

## Start the Qt event loop
app.exec_()
# Shutting down
die = True
# Give the thread a chance to re join
thr.join(1)

#The thread didn't join, so uncondinationally kill the whole processes
# print("Killing")