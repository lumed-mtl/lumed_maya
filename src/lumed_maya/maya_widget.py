import logging
import sys
from pathlib import Path
from time import strftime

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT, FigureCanvasQTAgg
from matplotlib.figure import Figure

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
import pyqt5_fugueicons as fugue

from lumed_maya.ui.maya_ui import Ui_widgetMayaSpectrometer
from lumed_maya.maya_control import MayaSpectrometer

logger = logging.getLogger(__name__)

LOGS_DIR = Path.home() / "logs/maya_spectro"
LOG_PATH = LOGS_DIR / f"{strftime('%Y_%m_%d_%H_%M_%S')}.log"

spectro_state = {0: "Idle", 1: "Measuring", 2: "Not connected"}
STATE_COLORS = {
    0: "QLabel { background-color : blue; }",
    1: "QLabel { background-color : red; }",
    2: "QLabel { background-color : grey; }",
}

LOG_FORMAT = (
    "%(asctime)s - %(levelname)s"
    "(%(filename)s:%(funcName)s)"
    "(%(filename)s:%(lineno)d) - "
    "%(message)s"
)


def configure_logger():
    """Configures the logger if lumed_HL_2000_HP_232R is launched as a module"""

    if not LOGS_DIR.parent.exists():
        LOGS_DIR.parent.mkdir()
    if not LOGS_DIR.exists():
        LOGS_DIR.mkdir()

    formatter = logging.Formatter(LOG_FORMAT)

    terminal_handler = logging.StreamHandler()
    terminal_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(LOG_PATH)
    file_handler.setFormatter(formatter)

    logger.addHandler(terminal_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)


