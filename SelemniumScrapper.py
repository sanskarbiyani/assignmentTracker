import time
from selenium import webdriver
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import InvalidArgumentException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pprint import pprint

from selenium.webdriver.support.wait import IGNORED_EXCEPTIONS

USERNAME = "1032190914@mitwpu.edu.in"
PASSWORD = "S1032190914"

chrome_driver = "C:\Development\chromedriver.exe"


class CourseBot():
    def __init__(self) -> None:
        super().__init__()
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.options.add_argument('window-size=1920x1080')
        self.options.add_argument("disable-gpu")
        self.options.add_argument('log-level=3')

        self.driver = webdriver.Chrome(
            executable_path=chrome_driver, options=self.options)
        # self.driver = webdriver.Chrome(executable_path=chrome_driver)
        self.driver.get("https://mitwpu.instructure.com")
        self.wait = WebDriverWait(self.driver, 20)
        self.course_link = "https://mitwpu.instructure.com/courses/"

    def current_url(self):
        return self.driver.current_url

    def login(self):
        time.sleep(2)
        remember_me_checkbox = self.driver.find_element_by_id(
            "pseudonym_session_remember_me")
        remember_me_checkbox.click()
        unique_id = self.driver.find_element_by_id(
            "pseudonym_session_unique_id")
        unique_id.send_keys(USERNAME, Keys.TAB, PASSWORD, Keys.ENTER)

        try:
            tour_cancel = self.driver.find_element_by_xpath(
                "/html/body/div[4]/div[4]/div/div/div/span[2]/span[2]/button[1]")
        except NoSuchElementException:
            pass
        else:
            element = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "/html/body/div[4]/div[4]/div/div/div/span[1]/span/button")))
            self.driver.execute_script("arguments[0].click();", element)
            self.driver.implicitly_wait(20)
            time.sleep(2)
            close_button = self.wait.until(EC.visibility_of_element_located((
                By.XPATH, "/html/body/div[4]/div[4]/div/div/div/span[1]/span/button")))
            self.driver.execute_script("arguments[0].click();", close_button)

    def getCourses(self) -> list:
        container = self.driver.find_element_by_class_name(
            "ic-DashboardCard__box__container")
        element_list = container.find_elements_by_class_name(
            "ic-DashboardCard")

        course_list = []
        for element in element_list[:5]:
            course = {
                "name": element.get_attribute("aria-label"),
                "code": int(element.find_element_by_css_selector(
                    ".ic-DashboardCard__header a").get_attribute("href").split("/")[-1])
            }
            course_list.append(course)
        return course_list

    def get_assignments(self, course_code: int):
        print(f"For Course code: {course_code}")
        self.driver.get(f"{self.course_link}{course_code}/assignments")

        main_container = self.driver.find_element_by_id("ag-list")
        assignment_tabs = main_container.find_elements_by_xpath("./ul/li")
        for i in range(0, len(assignment_tabs)):
            time.sleep(2)
            while True:
                try:
                    assignment_list = assignment_tabs[i].find_elements_by_xpath(
                        "./div/div[2]/ul/li")
                except StaleElementReferenceException:
                    print("Error..")
                    assignment_tabs = main_container.find_elements_by_xpath(
                        "./ul/li")
                    time.sleep(1)
                else:
                    for assignment in assignment_list:
                        name = assignment.find_element_by_xpath(
                            "./div/div/div[2]/a").text
                        print(f"Name: {name} ", end="   ")
                        try:
                            detail = assignment.find_element_by_xpath(
                                "./div/div/div[2]/div/div[1]/span[1]")
                        except NoSuchElementException:
                            try:
                                date = assignment.find_element_by_xpath(
                                    "./div/div/div[2]/div/div[1]/span/span[1]")
                            except NoSuchElementException:
                                pass
                            else:
                                due_date = date.text
                                print(f"Due date: {due_date} ")
                        else:
                            due_date = detail.text
                            print(f"Due Date: {due_date} ")
                    break
            # print(f"length: {len(assignment_list)}")
