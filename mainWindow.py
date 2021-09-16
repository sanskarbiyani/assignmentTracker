import sys
from PyQt5.QtWidgets import QLabel, QMainWindow
from PyQt5.QtCore import QSize, Qt


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.setMinimumSize(QSize(1000, 800))
        self.setWindowTitle("Assignment Tracker")
        label = QLabel("Hello")
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)
