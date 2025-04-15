
import tkinter as tk 
from tkinter import ttk, messagebox
# Import the Tkinter library for GUI & Import additional Tkinter modules for widgets & message boxes

class Student:                                    # Define a class for a student
    def __init__(self, Firstname, student_id, Surname, Birthyear):
        self.name = Firstname
        self.student_id = student_id
        self._grades = []
        self.surname = Surname
        self.birthyear = Birthyear

    def add_grade(self, grade):                 # Method (add a grade to the student's grades list)
        self._grades.append(grade)

    def calculate_average(self):                # Method (calculate the average grade of the student)
        if len(self._grades) == 0:
            return 0
        return sum(self._grades) / len(self._grades)

    def determine_pass_fail(self):              # Method (determine if the student passed or failed based on their average grade)
        return self.calculate_average() >= 50

    def get_report(self):                       # Method (generate a report for the students)
        return (f"Student: {self.name} (ID: {self.student_id})\n"
                f"Grades: {self._grades}\n"
                f"Average: {self.calculate_average():.2f}\n"
                f"Status: {'Pass' if self.determine_pass_fail() else 'Fail'}\n")

class HonoursStudent(Student):                  # Define a class for an honours student (inherits from the student class)
    def determine_pass_fail(self):               # Method (override the determine_pass_fail method for honours students)
        return self.calculate_average() >= 70

class GradeTrackerGUI:                           # Define a class for the grade tracker GUI
    def __init__(self, root):
        self.root = root
        self.root.title("Student Grade Tracker")
        self.tracker = GradeTracker()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create and pack widgets
        ttk.Label(self.main_frame, text="Student Grade Tracker System", font=('Helvetica', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Button(self.main_frame, text="Add New Student", command=self.show_add_student).grid(row=1, column=0, columnspan=2, pady=5, sticky=tk.EW)
        ttk.Button(self.main_frame, text="Enter Grades", command=self.show_enter_grades).grid(row=2, column=0, columnspan=2, pady=5, sticky=tk.EW)
        ttk.Button(self.main_frame, text="View Reports", command=self.show_reports).grid(row=3, column=0, columnspan=2, pady=5, sticky=tk.EW)
        
    def show_add_student(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Student")
        dialog.geometry("300x250")
        
        ttk.Label(dialog, text="First Name:").grid(row=0, column=0, pady=5, padx=5, sticky='w')
        name_entry = tk.Text(dialog, height=1, width=20)
        name_entry.grid(row=0, column=1, pady=5, padx=5, sticky='ew')
        
        ttk.Label(dialog, text="Surname:").grid(row=1, column=0, pady=5, padx=5, sticky='w')
        surname_entry = tk.Text(dialog, height=1, width=20)
        surname_entry.grid(row=1, column=1, pady=5, padx=5, sticky='ew')
        
        ttk.Label(dialog, text="Birth Year:").grid(row=2, column=0, pady=5, padx=5, sticky='w')
        birth_year_entry = tk.Text(dialog, height=1, width=20)
        birth_year_entry.grid(row=2, column=1, pady=5, padx=5, sticky='ew')
        
        # Configure column weight to allow expansion
        dialog.grid_columnconfigure(1, weight=1)
        
        honours_var = tk.BooleanVar()
        ttk.Checkbutton(dialog, text="Honours Student", variable=honours_var).grid(row=3, column=0, columnspan=2, pady=5)
        
        def submit():
            name = name_entry.get("1.0", "end-1c").strip()
            surname = surname_entry.get("1.0", "end-1c").strip()
            birth_year = birth_year_entry.get("1.0", "end-1c").strip()
            
            if not all([name, surname, birth_year]):
                messagebox.showerror("Error", "All fields are required!")
                return
        
            student_id = name[0:3] + surname[0:3] + birth_year
            self.tracker.add_student(name, student_id, surname, birth_year, honours_var.get())
            messagebox.showinfo("Success", f"Student added successfully!\nStudent ID: {student_id}")
            dialog.destroy()
            
        ttk.Button(dialog, text="Add Student", command=submit).grid(row=4, column=0, columnspan=2, pady=10)
        
    def show_enter_grades(self):
        if not self.tracker.students:
            messagebox.showwarning("Warning", "No students added yet!")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("Enter Grades")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="Student ID:").grid(row=0, column=0, pady=5, padx=5)
        id_entry = ttk.Entry(dialog)
        id_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(dialog, text="Grades (space-separated):").grid(row=1, column=0, pady=5, padx=5)
        grades_entry = ttk.Entry(dialog)
        grades_entry.grid(row=1, column=1, pady=5, padx=5)
        
        def submit():
            student_id = id_entry.get().strip()
            try:
                grades = list(map(int, grades_entry.get().split()))
                self.tracker.enter_grades(student_id, grades)
                messagebox.showinfo("Success", "Grades added successfully!")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid grades format!")
                
        ttk.Button(dialog, text="Submit Grades", command=submit).grid(row=2, column=0, columnspan=2, pady=10)
        
    def show_reports(self):
        if not self.tracker.students:
            messagebox.showwarning("Warning", "No students added yet!")
            return
            
        has_grades = any(len(student._grades) > 0 for student in self.tracker.students.values())
        if not has_grades:
            messagebox.showwarning("Warning", "No grades entered yet!")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("Student Reports")
        dialog.geometry("400x300")
        
        text_widget = tk.Text(dialog, wrap=tk.WORD, width=40, height=15)
        text_widget.grid(row=0, column=0, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        for student in self.tracker.students.values():
            text_widget.insert(tk.END, student.get_report() + "\n")
        text_widget.configure(state='disabled')

class GradeTracker:
    def __init__(self):
        self.students = {}

    def add_student(self, name, student_id, Surname, Birthyear, honours=False):
        if honours:
            student = HonoursStudent(name, student_id, Surname, Birthyear)
        else:
            student = Student(name, student_id, Surname, Birthyear)
        self.students[student_id] = student

    def enter_grades(self, student_id, grades):
        if student_id in self.students:
            for grade in grades:
                self.students[student_id].add_grade(grade)
        else:
            messagebox.showerror("Error", "Student ID not found!")

if __name__ == "__main__":
    root = tk.Tk()
    app = GradeTrackerGUI(root)
    root.mainloop()