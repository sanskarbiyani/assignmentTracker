from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLayout, QListWidget, QListWidgetItem, QMainWindow, QRadioButton, QTabWidget, QToolBar, QAction, QVBoxLayout, QWidget


class Toolbar(QToolBar):
    def __init__(self, string: str, course_list: list) -> None:
        super().__init__(string)
        self.course_list = course_list
        self.update_courses_button = QAction("Update Courses", self)
        self.update_courses_button.setStatusTip("Check For new courses.")
        self.addAction(self.update_courses_button)

        self.addSeparator()

        self.get_assignments_button = QAction("Get Assignments", self)
        self.get_assignments_button.setStatusTip("Get Assignment List")
        self.addAction(self.get_assignments_button)

        self.addSeparator()

        self.update_assignment_list = QAction("Update All Assignment", self)
        self.update_assignment_list.setStatusTip("Get all assignments")
        self.addAction(self.update_assignment_list)

        self.addSeparator()

        self.quit_button = QAction("Quit Application", self)
        self.quit_button.setStatusTip("Quit Application")
        self.addAction(self.quit_button)


class MyTabWidget(QTabWidget):
    def __init__(self, **kwargs):
        super().__init__()
        # self.tab = QWidget()
        # self.tab.layout = QVBoxLayout()
        # For creating MAIN tablist
        if 'course_list' in kwargs:
            for course in kwargs['course_list']:
                self.tab = QWidget()
                self.tab.have_sub_tabs = False
                layout = QVBoxLayout()
                label = QLabel("Loading...")
                layout.addWidget(label)
                self.tab.setLayout(layout)
                self.addTab(self.tab, course['name'])

        # For creating the sub tab list
        # Will be creating when called from tab_changed() in MainWindow.
        else:
            status_list = ["unsubmitted", "submitted"]
            self.d = {}
            for status in status_list:
                self.status_tab = QWidget()
                layout = QVBoxLayout()
                self.d[status] = QListWidget()
                if len(kwargs[status]) != 0:
                    for assignment in kwargs[status]:
                        new_item = QListWidgetItem()
                        text = f"{assignment['name']}\nDue Date: {assignment['due_date']}"
                        new_item.setText(text)
                        self.d[status].addItem(new_item)
                else:
                    new_item = QListWidgetItem()
                    text = "No Assignments present here! PLease check other tabs."
                    new_item.setText(text)
                    self.d[status].addItem(new_item)
                self.d[status].setWordWrap(True)
                self.d[status].setSpacing(5)
                layout.addWidget(self.d[status])
                self.status_tab.setLayout(layout)
                self.addTab(self.status_tab, status)