class DataDisplayWidget(QWidget):
    """Widget to display spectrometer data on MayaSpectrometerWidget"""

    def __init__(self, parent=None):

        super().__init__(parent)
        fig = Figure(figsize=(5, 5))
        self.canvas = FigureCanvasQTAgg(fig)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.ax = self.canvas.figure.add_subplot(111)

    def plot_basic_line(self, x, y, label, xlim=None):
        corrected = np.nan_to_num(y, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
        self.ax.plot(x, y, label=f"{label}")
        self.ax.set_xlabel("wavelength (nm)")
        self.ax.set_ylabel("intensity")
        # Set x axis
        if xlim != None:
            self.ax.set_xlim(xlim, x[-1])
            # new x limits
            x_min, x_max = self.ax.get_xlim()
            # Filter the data based on x limits
            mask = (x >= x_min) & (x <= x_max)
            y_visible = corrected[mask]
            # Adjust y-axis limits based on visible data
            spacing = 0.05 * (y_visible.max() - y_visible.min())
            self.ax.set_ylim(y_visible.min() - spacing, y_visible.max() + spacing)
        # Refresh canvas
        self.ax.legend()
        self.canvas.draw()


class MayaSpectrometerWidget(QWidget, Ui_widgetMayaSpectrometer):
    """User Interface for Maya 2000pro spectrometer.
    Subclass MayaSpectrometerWidget to customize the Ui_widgetMayaSpectrometer widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # logger
        logger.info("Widget intialization")

        self.mayaspectro: MayaSpectrometer = MayaSpectrometer()
        self.disp = DataDisplayWidget(self)  # Data display
        self.setup_default_ui()
        self.connect_ui_signals()
        self.update_ui()
        logger.info("Widget initialization complete")

    def setup_default_ui(self):
        self.pushbtnFindSpectro.setIcon(fugue.icon("magnifier-left"))
        self.verticalLayoutPlot.addWidget(self.disp.canvas)
        self.verticalLayoutPlot.addWidget(self.disp.toolbar)

    def connect_ui_signals(self):
        self.pushbtnFindSpectro.clicked.connect(self.find_spectro)
        self.pushButtonConnect.clicked.connect(self.connect_mayaspectro)
        self.pushButtonDisconnect.clicked.connect(self.disconnect_mayaspectro)
        self.doubleSpinBoxExposure.valueChanged.connect(self.get_exposure)
        self.pushButtonMeasure.clicked.connect(self.get_spectrum)

    def find_spectro(self):
        logger.info("Looking for connected spectros")
        self.pushbtnFindSpectro.setEnabled(False)
        self.pushbtnFindSpectro.setIcon(fugue.icon("hourglass"))
        self.repaint()
        try:
            spectros = self.mayaspectro.find_spectros()
            logger.info("Found spectrometers : %s", spectros)
            self.comboBoxAvailableSpectro.clear()
            for spectro in spectros:
                self.comboBoxAvailableSpectro.addItem(
                    f"{spectro.model}:{spectro.serial_number}"
                )
        except Exception as e:
            logger.error(e, exc_info=True)
        self.pushbtnFindSpectro.setEnabled(True)
        self.pushbtnFindSpectro.setIcon(fugue.icon("magnifier-left"))
        self.update_ui()

    def connect_mayaspectro(self):
        logger.info("Connecting spectrometer")
        self.pushButtonConnect.setEnabled(False)
        if self.mayaspectro.is_spectro_available():
            try:
                combobox_spectro_name = self.comboBoxAvailableSpectro.currentText()
                devices = self.mayaspectro.find_spectros()
                for device in devices:
                    if device.serial_number == combobox_spectro_name.split(":")[-1]:
                        self.mayaspectro.device = device
                self.mayaspectro.connect()
                self.doubleSpinBoxExposure.setRange(
                    self.mayaspectro.get_exposure_time_lims()[0],
                    self.mayaspectro.get_exposure_time_lims()[1],
                )
            except Exception as e:
                logger.error(e, exc_info=True)
        else:
            print("Maya spectrometer not available")
        self.update_ui()

    def disconnect_mayaspectro(self):
        logger.info("Disconnecting spectrometer")
        self.pushButtonDisconnect.setEnabled(False)
        try:
            self.mayaspectro.disconnect()
        except:
            if self.mayaspectro.is_spectro_available() == False:
                print("Maya spectrometer not available")
            raise Exception("No spectrometer available")
        self.update_ui()
        logger.info("Disconnected spectrometer")

    def get_exposure(self):
        logger.info("Setting Exposure time to : %s", self.doubleSpinBoxExposure.value())
        return self.doubleSpinBoxExposure.value()

    def get_spectrum(self):
        self.pushButtonMeasure.setEnabled(False)
        logger.info("Acquiring spectrum")
        if self.mayaspectro.isconnected:
            wavelengths, intensities = self.mayaspectro.spectrum_acquisition(
                self.get_exposure()
            )
            self.disp.ax.cla()  # Clears axis
            self.disp.plot_basic_line(wavelengths, intensities, label=f"acquisition")
            logger.info("Spectrum acquired")
        self.update_ui()

    def set_label_connected(self, isconnected: bool) -> None:
        if isconnected:
            self.labelStatus.setStyleSheet("background-color: white; color: green;")
            self.labelStatus.setText("Connected")
        else:
            self.labelStatus.setStyleSheet("background-color: white; color: red;")
            self.labelStatus.setText("Not connected")

    def update_ui(self):
        # Enable/disable controls if laser is connected or not
        is_connected = self.mayaspectro.isconnected
        self.pushButtonConnect.setEnabled(not is_connected)
        self.comboBoxAvailableSpectro.setEnabled(not is_connected)
        self.pushButtonDisconnect.setEnabled(is_connected)
        self.set_label_connected(is_connected)
        self.pushButtonMeasure.setEnabled(is_connected)
        if is_connected:
            self.textEditModel.setText(self.mayaspectro.spectro.model)
            self.textEditSN.setText(self.mayaspectro.spectro.serial_number)


if __name__ == "__main__":

    # Set up logging
    configure_logger()

    # Create app window
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.show()

    mainWidget = MayaSpectrometerWidget()
    window.setCentralWidget(mainWidget)

    app.exec_()
