import logging
import sys
from pathlib import Path
from time import strftime

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from lumed_maya.ui.maya_ui import Ui_widgetMayaSpectrometer


class MayaSpectrometerWidget(QWidget, Ui_widgetMayaSpectrometer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.setup_default_ui()
        self.connect_signals_to_slots()

    def setup_default_ui(self):
        # self.spi
        self.spinBoxExposure.setRange(0, 65000)
        self.spinBoxGain.setRange(1, 16)

    def connect_signals_to_slots(self):
        self.spinBoxExposure.valueChanged.connect(self.exposure_changed)

    # Slots
    def exposure_changed(self):
        print(self.spinBoxExposure.value())


if __name__ == "__main__":

    # Create app window
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.show()

    mainWidget = MayaSpectrometerWidget()
    window.setCentralWidget(mainWidget)

    app.exec_()
