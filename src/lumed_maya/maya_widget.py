import logging
import sys
from pathlib import Path
from time import strftime

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import  NavigationToolbar2QT, FigureCanvasQTAgg
from matplotlib.figure import Figure

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from lumed_maya.ui.maya_ui import Ui_widgetMayaSpectrometer
from maya_control import MayaSpectrometer

class DataDisplayWidget(QWidget):
  
    def __init__(self, parent=None):
        
        super().__init__(parent)
        fig = Figure(figsize=(5, 5))
        self.canvas = FigureCanvasQTAgg(fig)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.ax = self.canvas.figure.add_subplot(111)

    def plot_basic_line(self, x, y, label, xlim = None):
        corrected = np.nan_to_num(y, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
        self.ax.plot(x, y, label = f"{label}")
        #Set x axis
        self.ax.set_xlabel("wavelength (nm)")
        self.ax.set_ylabel("intensity")
        if xlim != None:
            self.ax.set_xlim(xlim,x[-1])
            # new x limits
            x_min, x_max = self.ax.get_xlim()
            # Filter the data based on x limits
            mask = (x >= x_min) & (x <= x_max)
            y_visible = corrected[mask]
            # Adjust y-axis limits based on visible data
            spacing = 0.05*(y_visible.max() - y_visible.min())
            self.ax.set_ylim(y_visible.min()-spacing, y_visible.max()+spacing)
        #Refresh canvas
        self.ax.legend()
        self.canvas.draw()

class MayaSpectrometerWidget(QWidget, Ui_widgetMayaSpectrometer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.mayaspectro: MayaSpectrometer = MayaSpectrometer()
        self.disp = DataDisplayWidget(self) # Data display 
        self.setup_default_ui()
        self.connect_ui_signals()
        

    def setup_default_ui(self):
        self.labelStatus.setStyleSheet("background-color: white; color: red;")
        self.labelStatus.setText("Not connected")
        self.verticalLayoutPlot.addWidget(self.disp.canvas)
        self.verticalLayoutPlot.addWidget(self.disp.toolbar)
        self.update_ui()
        
    def connect_ui_signals(self):
        self.pushButtonConnect.clicked.connect(self.connect_mayaspectro)
        self.pushButtonDisconnect.clicked.connect(self.disconnect_mayaspectro)
        self.doubleSpinBoxExposure.valueChanged.connect(self.getExposure)
        self.pushButtonMeasure.clicked.connect(self.getSpectrum)
    
    def connect_mayaspectro(self):
        self.pushButtonConnect.setEnabled(False)
        if self.mayaspectro.isSpectroAvailable():
            self.mayaspectro.connect()
            self.labelStatus.setStyleSheet("background-color: white; color: green;")
            self.labelStatus.setText("Connected")
            self.doubleSpinBoxExposure.setRange(self.mayaspectro.get_exposure_time_lims()[0], 
                                      self.mayaspectro.get_exposure_time_lims()[1])
        else:
            print("Maya spectrometer not available")
        self.update_ui()
    def disconnect_mayaspectro(self):
        self.pushButtonDisconnect.setEnabled(False)
        try:
            self.mayaspectro.disconnect() 
            self.labelStatus.setStyleSheet("background-color: white; color: red;")
            self.labelStatus.setText("Not connected")
        except:
            if self.mayaspectro.isSpectroAvailable() == False:
                print("Maya spectrometer not available")
            raise Exception("No spectrometer available")
        self.update_ui()

    def getExposure(self):
        print(f"Exposure set to: {self.doubleSpinBoxExposure.value()}")
        return self.doubleSpinBoxExposure.value()
    
    def getSpectrum(self):
        self.pushButtonMeasure.setEnabled(False)
        if self.mayaspectro.isconnected:
            wavelengths, intensities = self.mayaspectro.spectrum_acquisition(self.getExposure())
            self.disp.ax.cla() #Clears axis
            self.disp.plot_basic_line(wavelengths,intensities, label=f"acquisition")
        self.update_ui()
    def update_ui(self):
        # Enable/disable controls if laser is connected or not
        is_connected = self.mayaspectro.isconnected
        print(" Maya connected ?: ", is_connected)
        self.pushButtonConnect.setEnabled(not is_connected)
        self.pushButtonDisconnect.setEnabled(is_connected)
        self.pushButtonMeasure.setEnabled(is_connected)

if __name__ == "__main__":

    # Create app window
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.show()

    mainWidget = MayaSpectrometerWidget()
    window.setCentralWidget(mainWidget)

    app.exec_()
