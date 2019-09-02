import flight_sim               as flight_sim
import dynamic_models.engine    as engine
import grapher.data_input       as data_input
import time
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QSlider, QLabel, QLineEdit)
import pyqtgraph as pg
import time
import threading
import os

app = QtGui.QApplication([])

window = QtGui.QWidget()

## Create some widgets to be placed inside
plot            = pg.PlotWidget()
apogee_label    = QLabel()
global apogee_value
apogee_value    = QLabel()

## Create a grid layout to manage the widgets size and position
layout = QtGui.QGridLayout()

## Add widgets to the layout in their proper positions
plot_rows = 16
plot_cols = 6
layout.addWidget(plot, 0, 0, plot_rows, plot_cols)
layout.addWidget(apogee_label,  plot_rows, 0, 1, 1)
layout.addWidget(apogee_value,  plot_rows, 1, 1, 1)

apogee_label.setText("Apogee (m)")


global die
die = False

global input_list
input_list = []

row_index = 0

input_list.append(data_input.Variable_Widget(layout, row_index, plot_cols, "Thrust",            "N"))
row_index += 2
input_list.append(data_input.Variable_Widget(layout, row_index, plot_cols, "Burn Time",         "S"))
row_index += 2
input_list.append(data_input.Variable_Widget(layout, row_index, plot_cols, "Vehicle Diameter",  "in"))
row_index += 2
input_list.append(data_input.Variable_Widget(layout, row_index, plot_cols, "Vehicle Mass",      "kg"))
row_index += 2
input_list.append(data_input.Variable_Widget(layout, row_index, plot_cols, "Drogue Size",       "in"))
row_index += 2
input_list.append(data_input.Variable_Widget(layout, row_index, plot_cols, "Main Size",         "in"))
row_index += 2
input_list.append(data_input.Variable_Widget(layout, row_index, plot_cols, "Launch Altitude",   "ft"))
row_index += 2
input_list.append(data_input.Variable_Widget(layout, row_index, plot_cols, "Sim dt",            "s"))
row_index += 2

#Force column relative layout
for i in range(0,plot_cols + 5):
    layout.setColumnStretch(i,1)

def display_slider(il):
    global die
    global apogee_value
    last_time = time.time()
    while(not(die)):
        time.sleep(0.2)
        # Process all of the widgets
        for w in il:
            w.process()

        # Make the motor model
        motor_model = engine.Rocket_Motor(input_list[0].cur_val, input_list[1].cur_val)

        # Update the sim
        sim = flight_sim.perform_flight(    motor_model,
                                            input_list[2].cur_val,
                                            input_list[3].cur_val,
                                            input_list[4].cur_val,
                                            input_list[5].cur_val,
                                            input_list[6].cur_val,
                                            input_list[7].cur_val
                                    )
        
        apogee = 0
        # Find Apogee
        for entry in sim:
            if entry.altitude > apogee:
                apogee == entry.altitude
        apogee -= input_list[6].cur_val
        apogee *= 3.28084
        apogee_value.setText(str(apogee))

thr = threading.Thread(target=display_slider, args=(input_list,))
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
print("Killing")