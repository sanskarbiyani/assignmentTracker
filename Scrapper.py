import requests
from bs4 import BeautifulSoup
import os

CURRENT_TRIMESTER = 7
ASSIGNMENT_URL = "https://mitwpu.instructure.com/api/v1/courses/"


class Scrapper():
    def __init__(self) -> None:
        self.session = requests.Session()
        login_url = "https://mitwpu.instructure.com/login/canvas"
        login_result = self.session.get(url=login_url)

        soup = BeautifulSoup(login_result.text, "html.parser")
        input_list = soup.find_all('input')

        self.payload = {
            "pseudonym_session[unique_id]": os.getenv('MIT_LOGIN'),
            "pseudonym_session[password]": os.getenv('MIT_PASSWORD'),
            "authenticity_token": "",
            "utf8": "✓"
        }
        for input in input_list:
            if input['name'] == "authenticity_token":
                self.payload["authenticity_token"] = input['value']
                break

        result = self.session.post(
            login_url,
            data=self.payload,
            headers=dict(referer=login_url)
        )

    def get_courses(self) -> list:
        courses_url = "https://mitwpu.instructure.com/courses"
        courses_result = self.session.get(
            url=courses_url,
            headers=dict(referer=courses_url)
        )
        soup = BeautifulSoup(courses_result.text, "html.parser")
        course_lists = soup.table.tbody.find_all('tr')
        course_codes = []
        for course in course_lists:
            trimester = str(course.find(
                "td", class_="course-list-term-column").string).strip()
            if trimester == f"Trimester {CURRENT_TRIMESTER}" or trimester == f"Semester {CURRENT_TRIMESTER}":
                course_detail = {
                    "title": course.a['title'],
                    "code": int(str(course.a['href']).split("/")[-1]),
                    "trimester": int(trimester.split(" ")[-1])
                }
                course_codes.append(course_detail)
        return course_codes

    def get_course_assignment(self, course_codes: list) -> dict:
        assignment_details = {}
        for course in course_codes:
            assignment_result = self.session.get(
                url=f"{ASSIGNMENT_URL}{course['code']}/assignments",
                headers=dict(referer=ASSIGNMENT_URL)
            )
            assignments = []
            for assignment in assignment_result.json():
                date = str(assignment['due_at']).split("T")[0]
                if date == "None":
                    date = "0000-00-00"
                status = self.get_submission_status(
                    course['code'], assignment['id'])
                assignment_detail = {
                    "name": assignment['name'].replace("'", ""),
                    "code": assignment['id'],
                    "due_date": date,
                    "status": status
                }
                assignments.append(assignment_detail)
            assignment_details[course['code']] = assignments
        return assignment_details

    def get_submission_status(self, course_code: int, assignment_code: int) -> int:
        result = self.session.get(
            url=f"{ASSIGNMENT_URL}{course_code}/assignments/{assignment_code}/submissions/12921"
        )
        result = result.json()
        if result == "submitted":
            return 1
        else:
            return 0
