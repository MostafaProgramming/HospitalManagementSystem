import tkinter as tk
from tkinter import ttk, messagebox # Imports the Tkinter library for GUI & the ttk & messagebox modules from Tkinter

class Student: # Defines the student class with attributes & methods for the student
    def __init__(self, Firstname, student_id, Surname, Birthyear, subject_count):
        self.name = Firstname
        self.student_id = student_id
        self._grades = []
        self.surname = Surname
        self.birthyear = Birthyear
        self.subject_count = subject_count

    def add_grade(self, grade): # Adds a grade to the student's list of grades
        self._grades.append(grade)

    def calculate_average(self): # Calculates the average grade of the student
        if len(self._grades) == 0:
            return 0
        return sum(self._grades) / len(self._grades)

    def determine_pass_fail(self): # Determines whether student has passed or failed based on average grade
        return self.calculate_average() >= 50

    def get_report(self): # Returns a string report of the student's details
        return f"Student: {self.name} (ID: {self.student_id})\nGrades: {self._grades}\nAverage: {self.calculate_average():.2f}\nStatus: {'Pass' if self.determine_pass_fail() else 'Fail'}\n" # Returns the student's name, ID, grades, average grade, & pass/fail status as a string

class HonoursStudent(Student):
    def determine_pass_fail(self):
        return self.calculate_average() >= 70

# Defines the HonoursStudent class as a subclass of student, with a different pass/fail threshold

class GradeTrackerGUI: # Defines the GradeTrackerGUI class, which is the main GUI for the grade tracker system.
    def __init__(self, root):
        self.root = root
        self.root.title("Student Grade Tracker")
        self.tracker = GradeTracker()
        
        # Configure window size and centering
        window_width = 500
        window_height = 400
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.configure(bg='#f0f0f0')
        
        # Style configuration
        style = ttk.Style()
        style.configure('MainFrame.TFrame', background='#ffffff')
        style.configure('Header.TLabel', font=('Helvetica', 24, 'bold'), foreground='#2c3e50')
        style.configure('Subheader.TLabel', font=('Helvetica', 12), foreground='#7f8c8d')
        style.configure('Action.TButton', 
                       font=('Helvetica', 11),
                       padding=15,
                       background='#3498db',
                       foreground='#ffffff')
        style.map('Action.TButton',
                 background=[('active', '#2980b9')],
                 foreground=[('active', '#ffffff')])
        
        # Create main frame with improved spacing
        self.main_frame = ttk.Frame(root, style='MainFrame.TFrame')
        self.main_frame.pack(expand=True, fill='both', padx=30, pady=30)
        
        # Create header frame with title and subtitle
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 30))
        ttk.Label(header_frame, 
                 text="Student Grade Tracker",
                 style='Header.TLabel').pack(pady=(0, 5))
        ttk.Label(header_frame,
                 text="Manage student records and grades efficiently",
                 style='Subheader.TLabel').pack()
        
        # Create button frame with enhanced styling
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(expand=True, fill='x', padx=50)
        
        # Create buttons with improved spacing and style
        buttons = [
            ("Add New Student", self.show_add_student),
            ("Enter Grades", self.show_enter_grades),
            ("View Reports", self.show_reports)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(button_frame, text=text, command=command, style='Action.TButton')
            btn.pack(fill='x', pady=10, ipady=5)

    def show_add_student(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Student")
        dialog.geometry("500x550")
        dialog.resizable(False, False)
        dialog.configure(bg='#f0f0f0')
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.eval(f'tk::PlaceWindow {str(dialog)} center')
        
        # Create main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # Configure grid
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Add header
        ttk.Label(main_frame, 
                 text="Add New Student",
                 style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Add form fields
        ttk.Label(main_frame, text="First Name:").grid(row=1, column=0, pady=5, padx=5, sticky='e')
        name_entry = ttk.Entry(main_frame)
        name_entry.grid(row=1, column=1, pady=5, padx=5, sticky='ew')

        ttk.Label(main_frame, text="Surname:").grid(row=2, column=0, pady=5, padx=5, sticky='e')
        surname_entry = ttk.Entry(main_frame)
        surname_entry.grid(row=2, column=1, pady=5, padx=5, sticky='ew')

        ttk.Label(main_frame, text="Birth Year:").grid(row=3, column=0, pady=5, padx=5, sticky='e')
        birth_year_entry = ttk.Entry(main_frame)
        birth_year_entry.grid(row=3, column=1, pady=5, padx=5, sticky='ew')

        ttk.Label(main_frame, text="Number of Subjects:").grid(row=4, column=0, pady=5, padx=5, sticky='e')
        subjects_entry = ttk.Entry(main_frame)
        subjects_entry.grid(row=4, column=1, pady=5, padx=5, sticky='ew')

        honours_var = tk.BooleanVar()
        ttk.Label(main_frame, text="Honours Student:").grid(row=5, column=0, pady=5, padx=5, sticky='e')
        honours_checkbox = ttk.Checkbutton(main_frame, variable=honours_var)
        honours_checkbox.grid(row=5, column=1, pady=5, padx=5, sticky='w')

        def submit(): # Defines the submit method to add the student to the grade tracker system
            name = name_entry.get().strip().upper()
            surname = surname_entry.get().strip().upper()
            birth_year = birth_year_entry.get().strip()

            if not all([name, surname, birth_year]):
                messagebox.showerror("Error", "All fields are required!")
                return

            # Validate birth year
            if not (birth_year.isdigit() and birth_year >= '1945' and birth_year <= '2023'):
                messagebox.showerror("Error", "Birth year must be a number between 1945 and 2023!")
                return

            # Validate subject count
            try:
                subject_count = int(subjects_entry.get().strip())
                if not (1 <= subject_count <= 14):
                    messagebox.showerror("Error", "Subject count must be between 1 and 14!")
                    return
            except ValueError:
                messagebox.showerror("Error", "Subject count must be a number!")
                return

            student_id = name[0:3] + surname[0:3] + birth_year
            self.tracker.add_student(name, student_id, surname, birth_year, honours_var.get(), subject_count)
            messagebox.showinfo("Success", f"Student added successfully!\nStudent ID: {student_id}")
            dialog.destroy()

        ttk.Button(main_frame, text="Add Student", command=submit).grid(row=6, column=0, columnspan=2, pady=20)

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

        # Create a frame for grades
        grades_frame = ttk.Frame(dialog, padding="10")
        grades_frame.grid(row=0, column=0, sticky='nsew')

        for i in range(subject_count):
            ttk.Label(grades_frame, text=f"Grade {i+1}:").grid(row=i, column=0, pady=10, padx=5, sticky='e')
            entry = ttk.Entry(grades_frame, width=20)
            entry.grid(row=i, column=1, pady=10, padx=5, sticky='w')
            grade_entries.append(entry)

        # Configure grid weights for expansion
        dialog.grid_columnconfigure(0, weight=1)
        grades_frame.grid_columnconfigure(1, weight=1)

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

        ttk.Button(dialog, text="Submit Grades", command=submit).grid(row=1, column=0, pady=20, sticky='ew')

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