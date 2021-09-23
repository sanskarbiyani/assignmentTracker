from pprint import pprint
from re import sub

from mysql.connector.constants import ServerFlag, flag_is_set
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
        self.toobar = Toolbar("Main Toolbar", self.course_list)
        self.toobar.update_courses_button.triggered.connect(
            self.on_update_course_button_click)
        self.toobar.get_assignments_button.triggered.connect(
            self.on_get_assignment_button_click)
        self.toobar.update_assignment_list.triggered.connect(
            self.update_all_assignments)
        self.toobar.quit_button.triggered.connect(self.quit_application)
        self.toobar.check_assignment_status.triggered.connect(
            self.check_assignment_status)
        self.addToolBar(self.toobar)
        self.setStatusBar(QStatusBar(self))

        self.tab_widget = MyTabWidget(course_list=self.course_list)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        layout.addWidget(self.tab_widget)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.tab_changed(self.tab_widget.currentIndex())
        self.selected_list_item = None

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
            self.tab_widget.currentWidget().sub_tab = MyTabWidget(
                submitted=submitted, unsubmitted=unsubmitted)
            current_layout = self.tab_widget.currentWidget().layout()
            widget = current_layout.itemAt(0)
            current_layout.removeItem(widget)
            self.tab_widget.currentWidget().layout().addWidget(
                self.tab_widget.currentWidget().sub_tab)
            self.tab_widget.currentWidget().have_sub_tabs = True
            self.tab_widget.currentWidget().sub_tab.d["unsubmitted"].itemClicked.connect(
                self.list_item_clicked)
            self.tab_widget.currentWidget().sub_tab.d["submitted"].itemClicked.connect(
                self.list_item_clicked)
            self.tab_widget.currentWidget().sub_tab.currentChanged.connect(
                self.sub_tabs_changed)
            self.course_list[index]['submitted'] = submitted
            self.course_list[index]['unsubmitted'] = unsubmitted
        else:
            self.deselect_item()

    def list_item_clicked(self, item):
        self.selected_list_item = item
        course = self.tab_widget.currentWidget()
        course_index = self.tab_widget.indexOf(course)
        self.course_id = self.course_list[course_index]['code']
        status_index = course.sub_tab.indexOf(course.sub_tab.currentWidget())
        if status_index == 0:
            row = course.sub_tab.d["unsubmitted"].row(item)
            print(f"Row from list_item_clicked: {row}", end='\n\n')
            self.assignment_id = self.course_list[course_index]['unsubmitted'][row]["id"]
        else:
            row = course.sub_tab.d["submitted"].row(item)
            self.assignment_id = self.course_list[course_index]['submitted'][row]["id"]

    # This method de-selects the selected item on the next turn when the tab is clicked
    # As the currentItem() and currentWidget() returns the new widget not the old ones.
    # def deselect_item(self, index):
    #     list_widget = self.tab_widget.currentWidget().sub_tab
    #     if index == 0:
    #         item = list_widget.d["unsubmitted"].currentItem()
    #         if not item:
    #             return
    #     else:
    #         item = list_widget.d["submitted"].currentItem()
    #         if not item:
    #             return
    #     item.setSelected(False)

    def deselect_item(self):
        if self.selected_list_item:
            self.selected_list_item.setSelected(False)

    def sub_tabs_changed(self, index):
        if index == 0:
            self.toobar.check_assignment_status.setEnabled(True)
        else:
            self.toobar.check_assignment_status.setDisabled(True)
        self.deselect_item()

    # For checking the status of a particular assignment
    # We check it's status and try to update the databases is status is 1
    # If database updated successfully, than we remove the element from the unsubmitted list
    # and add it to the submitted list.

    # After deleting the element at the last row, we would check the second last element
    # to see if it exists, if it does then we update the course and assignment id
    # if not, than we disable the button.
    def check_assignment_status(self):
        status = course_scrapper.get_submission_status(
            self.course_id, self.assignment_id)
        print("Inside.")
        if status == 1:
            error = mydatabase.update_assignment_status(
                self.course_id, self.assignment_id)
            if error:
                print("Check above.")
            else:
                sub_tab = self.tab_widget.currentWidget().sub_tab
                row = sub_tab.d['unsubmitted'].row(self.selected_list_item)
                index = self.tab_widget.indexOf(
                    self.tab_widget.currentWidget())
                assignment = self.course_list[index]['unsubmitted'].pop(row)
                self.course_list[index]['submitted'].append(assignment)
                sub_tab.d["unsubmitted"].takeItem(row)
                sub_tab.d["submitted"].addItem(self.selected_list_item)
                self.selected_list_item = sub_tab.d['unsubmitted'].item(row)
                print(f"Row from check status: {row}")
                if self.selected_list_item is not None:
                    self.selected_list_item.setSelected(True)
                    self.list_item_clicked(self.selected_list_item)
                else:
                    self.selected_list_item = sub_tab.d['unsubmitted'].item(
                        row-1)
                    if self.selected_list_item is not None:
                        self.list_item_clicked(self.selected_list_item)
                    else:
                        self.toobar.check_assignment_status.setDisabled(True)

    def quit_application(self):
        app.quit()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec_())
