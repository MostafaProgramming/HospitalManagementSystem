grades = []
class Student:
    def __init__(self, name: str, student_id: str):
        self.__name = name
        self.__student_id = student_id
        self.__grades = []  # List to store grades

    def add_grade(self, grade: float):
        pass                           # TODO: Add the grade to the grades list
        grade = float(input("Enter grade: "))
        grades.append(grade)
        print("Grade added successfully.")
        #while True:
        #    print("1. Add grade")
        #    print("2. view grades")
        #    print("3. Exit")
        #    choice = input("Enter your choice: ")
        #    if choice == "1":
        #        add_grade()
        #    elif choice == "2":
        #        view_grades()
        #    elif choice == "3":
        #        break
        #    else:
        #        print("Invalid choice. Please try again.  ")

    def view_grades(self):
        pass  # TODO: Print the grades list
        print("Grades:", grades)
        
    def calculate_average(self) -> float:
        pass  # TODO: Calculate and return the average grade
        average = sum(grades) / len(grades)
        print("Average grades: ",average)
        return average
        
        
        

    def get_details(self) -> str:
        pass  # TODO: Return a formatted string with student details
        return f"Name: {self.name}, Student ID: {self.__student_id}, Average Grade: {self.calculate_average()}"

student1 = Student("Alice Johnson", "S12345")
student1.add_grade(85)
student1.add_grade(90)
student1.add_grade(78)

print(student1.get_details())  # Should print student details and average grade