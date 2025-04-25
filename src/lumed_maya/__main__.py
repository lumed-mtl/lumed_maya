import sys
from maya_widget import MayaSpectrometerWidget
from PyQt5.QtWidgets import QApplication, QMainWindow

if __name__ == "__main__":
    # Create app window
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.show()

    mainWidget = MayaSpectrometerWidget()
    window.setCentralWidget(mainWidget)
    app.exec_()
