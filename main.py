class Student:
    def __init__(self, Firstname, student_id, Surname, Birthyear):
        self.name = Firstname
        self.student_id = student_id
        self._grades = []  # Private attribute for encapsulation
        self.surname = Surname
        self.birthyear = Birthyear

    def add_grade(self, grade):
        """Adds a new grade to the student."""
        self._grades.append(grade)

    def calculate_average(self):
        """Calculates the average grade."""
        if len(self._grades) == 0:
            return 0
        return sum(self._grades) / len(self._grades)

    def determine_pass_fail(self):
        """Determines pass/fail based on a 50% pass mark."""
        return self.calculate_average() >= 50

    def get_report(self):
        """Generates and returns a student report."""
        return (f"Student: {self.name} (ID: {self.student_id})\n"
                f"Grades: {self._grades}\n"
                f"Average: {self.calculate_average():.2f}\n"
                f"Status: {'Pass' if self.determine_pass_fail() else 'Fail'}\n")


class HonoursStudent(Student):
    def determine_pass_fail(self):
        """Honours students require at least 70% to pass."""
        return self.calculate_average() >= 70


class GradeTracker:
    def __init__(self):
        self.students = {}

    def add_student(self, name, student_id, Surname, Birthyear, honours=False):
        """Adds a student to the tracker."""
        if honours:
            student = HonoursStudent(name, student_id, Surname, Birthyear)
        else:
            student = Student(name, student_id, Surname, Birthyear)
        self.students[student_id] = student
        print(f"Student '{name}' added successfully!")

    def enter_grades(self, student_id, grades):
        """Adds grades to a student."""
        if student_id in self.students:
            for grade in grades:
                self.students[student_id].add_grade(grade)
            print(f"Grades {grades} added for {self.students[student_id].name}.")
        else:
            print("Student ID not found!")

    def generate_reports(self):
        """Prints all student reports."""
        for student in self.students.values():
            print(student.get_report())


# CLI Interface
def main():
    tracker = GradeTracker()
    # Main options menu for user input
    while True:
        print("""
╔══════════════════════════════════════════╗
║         Student Grade Tracker            ║
║            Management System             ║
╠══════════════════════════════════════════╣
║                                          ║
║    1. Add New Student                    ║
║    2. Enter Student Grades               ║
║    3. View Student Reports               ║
║    4. Exit System                        ║
║                                          ║
╚══════════════════════════════════════════╝
""")
        choice = input("➜ Please enter your choice (1-4): ")
        print("")
        if choice == "1":
            name = str(input("Enter student name: "))
            while len(name) > 30 or len(name) < 1:
                print("Invalid name. Please enter a valid name between 1-30 letters.")
                print("")
                name = input("Enter student name: ")

            Surname = str(input("Enter student Surname: "))
            while len(Surname) > 30 or len(Surname) < 1:
                print("Invalid surname. Please enter a valid surname between 1-30 letters.")
                print("")
                Surname = input("Enter student surname: ")
                
            Birthyear = (input("Enter student Birthyear: "))
            while not Birthyear.isdigit():
                print("Invalid input. Please enter a valid number")
                Birthyear = (input("Enter student Birthyear: "))
                
            honours = input("Is this an honours student? ([y]es/[n]o): ")
            while honours.lower() != "y" and honours.lower() != "n":
                print("invalid. Please enter either [y]es or [n]o. ")
                honours = input("Is this an honours student? (yes/no): ")
             
            
            student_id = name[0:3] + Surname[0:3] + str(Birthyear)
            tracker.add_student(name, student_id, Surname, Birthyear, honours)
            print(name,"'s ID is ", student_id)

        elif choice == "2":
            if not tracker.students:
                print("No students added yet. Please add a student first. ")
            else:
                student_id = input("Enter student ID: ")
                grades = list(map(int, input("Enter grades separated by spaces: ").split()))
                tracker.enter_grades(student_id, grades)

        elif choice == "3":
            if not tracker.students:
                print("No students added yet. Please add a student first.  ")
            else: # Check if any student has grades
                has_grades = any(len(student._grades) > 0 for student in tracker.students.values())
                if not has_grades:
                    print("No grades entered yet. Please enter grades first.  ")
                else:
                    print("\nStudent Reports:")
                    tracker.generate_reports()

        elif choice == "4":
            print("Exiting the system. Goodbye!")
            break

        else:
            print("Invalid choice! Please enter a valid option.")

# Run the program
if __name__ == "__main__":
    main()
