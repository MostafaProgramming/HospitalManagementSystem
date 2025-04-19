import tkinter as tk
from tkinter import ttk, messagebox

class Student:
    def __init__(self, Firstname, student_id, Surname, Birthyear, subject_count):
        self.name = Firstname
        self.student_id = student_id
        self._grades = []
        self.surname = Surname
        self.birthyear = Birthyear
        self.subject_count = subject_count

    def add_grade(self, grade):
        self._grades.append(grade)

    def calculate_average(self):
        if len(self._grades) == 0:
            return 0
        return sum(self._grades) / len(self._grades)

    def determine_pass_fail(self):
        return self.calculate_average() >= 50

    def get_report(self):
        return (f"Student: {self.name} (ID: {self.student_id})\n"
                f"Grades: {self._grades}\n"
                f"Average: {self.calculate_average():.2f}\n"
                f"Status: {'Pass' if self.determine_pass_fail() else 'Fail'}\n")

class HonoursStudent(Student):
    def determine_pass_fail(self):
        return self.calculate_average() >= 70

class GradeTrackerGUI:
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
        dialog.geometry("300x300")
        
        ttk.Label(dialog, text="First Name:").grid(row=0, column=0, pady=5, padx=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(dialog, text="Surname:").grid(row=1, column=0, pady=5, padx=5)
        surname_entry = ttk.Entry(dialog)
        surname_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(dialog, text="Birth Year:").grid(row=2, column=0, pady=5, padx=5)
        birth_year_entry = ttk.Entry(dialog)
        birth_year_entry.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(dialog, text="Number of Subjects:").grid(row=3, column=0, pady=5, padx=5)
        subjects_entry = ttk.Entry(dialog)
        subjects_entry.grid(row=3, column=1, pady=5, padx=5)
        
        honours_var = tk.BooleanVar()
        ttk.Label(dialog, text="Honours Student:").grid(row=4, column=0, pady=5, padx=5)
        honours_checkbox = ttk.Checkbutton(dialog, variable=honours_var)
        honours_checkbox.grid(row=4, column=1, pady=5, padx=5, sticky='w')
        
        def submit():
            name = name_entry.get().strip()
            surname = surname_entry.get().strip()
            birth_year = birth_year_entry.get().strip()
            
            if not all([name, surname, birth_year]):
                messagebox.showerror("Error", "All fields are required!")
                return
                
            subject_count = int(subjects_entry.get().strip())
            student_id = name[0:3] + surname[0:3] + birth_year
            self.tracker.add_student(name, student_id, surname, birth_year, honours_var.get(), subject_count)
            messagebox.showinfo("Success", f"Student added successfully!\nStudent ID: {student_id}")
            dialog.destroy()
            
        ttk.Button(dialog, text="Add Student", command=submit).grid(row=5, column=0, columnspan=2, pady=10)
        
    def show_enter_grades(self):
        if not self.tracker.students:
            messagebox.showwarning("Warning", "No students added yet!")
            return

        # First dialog for student ID
        id_dialog = tk.Toplevel(self.root)
        id_dialog.title("Enter Student ID")
        id_dialog.geometry("300x120")
        
        ttk.Label(id_dialog, text="Student ID:").grid(row=0, column=0, pady=5, padx=5)
        id_entry = ttk.Entry(id_dialog)
        id_entry.grid(row=0, column=1, pady=5, padx=5)
        
        def check_id():
            student_id = id_entry.get().strip()
            if student_id in self.tracker.students:
                id_dialog.destroy()
                self.show_grade_entry_form(student_id)
            else:
                messagebox.showerror("Error", "Student ID not found!")
        
        ttk.Button(id_dialog, text="Continue", command=check_id).grid(row=1, column=0, columnspan=2, pady=10)
        
    def show_grade_entry_form(self, student_id):
        dialog = tk.Toplevel(self.root)
        dialog.title("Enter Grades")
        subject_count = self.tracker.students[student_id].subject_count
        dialog.geometry(f"300x{100 + subject_count * 40}")
        
        grade_entries = []
        for i in range(subject_count):
            ttk.Label(dialog, text=f"Grade {i+1}:").grid(row=i, column=0, pady=5, padx=5)
            entry = ttk.Entry(dialog)
            entry.grid(row=i, column=1, pady=5, padx=5)
            grade_entries.append(entry)
        
        # Configure grid weights for expansion
        dialog.grid_columnconfigure(1, weight=1)
        dialog.grid_rowconfigure(1, weight=1)
        
        def submit():
            try:
                grades = []
                for entry in grade_entries:
                    grade = int(entry.get().strip())
                    grades.append(grade)
                self.tracker.enter_grades(student_id, grades)
                messagebox.showinfo("Success", "Grades added successfully!")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid grade format! Please enter numbers only.")
                
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

    def add_student(self, name, student_id, Surname, Birthyear, honours=False, subject_count=0):
        if honours:
            student = HonoursStudent(name, student_id, Surname, Birthyear, subject_count)
        else:
            student = Student(name, student_id, Surname, Birthyear, subject_count)
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
