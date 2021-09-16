from PyQt5.QtWidgets import QLabel, QTabWidget, QToolBar, QAction, QVBoxLayout, QWidget


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
        print(self.course_list)


class MyTabWidget(QTabWidget):
    def __init__(self, course_list: list):
        super().__init__()
        for course in course_list:
            self.tab = QWidget()
            self.tab.layout = QVBoxLayout()
            label = QLabel(course['name'])
            label2 = QLabel(str(course['code']))
            self.tab.layout.addWidget(label)
            self.tab.layout.addWidget(label2)
            self.tab.setLayout(self.tab.layout)
            self.addTab(self.tab, course['name'])
