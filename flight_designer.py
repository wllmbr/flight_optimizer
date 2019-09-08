#!/usr/bin/python3
import sys
if not((sys.version_info > (3, ))):
    print("FATAL\tThis Script needs Python 3")
    sys.exit()

# Try to import numpy
try:
    import numpy
except:
    print("Warning:   numpy not installed!\nAuto-installing...")
    import pip
    pip.main(['install', 'numpy'])
    # sys.exit()

# Try to import pyqtgraph
try:
    import pyqtgraph
except:
    print("Warning:   pyqtgraph not installed!\nAuto-installing...")
    import pip
    pip.main(['install', 'pyqtgraph'])
    # exit()

# Try to import PyQt5
try:
    import PyQt5
except:
    print("Warning:   PyQt5 not installed!\nAuto-installing...")
    import pip
    pip.main(['install', 'PyQt5'])
    # exit()

# Switch over to the actual program
import src.flight_optimizer

