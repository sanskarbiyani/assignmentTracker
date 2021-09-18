from pprint import pprint

from mysql.connector.constants import ServerFlag
from Scrapper import Scrapper
from Database import Database
import sys
from PyQt5.QtWidgets import QAction, QApplication, QStatusBar, QToolBar, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QLabel, QMainWindow
from PyQt5.QtCore import QSize, Qt
from widgets import MyTabWidget, Toolbar
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
        toobar = Toolbar("Main Toolbar", self.course_list)
        toobar.update_courses_button.triggered.connect(
            self.on_update_course_button_click)
        toobar.get_assignments_button.triggered.connect(
            self.on_get_assignment_button_click)
        toobar.update_assignment_list.triggered.connect(
            self.update_all_assignments)
        toobar.quit_button.triggered.connect(self.quit_application)
        self.addToolBar(toobar)
        self.setStatusBar(QStatusBar(self))

        self.tab_widget = MyTabWidget(course_list=self.course_list)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        layout.addWidget(self.tab_widget)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.tab_changed(self.tab_widget.currentIndex())

    def on_update_course_button_click(self):
        status = update_course()
        if status:
            print("Course List updated")
        else:
            print("No new course available")

    def update_all_assignments(self):
        assignment_course(self.course_list)

    def on_get_assignment_button_click(self):
        print("Function of this button is not decided.")

    def tab_changed(self, index):
        if not self.tab_widget.currentWidget().have_sub_tabs:
            (submitted, unsubmitted) = mydatabase.get_course_assignments(
                self.course_list[index]['code'])
            self.sub_tabs = MyTabWidget(
                submitted=submitted, unsubmitted=unsubmitted)
            current_layout = self.tab_widget.currentWidget().layout()
            widget = current_layout.itemAt(0)
            current_layout.removeItem(widget)
            self.tab_widget.currentWidget().layout().addWidget(self.sub_tabs)
            self.tab_widget.currentWidget().have_sub_tabs = True
            self.sub_tabs.d["unsubmitted"].itemClicked.connect(
                self.list_item_clicked)
            self.sub_tabs.d["submitted"].itemClicked.connect(
                self.list_item_clicked)
            self.course_list[index]['submitted'] = submitted
            self.course_list[index]['unsubmitted'] = unsubmitted

    def list_item_clicked(self, item):
        course_index = self.tab_widget.indexOf(self.tab_widget.currentWidget())
        status_index = self.sub_tabs.indexOf(self.sub_tabs.currentWidget())
        if status_index == 0:
            row = self.sub_tabs.d["unsubmitted"].row(item)
        else:
            row = self.sub_tabs.d["submitted"].row(item)

    def quit_application(self):
        app.quit()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec_())
