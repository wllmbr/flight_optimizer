from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QSlider, QLabel, QLineEdit)
import pyqtgraph as pg

class Variable_Widget:
    def __init__(self, layout, start_row, start_col, name, unit, min, max, callback):
        self.start_col  = start_col
        self.start_row  = start_row
        self.name       = name

        # Create widgets
        self.slider_w   = QSlider(Qt.Horizontal)
        self.name_w     = QLabel()
        self.unit_w     = QLabel()
        self.value_w    = QLabel()
        self.min_w      = QLineEdit()
        self.max_w      = QLineEdit()
        self.cur_val    = 0
        self.updated    = True

        self.slider_w.valueChanged.connect(callback)
        self.min_w.editingFinished.connect(callback)
        self.max_w.editingFinished.connect(callback)

        # Setup widgets
        self.name_w.setText(str(name))
        self.unit_w.setText(str(unit))

        self.tick_range = 1000
        self.slider_w.setMinimum(0)
        self.slider_w.setMaximum(self.tick_range)

        # Add widgets to layout
        layout.addWidget(self.name_w,   start_row,     start_col,        1, 3)
        layout.addWidget(self.value_w,  start_row,     start_col + 3,    1, 1)
        layout.addWidget(self.unit_w,   start_row,     start_col + 4,    1, 1)

        layout.addWidget(self.min_w,    start_row + 1, start_col,        1, 1)
        layout.addWidget(self.slider_w, start_row + 1, start_col + 1,    1, 3)
        layout.addWidget(self.max_w,    start_row + 1, start_col + 4,    1, 1)

        self.set_min(min)
        self.set_max(max)
        self.slider_w.setValue(50)
        self.process()

    def set_min(self, val):
        self.min_val = val
        self.min_w.setText(str(val))

    def set_max(self, val):
        self.max_val = val
        self.max_w.setText(str(val))

    def set_val(self, val):
        if val < self.min_val:
            self.min_val = val
        if val > self.max_val:
            self.max_val = val
        
        # Find the where in the range the value is
        r = self.max_val - self.min_val
        rp = val - self.min_val

        mp = rp / r
        self.slider_w.setValue(int(mp * self.tick_range))

    def process(self):
        # # Update values from min/max
        try:
            self.min_val = float(self.min_w.text())
        except:
            # Value input could not be converted to float so reset it
            self.set_min(self.min_val)

        try:
            self.max_val = float(self.max_w.text())
        except:
            # Value input could not be converted to float so reset it
            self.set_max(self.max_val)

        percent     = self.slider_w.value() * (100 / self.tick_range)
        in_range    = (self.max_val - self.min_val) * (percent / 100.0)

        new_val     = in_range + self.min_val

        if(new_val == self.cur_val):
            self.updated = False
        else :
            self.cur_val = new_val
            self.updated = True
            
        self.value_w.setText("%10.3f" % self.cur_val)