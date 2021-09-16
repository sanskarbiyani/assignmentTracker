from Scrapper import CURRENT_TRIMESTER
import mysql.connector
from mysql.connector import errorcode
from mysql.connector.connection import MySQLConnection
import os

DB_NAME = "assignmenttracker"
TABLES = {}
TABLES["course"] = (
    "CREATE TABLE course ("
    "id INT PRIMARY KEY,"
    "name VARCHAR(30) NOT NULL UNIQUE,"
    "trimester INT NOT NULL"
    ");"
)

TABLES["assignment"] = (
    "CREATE TABLE assignment ("
    "id INT PRIMARY KEY,"
    "course_code INT NOT NULL,"
    "name VARCHAR(200) NOT NULL UNIQUE,"
    "due_date DATE NOT NULL,"
    "FOREIGN KEY (course_code) REFERENCES course(id)"
    ");"
)


class Database():
    def __init__(self) -> None:
        self.mydb = mysql.connector.connect(
            host="localhost",
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD')
        )
        self.cursor = self.mydb.cursor()
        self.check_tables_present()

    def create_database(self):
        try:
            self.cursor.execute("CREATE DATABASE {}".format(DB_NAME))
        except mysql.connector.Error as err:
            print("Failed Creating Database: {}".format(DB_NAME))
            exit(1)

    def create_tables(self):
        for table_name in TABLES:
            description = TABLES[table_name]
            try:
                print(type(description))
                print(f"Creating table {table_name}: ", end='')
                self.cursor.execute(description)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists")
                else:
                    print(err.msg)
            else:
                print("OK")

    def check_tables_present(self):
        try:
            self.cursor.execute("USE {}".format(DB_NAME))
        except mysql.connector.Error as err:
            print("Database {} does not exists.".format(DB_NAME))
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self.create_database()
                print("Database {} created sucessfully.".format(DB_NAME))
                self.mydb.database = DB_NAME
            else:
                print(err)
                exit(1)

        self.cursor.execute(
            f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{DB_NAME}'")
        (result_list, ) = self.cursor.fetchone()
        if result_list == 2:
            print("Tables exists.")
        else:
            print("No tables exists.")
            self.create_tables()

    def courses_exists(self) -> bool:
        self.cursor.execute(f'''
            SELECT COUNT(*) FROM course
            WHERE trimester={CURRENT_TRIMESTER}
        ''')
        (result, ) = self.cursor.fetchone()
        if result > 4:
            print("All Courses present.")
            return True
        else:
            return False

    def add_new_courses(self, courseList: list) -> None:
        for course in courseList:
            string = f"INSERT INTO course (id, name, trimester) VALUES ({course['code']}, '{course['title']}', {course['trimester']});"
            try:
                self.cursor.execute(string)
            except mysql.connector.Error as err:
                if err.errno == 1062:
                    print(f"The value {course['title']} already present")
                elif err.errno == 1064:
                    print("Syntax error in statement.")
                else:
                    print(err)
            else:
                print(f"Course {course['title']} inserted.")
        self.mydb.commit()

    def assignment_addition(self, code: int, assignments: list) -> bool:
        try:
            self.cursor.execute(
                f"SELECT COUNT(*) FROM assignment WHERE course_code ={code}")
            (assignment_number, ) = self.cursor.fetchone()
        except mysql.connector.Error as err:
            print(err)
        else:
            if assignment_number == len(assignments):
                return False
            else:
                self.add_assignments(code, assignments, assignment_number)
                return True

    def add_assignments(self, course_code: int, assignments: list, length: int):
        for assignment in assignments[length:]:
            string = f"""
                INSERT INTO assignment (id, course_code, name, due_date, status) 
                VALUES ({assignment['code']}, {course_code}, '{assignment['name']}', '{assignment['due_date']}', {assignment['status']})
            """
            try:
                self.cursor.execute(string)
            except mysql.connector.Error as err:
                if err.errno == 1062:
                    print(f"{assignment['name']} already exists.")
                else:
                    print(err)
            else:
                print(
                    f"Assignment {assignment['name']} for course {course_code} added.")
        self.mydb.commit()

    def get_courses(self) -> list:
        self.cursor.execute(
            f"SELECT name, id, trimester FROM course WHERE trimester={CURRENT_TRIMESTER}")
        results = self.cursor.fetchall()
        course_list = []
        for (name, code, trimester) in results:
            course = {
                "name": name,
                "code": code,
                "trimester": trimester
            }
            course_list.append(course)
        return course_list

    def __del__(self):
        self.cursor.close()
        self.mydb.close()
        print("Connnection Closed.")
