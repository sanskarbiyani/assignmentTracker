from pprint import pprint
from Scrapper import Scrapper
from Database import Database
import sys
from PyQt5.QtWidgets import QAction, QApplication, QStatusBar, QToolBar, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QLabel, QMainWindow
from PyQt5.QtCore import QSize, Qt
from toolbar import MyTabWidget, Toolbar
from dotenv import load_dotenv

load_dotenv()


mydatabase = Database()
course_scrapper = Scrapper()


def update_course():
    course_codes = course_scrapper.get_courses()
    if not mydatabase.courses_exists():
        mydatabase.add_new_courses(course_codes)
        return True
    else:
        return False


def assignment_course(course_codes: list):
    assignment_lists = course_scrapper.get_course_assignment(course_codes)
    for code, assignments in assignment_lists.items():
        mydatabase.assignment_addition(code, assignments)


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.setMinimumSize(QSize(1000, 800))
        self.setWindowTitle("Assignment Tracker")
        layout = QVBoxLayout()
        # label = QLabel("Hello")
        # label.setAlignment(Qt.AlignCenter)
        # self.setCentralWidget(label)

        self.course_list = mydatabase.get_courses()
        print(self.course_list)
        toobar = Toolbar("Main Toolbar", self.course_list)
        toobar.update_courses_button.triggered.connect(
            self.on_update_course_button_click)
        toobar.get_assignments_button.triggered.connect(
            self.on_get_assignment_button_click)
        self.addToolBar(toobar)
        self.setStatusBar(QStatusBar(self))

        tab_widget = MyTabWidget(self.course_list)
        layout.addWidget(tab_widget)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def on_update_course_button_click(self):
        status = update_course()
        if status:
            print("Course List updated")
        else:
            print("No new course available")

    def on_get_assignment_button_click(self):
        self.assignmentList


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
app.exec()
