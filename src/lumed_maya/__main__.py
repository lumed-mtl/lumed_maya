import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

if __name__ == "__main__":
    # Create app window
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.show()

    app.exec_()
