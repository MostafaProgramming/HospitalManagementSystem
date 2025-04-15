import tkinter as tk
from tkinter import ttk, messagebox

class Student:
    def __init__(self, Firstname, student_id, Surname, Birthyear):
        self.name = Firstname
        self.student_id = student_id
        self._grades = []
        self.surname = Surname
        self.birthyear = Birthyear

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
        # Make window fullscreen
        self.root.attributes('-fullscreen', True)
        self.tracker = GradeTracker()
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Configure grid weights
        self.main_frame.grid_columnconfigure(0, weight=1)
        for i in range(4):
            self.main_frame.grid_rowconfigure(i, weight=1)
        
        # Create and pack widgets with larger font and size
        title_label = ttk.Label(
            self.main_frame,
            text="Student Grade Tracker System",
            font=('Helvetica', 24, 'bold')
        )
        title_label.grid(row=0, column=0, pady=30)
        
        # Style configuration for larger buttons
        style = ttk.Style()
        style.configure('Large.TButton', font=('Helvetica', 14))
        
        # Create large buttons
        buttons = [
            ("Add New Student", self.show_add_student),
            ("Enter Grades", self.show_enter_grades),
            ("View Reports", self.show_reports)
        ]
        
        for idx, (text, command) in enumerate(buttons, 1):
            btn = ttk.Button(
                self.main_frame,
                text=text,
                command=command,
                style='Large.TButton'
            )
            btn.grid(row=idx, column=0, pady=20, ipady=20, ipadx=100)
            
        # Add exit button
        exit_btn = ttk.Button(
            self.main_frame,
            text="Exit",
            command=self.root.destroy,
            style='Large.TButton'
        )
        exit_btn.grid(row=len(buttons)+1, column=0, pady=20, ipady=20, ipadx=100)
        
    def show_add_student(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Student")
        dialog.geometry("300x250")
        
        ttk.Label(dialog, text="First Name:").grid(row=0, column=0, pady=5, padx=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(dialog, text="Surname:").grid(row=1, column=0, pady=5, padx=5)
        surname_entry = ttk.Entry(dialog)
        surname_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(dialog, text="Birth Year:").grid(row=2, column=0, pady=5, padx=5)
        birth_year_entry = ttk.Entry(dialog)
        birth_year_entry.grid(row=2, column=1, pady=5, padx=5)
        
        honours_var = tk.BooleanVar()
        ttk.Checkbutton(dialog, text="Honours Student", variable=honours_var).grid(row=3, column=0, columnspan=2, pady=5)
        
        def submit():
            name = name_entry.get().strip()
            surname = surname_entry.get().strip()
            birth_year = birth_year_entry.get().strip()
            
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
        
        ttk.Label(dialog, text="Grades (space-separated):").grid(row=1, column=0, pady=5, padx=5, sticky='n')
        grades_entry = tk.Text(dialog, height=4, width=20, wrap=tk.WORD)
        grades_entry.grid(row=1, column=1, pady=5, padx=5, sticky='nsew')
        
        # Configure grid weights for expansion
        dialog.grid_columnconfigure(1, weight=1)
        dialog.grid_rowconfigure(1, weight=1)
        
        def submit():
            student_id = id_entry.get().strip()
            try:
                grades = list(map(int, grades_entry.get("1.0", "end-1c").split()))
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
