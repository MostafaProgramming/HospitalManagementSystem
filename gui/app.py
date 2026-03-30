import datetime
import tkinter as tk
from tkinter import messagebox, ttk

try:
    import winsound
except ImportError:
    winsound = None

from auth import auth_system
from modules import ehr, medication_reminders, medication_stock


CARD_BG = "#f8f1e7"
PAGE_BG = "#efe3d3"
PANEL_BG = "#fffaf4"
ACCENT = "#1f3c4d"
ACCENT_LIGHT = "#2f5b73"
HIGHLIGHT = "#b86b3a"
TEXT = "#24313a"
MUTED = "#6e6e6e"


def launch_app():
    app = HospitalApp()
    app.mainloop()


class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Management System")
        self.geometry("1320x860")
        self.minsize(1120, 720)
        self.configure(bg=PAGE_BG)

        self.current_frame = None
        self._configure_style()
        self.show_login()

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(".", font=("Segoe UI", 10), foreground=TEXT)
        style.configure("App.TFrame", background=PAGE_BG)
        style.configure("Panel.TFrame", background=PANEL_BG)
        style.configure("App.TLabel", background=PAGE_BG, foreground=TEXT)
        style.configure("Panel.TLabel", background=PANEL_BG, foreground=TEXT)
        style.configure(
            "Header.TLabel",
            background=PAGE_BG,
            foreground=ACCENT,
            font=("Georgia", 24, "bold"),
        )
        style.configure(
            "SubHeader.TLabel",
            background=PAGE_BG,
            foreground=MUTED,
            font=("Segoe UI", 11),
        )
        style.configure(
            "Section.TLabelframe",
            background=PANEL_BG,
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "Section.TLabelframe.Label",
            background=PANEL_BG,
            foreground=ACCENT,
            font=("Segoe UI Semibold", 11),
        )
        style.configure(
            "App.TButton",
            background=ACCENT,
            foreground="white",
            borderwidth=0,
            padding=(10, 8),
        )
        style.map("App.TButton", background=[("active", ACCENT_LIGHT)])
        style.configure(
            "Accent.TButton",
            background=HIGHLIGHT,
            foreground="white",
            borderwidth=0,
            padding=(10, 8),
        )
        style.map("Accent.TButton", background=[("active", "#ca8255")])
        style.configure(
            "Treeview",
            rowheight=28,
            fieldbackground="white",
            background="white",
            foreground=TEXT,
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI Semibold", 10),
            background=ACCENT,
            foreground="white",
        )
        style.map("Treeview.Heading", background=[("active", ACCENT_LIGHT)])
        style.configure("TNotebook", background=PAGE_BG, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background="#d8c8b6",
            padding=(16, 8),
            foreground=TEXT,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", ACCENT), ("active", ACCENT_LIGHT)],
            foreground=[("selected", "white")],
        )
        style.configure("TEntry", padding=6)
        style.configure("TCombobox", padding=5)

    def _swap_frame(self, frame_class, **kwargs):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_class(self, **kwargs)
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):
        self._swap_frame(LoginFrame)

    def show_dashboard(self, user):
        self._swap_frame(MainFrame, user=user)


class LoginFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style="App.TFrame", padding=36)
        self.master = master

        form = ttk.Frame(self, style="Panel.TFrame", padding=28)
        form.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(form, text="Welcome back", style="Header.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.role_var = tk.StringVar(value="Doctor")
        self.signup_key_var = tk.StringVar()

        fields = [
            ("Username", self.username_var),
            ("Password", self.password_var),
            ("Role", self.role_var),
            ("Signup Key", self.signup_key_var),
        ]

        for row, (label, variable) in enumerate(fields, start=1):
            ttk.Label(form, text=label, style="Panel.TLabel").grid(
                row=row, column=0, sticky="w", pady=(0, 6)
            )
            if label == "Password":
                widget = ttk.Entry(form, textvariable=variable, show="*", width=30)
            elif label == "Role":
                widget = ttk.Combobox(
                    form,
                    textvariable=variable,
                    width=28,
                    state="readonly",
                    values=("Doctor", "Nurse", "Admin", "Receptionist", "Pharmacist"),
                )
            else:
                widget = ttk.Entry(form, textvariable=variable, width=30)
            widget.grid(row=row, column=1, sticky="ew", pady=(0, 10))

        ttk.Label(
            form,
            text=auth_system.get_signup_key_hint(),
            style="SubHeader.TLabel",
            wraplength=320,
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(4, 14))

        ttk.Button(form, text="Login", style="App.TButton", command=self.login).grid(
            row=6, column=0, sticky="ew", pady=(0, 8)
        )
        ttk.Button(
            form,
            text="Register",
            style="Accent.TButton",
            command=self.register,
        ).grid(row=6, column=1, sticky="ew", padx=(10, 0), pady=(0, 8))

        form.columnconfigure(1, weight=1)

    def login(self):
        try:
            user = auth_system.authenticate_user(
                self.username_var.get(),
                self.password_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Login failed", str(exc))
            return

        self.master.show_dashboard(user)

    def register(self):
        try:
            user = auth_system.register_user(
                self.role_var.get(),
                self.username_var.get(),
                self.password_var.get(),
                self.signup_key_var.get(),
            )
            auth_system.authenticate_user(user["username"], self.password_var.get())
        except ValueError as exc:
            messagebox.showerror("Registration failed", str(exc))
            return

        self.master.show_dashboard(user)


class MainFrame(ttk.Frame):
    def __init__(self, master, user):
        super().__init__(master, style="App.TFrame", padding=20)
        self.master = master
        self.user = user
        self.tabs = []
        self.reminder_popup_windows = {}
        self.reminder_check_job = None

        self._build_header()
        self._build_tabs()
        self._schedule_reminder_check()

    def _build_header(self):
        header = ttk.Frame(self, style="App.TFrame")
        header.pack(fill="x", pady=(0, 16))

        title_block = ttk.Frame(header, style="App.TFrame")
        title_block.pack(side="left", fill="x", expand=True)

        ttk.Label(
            title_block,
            text="Hospital Management System",
            style="Header.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            title_block,
            text="Manage patient records, medication stock, and reminders from one place.",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        user_card = tk.Frame(
            header,
            bg=CARD_BG,
            padx=18,
            pady=14,
            highlightthickness=1,
            highlightbackground="#d8c8b6",
        )
        user_card.pack(side="right")
        tk.Label(
            user_card,
            text=self.user["username"],
            bg=CARD_BG,
            fg=ACCENT,
            font=("Segoe UI Semibold", 12),
        ).pack(anchor="e")
        tk.Label(
            user_card,
            text=f'{self.user["role"]} | {self.user["userID"]}',
            bg=CARD_BG,
            fg=MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="e")
        ttk.Button(
            user_card,
            text="Logout",
            style="Accent.TButton",
            command=self.logout,
        ).pack(anchor="e", pady=(10, 0))

    def _build_tabs(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.dashboard_tab = DashboardTab(notebook, self)
        self.patients_tab = PatientsTab(notebook, self)
        self.medication_tab = MedicationTab(notebook, self)
        self.reminders_tab = RemindersTab(notebook, self)

        self.tabs = [
            self.dashboard_tab,
            self.patients_tab,
            self.medication_tab,
            self.reminders_tab,
        ]

        notebook.add(self.dashboard_tab, text="Dashboard")
        notebook.add(self.patients_tab, text="Patients")
        notebook.add(self.medication_tab, text="Medication")
        notebook.add(self.reminders_tab, text="Reminders")

        notebook.bind("<<NotebookTabChanged>>", lambda _event: self.refresh_all())
        self.refresh_all()

    def refresh_all(self):
        for tab in self.tabs:
            tab.refresh()

    def logout(self):
        if self.reminder_check_job:
            self.after_cancel(self.reminder_check_job)
            self.reminder_check_job = None

        for popup in list(self.reminder_popup_windows.values()):
            if popup.winfo_exists():
                popup.destroy()
        self.reminder_popup_windows.clear()

        auth_system.logout_user()
        self.master.show_login()

    def patient_options(self):
        return [
            f'{patient["patient_id"]} - {patient["first_name"]} {patient["last_name"]}'
            for patient in ehr.list_patients()
        ]

    def medication_options(self):
        return [
            f'{medication["id"]} - {medication["name"]}'
            for medication in medication_stock.list_medications()
        ]

    def _schedule_reminder_check(self):
        self._check_due_reminders()
        self.reminder_check_job = self.after(15000, self._schedule_reminder_check)

    def _check_due_reminders(self):
        for reminder in medication_reminders.list_reminders(due_only=True):
            reminder_id = reminder["reminder_id"]
            popup = self.reminder_popup_windows.get(reminder_id)
            if popup is not None and popup.winfo_exists():
                continue
            self._show_reminder_popup(reminder)

    def _show_reminder_popup(self, reminder):
        reminder_id = reminder["reminder_id"]
        popup = tk.Toplevel(self)
        popup.title("Medication Reminder")
        popup.configure(bg=PANEL_BG)
        popup.resizable(False, False)
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        self.reminder_popup_windows[reminder_id] = popup

        if winsound is not None:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:
            self.bell()

        try:
            patient = ehr.get_patient(reminder["patient_id"])
            patient_name = f'{patient["first_name"]} {patient["last_name"]}'
        except ValueError:
            patient_name = reminder["patient_id"]

        body = (
            f'Medication: {reminder["medication_name"]}\n'
            f'Patient: {patient_name}\n'
            f'Dosage: {reminder["dosage"]}\n'
            f'Frequency: every {reminder["frequency_minutes"]} minutes\n'
            f'Due: {reminder["next_due"]}'
        )

        container = ttk.Frame(popup, style="Panel.TFrame", padding=16)
        container.pack(fill="both", expand=True)
        ttk.Label(container, text="Reminder Due", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            container,
            text=body,
            style="Panel.TLabel",
            justify="left",
        ).pack(anchor="w", pady=(10, 14))

        button_row = ttk.Frame(container, style="Panel.TFrame")
        button_row.pack(fill="x")

        def close_popup():
            popup.grab_release()
            popup.destroy()
            self.reminder_popup_windows.pop(reminder_id, None)

        def administer_now():
            try:
                medication_reminders.administer_reminder(reminder_id)
            except ValueError as exc:
                messagebox.showerror("Reminder not administered", str(exc), parent=popup)
                return
            close_popup()
            self.refresh_all()

        def administer_later():
            try:
                medication_reminders.snooze_reminder(reminder_id, 5)
            except ValueError as exc:
                messagebox.showerror("Reminder not snoozed", str(exc), parent=popup)
                return
            close_popup()
            self.refresh_all()

        popup.protocol("WM_DELETE_WINDOW", administer_later)

        ttk.Button(
            button_row,
            text="Administer Now",
            style="App.TButton",
            command=administer_now,
        ).pack(side="left", fill="x", expand=True)
        ttk.Button(
            button_row,
            text="Later (5 mins)",
            style="Accent.TButton",
            command=administer_later,
        ).pack(side="left", fill="x", expand=True, padx=(10, 0))


class BaseTab(ttk.Frame):
    def __init__(self, master, app_frame):
        super().__init__(master, style="App.TFrame", padding=12)
        self.app_frame = app_frame

    def show_error(self, title, error):
        messagebox.showerror(title, str(error))

    def show_info(self, title, message):
        messagebox.showinfo(title, message)

    @staticmethod
    def _extract_identifier(value):
        if not value:
            return ""
        return value.split(" - ", 1)[0].strip()

    @staticmethod
    def _validate_numeric_input(proposed_value):
        return proposed_value.isdigit() or proposed_value == ""

    def _make_tree(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return tree

    def refresh(self):
        raise NotImplementedError


class DashboardTab(BaseTab):
    def __init__(self, master, app_frame):
        super().__init__(master, app_frame)

        cards = ttk.Frame(self, style="App.TFrame")
        cards.pack(fill="x", pady=(0, 14))
        self.cards = {}

        for key, title in (
            ("patients", "Patients"),
            ("medications", "Medications"),
            ("low_stock", "Low Stock"),
            ("reminders", "Active Reminders"),
        ):
            card = tk.Frame(
                cards,
                bg=CARD_BG,
                padx=18,
                pady=18,
                highlightthickness=1,
                highlightbackground="#d8c8b6",
            )
            card.pack(side="left", fill="both", expand=True, padx=6)
            tk.Label(
                card,
                text=title,
                bg=CARD_BG,
                fg=MUTED,
                font=("Segoe UI Semibold", 10),
            ).pack(anchor="w")
            value = tk.Label(
                card,
                text="0",
                bg=CARD_BG,
                fg=ACCENT,
                font=("Georgia", 24, "bold"),
            )
            value.pack(anchor="w", pady=(8, 0))
            self.cards[key] = value

        lower = ttk.Frame(self, style="App.TFrame")
        lower.pack(fill="both", expand=True)

        low_stock_frame = ttk.LabelFrame(
            lower,
            text="Low Stock Alerts",
            style="Section.TLabelframe",
            padding=12,
        )
        low_stock_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.low_stock_tree = self._make_tree(low_stock_frame, ("id", "name", "stock"))
        for column, heading, width in (
            ("id", "ID", 90),
            ("name", "Medication", 180),
            ("stock", "Stock", 100),
        ):
            self.low_stock_tree.heading(column, text=heading)
            self.low_stock_tree.column(column, width=width, anchor="center")

        reminders_frame = ttk.LabelFrame(
            lower,
            text="Upcoming Reminders",
            style="Section.TLabelframe",
            padding=12,
        )
        reminders_frame.pack(side="left", fill="both", expand=True, padx=(8, 8))
        self.reminder_tree = self._make_tree(
            reminders_frame,
            ("reminder", "patient", "medication", "due"),
        )
        for column, heading, width in (
            ("reminder", "Reminder", 100),
            ("patient", "Patient", 90),
            ("medication", "Medication", 150),
            ("due", "Next Due", 150),
        ):
            self.reminder_tree.heading(column, text=heading)
            self.reminder_tree.column(column, width=width, anchor="center")

        patients_frame = ttk.LabelFrame(
            lower,
            text="Recent Patients",
            style="Section.TLabelframe",
            padding=12,
        )
        patients_frame.pack(side="left", fill="both", expand=True, padx=(8, 0))
        self.patient_tree = self._make_tree(
            patients_frame,
            ("patient", "name", "condition", "updated"),
        )
        for column, heading, width in (
            ("patient", "Patient", 90),
            ("name", "Name", 160),
            ("condition", "Condition", 140),
            ("updated", "Updated", 150),
        ):
            self.patient_tree.heading(column, text=heading)
            self.patient_tree.column(column, width=width, anchor="center")

    def refresh(self):
        patients = ehr.list_patients()
        medications = medication_stock.list_medications()
        low_stock_items = medication_stock.list_medications(low_stock_only=True)
        active_reminders = [
            reminder
            for reminder in medication_reminders.list_reminders()
            if reminder.get("active", True)
        ]

        self.cards["patients"].configure(text=str(len(patients)))
        self.cards["medications"].configure(text=str(len(medications)))
        self.cards["low_stock"].configure(text=str(len(low_stock_items)))
        self.cards["reminders"].configure(text=str(len(active_reminders)))

        self._fill_tree(
            self.low_stock_tree,
            [
                (item["id"], item["name"], f'{item["currentQty"]}/{item["maxStock"]}')
                for item in low_stock_items[:10]
            ],
        )
        self._fill_tree(
            self.reminder_tree,
            [
                (
                    item["reminder_id"],
                    item["patient_id"],
                    item["medication_name"],
                    item["next_due"],
                )
                for item in active_reminders[:10]
            ],
        )
        self._fill_tree(
            self.patient_tree,
            [
                (
                    item["patient_id"],
                    f'{item["first_name"]} {item["last_name"]}',
                    item.get("condition", ""),
                    item.get("updated_at", ""),
                )
                for item in patients[:10]
            ],
        )

    @staticmethod
    def _fill_tree(tree, rows):
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", "end", values=row)


class PatientsTab(BaseTab):
    def __init__(self, master, app_frame):
        super().__init__(master, app_frame)

        top = ttk.Frame(self, style="App.TFrame")
        top.pack(fill="x", pady=(0, 10))

        self.search_var = tk.StringVar()
        ttk.Label(top, text="Search", style="App.TLabel").pack(side="left")
        ttk.Entry(top, textvariable=self.search_var, width=32).pack(
            side="left",
            padx=(8, 8),
        )
        ttk.Button(top, text="Refresh", style="App.TButton", command=self.refresh).pack(
            side="left"
        )

        body = ttk.Frame(self, style="App.TFrame")
        body.pack(fill="both", expand=True)

        left_shell = ttk.Frame(body, style="App.TFrame")
        left_shell.pack(side="left", fill="y", padx=(0, 10))

        self.form_canvas = tk.Canvas(
            left_shell,
            bg=PAGE_BG,
            highlightthickness=0,
            width=390,
        )
        form_scrollbar = ttk.Scrollbar(
            left_shell,
            orient="vertical",
            command=self.form_canvas.yview,
        )
        self.form_canvas.configure(yscrollcommand=form_scrollbar.set)

        self.form_container = ttk.Frame(self.form_canvas, style="App.TFrame")
        self.form_window = self.form_canvas.create_window(
            (0, 0),
            window=self.form_container,
            anchor="nw",
        )
        self.form_container.bind("<Configure>", self._update_form_scroll_region)
        self.form_canvas.bind("<Configure>", self._resize_form_width)

        self.form_canvas.pack(side="left", fill="y")
        form_scrollbar.pack(side="right", fill="y")

        form = ttk.LabelFrame(
            self.form_container,
            text="Patient Details",
            style="Section.TLabelframe",
            padding=14,
        )
        form.pack(fill="x")

        self.patient_id_var = tk.StringVar()
        self.first_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.dob_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.condition_var = tk.StringVar()
        self.medication_var = tk.StringVar()

        self.notes_text = tk.Text(
            form,
            width=28,
            height=6,
            wrap="word",
            font=("Segoe UI", 10),
        )

        number_validate = (self.register(self._validate_numeric_input), "%P")
        fields = [
            ("Patient ID", self.patient_id_var, True),
            ("First Name", self.first_name_var, False),
            ("Last Name", self.last_name_var, False),
            ("Email", self.email_var, False),
            ("Phone", self.phone_var, False),
            ("Date of Birth", self.dob_var, False),
            ("Condition", self.condition_var, False),
            ("Medication", self.medication_var, False),
        ]

        for row, (label, variable, readonly) in enumerate(fields):
            ttk.Label(form, text=label, style="Panel.TLabel").grid(
                row=row,
                column=0,
                sticky="w",
                pady=(0, 6),
            )
            entry = ttk.Entry(form, textvariable=variable, width=30)
            if readonly:
                entry.configure(state="readonly")
            elif label == "Phone":
                entry.configure(validate="key", validatecommand=number_validate)
            entry.grid(row=row, column=1, sticky="ew", pady=(0, 8))

        ttk.Label(form, text="Notes", style="Panel.TLabel").grid(
            row=len(fields),
            column=0,
            sticky="nw",
            pady=(0, 6),
        )
        self.notes_text.grid(
            row=len(fields),
            column=1,
            sticky="ew",
            pady=(0, 8),
        )

        ttk.Button(form, text="Add Patient", style="App.TButton", command=self.add_patient).grid(
            row=len(fields) + 1, column=0, columnspan=2, sticky="ew", pady=(6, 6)
        )
        ttk.Button(
            form,
            text="Update Patient",
            style="Accent.TButton",
            command=self.update_patient,
        ).grid(row=len(fields) + 2, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        ttk.Button(
            form,
            text="Delete Patient",
            style="Accent.TButton",
            command=self.delete_patient,
        ).grid(row=len(fields) + 3, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        ttk.Button(
            form,
            text="Clear Form",
            style="Accent.TButton",
            command=self.clear_form,
        ).grid(row=len(fields) + 4, column=0, columnspan=2, sticky="ew")

        table_frame = ttk.LabelFrame(
            body,
            text="Patient Records",
            style="Section.TLabelframe",
            padding=12,
        )
        table_frame.pack(side="left", fill="both", expand=True)
        self.tree = self._make_tree(
            table_frame,
            ("patient_id", "name", "dob", "condition", "medication"),
        )
        for column, heading, width in (
            ("patient_id", "Patient ID", 90),
            ("name", "Name", 180),
            ("dob", "DOB", 100),
            ("condition", "Condition", 180),
            ("medication", "Medication", 160),
        ):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, anchor="center")
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _update_form_scroll_region(self, _event):
        self.form_canvas.configure(scrollregion=self.form_canvas.bbox("all"))

    def _resize_form_width(self, event):
        self.form_canvas.itemconfigure(self.form_window, width=event.width)

    def _notes(self):
        return self.notes_text.get("1.0", "end").strip()

    def _set_notes(self, text):
        self.notes_text.delete("1.0", "end")
        self.notes_text.insert("1.0", text)

    def _current_payload(self):
        return {
            "first_name": self.first_name_var.get(),
            "last_name": self.last_name_var.get(),
            "email": self.email_var.get(),
            "phone": self.phone_var.get(),
            "dob": self.dob_var.get(),
            "condition": self.condition_var.get(),
            "medication": self.medication_var.get(),
            "notes": self._notes(),
        }

    def add_patient(self):
        try:
            patient = ehr.add_patient(**self._current_payload())
        except ValueError as exc:
            self.show_error("Patient not added", exc)
            return

        self.show_info("Patient added", f'Patient {patient["patient_id"]} was added.')
        self.clear_form()
        self.app_frame.refresh_all()

    def update_patient(self):
        patient_id = self.patient_id_var.get().strip()
        if not patient_id:
            self.show_error("No patient selected", "Select a patient to update.")
            return

        try:
            patient = ehr.update_patient(patient_id=patient_id, **self._current_payload())
        except ValueError as exc:
            self.show_error("Patient not updated", exc)
            return

        self.show_info("Patient updated", f'Patient {patient["patient_id"]} was updated.')
        self.app_frame.refresh_all()

    def delete_patient(self):
        patient_id = self.patient_id_var.get().strip()
        if not patient_id:
            self.show_error("No patient selected", "Select a patient to delete.")
            return

        if not messagebox.askyesno(
            "Delete patient",
            f"Delete patient {patient_id}?",
            parent=self,
        ):
            return

        try:
            ehr.delete_patient(patient_id)
        except ValueError as exc:
            self.show_error("Patient not deleted", exc)
            return

        self.show_info("Patient deleted", f"Patient {patient_id} was deleted.")
        self.clear_form()
        self.app_frame.refresh_all()

    def clear_form(self):
        self.patient_id_var.set("")
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.dob_var.set(datetime.date.today().strftime("%Y-%m-%d"))
        self.condition_var.set("")
        self.medication_var.set("")
        self._set_notes("")

    def _on_tree_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return

        patient_id = self.tree.item(selected[0], "values")[0]
        patient = ehr.get_patient(patient_id)
        self.patient_id_var.set(patient["patient_id"])
        self.first_name_var.set(patient["first_name"])
        self.last_name_var.set(patient["last_name"])
        self.email_var.set(patient["email"])
        self.phone_var.set(patient["phone"])
        self.dob_var.set(patient["dob"])
        self.condition_var.set(patient.get("condition", ""))
        self.medication_var.set(patient.get("medication", ""))
        self._set_notes(patient.get("notes", ""))

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for patient in ehr.list_patients(search_text=self.search_var.get()):
            self.tree.insert(
                "",
                "end",
                values=(
                    patient["patient_id"],
                    f'{patient["first_name"]} {patient["last_name"]}',
                    patient["dob"],
                    patient.get("condition", ""),
                    patient.get("medication", ""),
                ),
            )


class MedicationTab(BaseTab):
    def __init__(self, master, app_frame):
        super().__init__(master, app_frame)

        body = ttk.Frame(self, style="App.TFrame")
        body.pack(fill="both", expand=True)

        left_shell = ttk.Frame(body, style="App.TFrame")
        left_shell.pack(side="left", fill="y", padx=(0, 10))

        self.form_canvas = tk.Canvas(
            left_shell,
            bg=PAGE_BG,
            highlightthickness=0,
            width=410,
        )
        form_scrollbar = ttk.Scrollbar(
            left_shell,
            orient="vertical",
            command=self.form_canvas.yview,
        )
        self.form_canvas.configure(yscrollcommand=form_scrollbar.set)

        self.form_container = ttk.Frame(self.form_canvas, style="App.TFrame")
        self.form_window = self.form_canvas.create_window(
            (0, 0),
            window=self.form_container,
            anchor="nw",
        )
        self.form_container.bind("<Configure>", self._update_form_scroll_region)
        self.form_canvas.bind("<Configure>", self._resize_form_width)

        self.form_canvas.pack(side="left", fill="y")
        form_scrollbar.pack(side="right", fill="y")

        form = ttk.LabelFrame(
            self.form_container,
            text="Inventory Actions",
            style="Section.TLabelframe",
            padding=14,
        )
        form.pack(fill="x")

        self.medication_id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.max_stock_var = tk.StringVar()
        self.reorder_level_var = tk.StringVar()
        self.initial_qty_var = tk.StringVar()
        self.patient_choice_var = tk.StringVar()
        self.dosage_var = tk.StringVar()
        self.resupply_var = tk.StringVar()
        number_validate = (self.register(self._validate_numeric_input), "%P")

        fields = [
            ("Medication ID", self.medication_id_var, True),
            ("Name", self.name_var, False),
            ("Category", self.category_var, False),
            ("Description", self.description_var, False),
            ("Max Stock", self.max_stock_var, False),
            ("Reorder Level", self.reorder_level_var, False),
            ("Initial Qty", self.initial_qty_var, False),
        ]

        for row, (label, variable, readonly) in enumerate(fields):
            ttk.Label(form, text=label, style="Panel.TLabel").grid(
                row=row, column=0, sticky="w", pady=(0, 6)
            )
            entry = ttk.Entry(form, textvariable=variable, width=28)
            if readonly:
                entry.configure(state="readonly")
            elif label in {"Max Stock", "Reorder Level", "Initial Qty"}:
                entry.configure(validate="key", validatecommand=number_validate)
            entry.grid(row=row, column=1, sticky="ew", pady=(0, 8))

        ttk.Button(
            form,
            text="Add Medication",
            style="App.TButton",
            command=self.add_medication,
        ).grid(row=7, column=0, columnspan=2, sticky="ew", pady=(6, 6))
        ttk.Button(
            form,
            text="Delete Medication",
            style="Accent.TButton",
            command=self.delete_medication,
        ).grid(row=8, column=0, columnspan=2, sticky="ew")

        ttk.Separator(form, orient="horizontal").grid(
            row=9, column=0, columnspan=2, sticky="ew", pady=8
        )

        ttk.Label(form, text="Resupply Amount", style="Panel.TLabel").grid(
            row=10, column=0, sticky="w", pady=(0, 6)
        )
        resupply_entry = ttk.Entry(form, textvariable=self.resupply_var, width=28)
        resupply_entry.configure(validate="key", validatecommand=number_validate)
        resupply_entry.grid(row=10, column=1, sticky="ew", pady=(0, 8))
        ttk.Button(
            form,
            text="Resupply",
            style="Accent.TButton",
            command=self.resupply_medication,
        ).grid(row=11, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        ttk.Label(form, text="Patient", style="Panel.TLabel").grid(
            row=12, column=0, sticky="w", pady=(0, 6)
        )
        self.patient_choice = ttk.Combobox(
            form,
            textvariable=self.patient_choice_var,
            width=26,
            state="readonly",
        )
        self.patient_choice.grid(row=12, column=1, sticky="ew", pady=(0, 8))

        ttk.Label(form, text="Dosage", style="Panel.TLabel").grid(
            row=13, column=0, sticky="w", pady=(0, 6)
        )
        dosage_entry = ttk.Entry(form, textvariable=self.dosage_var, width=28)
        dosage_entry.configure(validate="key", validatecommand=number_validate)
        dosage_entry.grid(row=13, column=1, sticky="ew", pady=(0, 8))

        ttk.Button(
            form,
            text="Administer",
            style="App.TButton",
            command=self.administer_medication,
        ).grid(row=14, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Button(
            form,
            text="Clear Form",
            style="Accent.TButton",
            command=self.clear_form,
        ).grid(row=15, column=0, columnspan=2, sticky="ew")

        table_frame = ttk.LabelFrame(
            body,
            text="Medication Stock",
            style="Section.TLabelframe",
            padding=12,
        )
        table_frame.pack(side="left", fill="both", expand=True)

        self.tree = self._make_tree(
            table_frame,
            ("id", "name", "category", "stock", "reorder"),
        )
        for column, heading, width in (
            ("id", "ID", 90),
            ("name", "Name", 180),
            ("category", "Category", 140),
            ("stock", "Stock", 120),
            ("reorder", "Reorder Level", 120),
        ):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, anchor="center")
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _update_form_scroll_region(self, _event):
        self.form_canvas.configure(scrollregion=self.form_canvas.bbox("all"))

    def _resize_form_width(self, event):
        self.form_canvas.itemconfigure(self.form_window, width=event.width)

    def add_medication(self):
        initial_qty = self.initial_qty_var.get().strip()
        try:
            medication = medication_stock.add_medication(
                name=self.name_var.get(),
                category=self.category_var.get(),
                description=self.description_var.get(),
                max_stock=int(self.max_stock_var.get()),
                reorder_level=int(self.reorder_level_var.get()),
                initial_qty=int(initial_qty) if initial_qty else None,
            )
        except (TypeError, ValueError) as exc:
            self.show_error("Medication not added", exc)
            return

        self.show_info("Medication added", f'{medication["name"]} was added.')
        self.clear_form()
        self.app_frame.refresh_all()

    def delete_medication(self):
        medication_id = self.medication_id_var.get().strip()
        if not medication_id:
            self.show_error("No medication selected", "Select a medication to delete.")
            return

        if not messagebox.askyesno(
            "Delete medication",
            f"Delete medication {medication_id}?",
            parent=self,
        ):
            return

        try:
            medication_stock.delete_medication(medication_id)
        except ValueError as exc:
            self.show_error("Medication not deleted", exc)
            return

        self.show_info("Medication deleted", f"Medication {medication_id} was deleted.")
        self.clear_form()
        self.app_frame.refresh_all()

    def resupply_medication(self):
        medication_id = self.medication_id_var.get().strip()
        if not medication_id:
            self.show_error("No medication selected", "Select a medication to resupply.")
            return

        try:
            medication = medication_stock.resupply_medication(
                medication_id,
                int(self.resupply_var.get()),
            )
        except (TypeError, ValueError) as exc:
            self.show_error("Medication not resupplied", exc)
            return

        self.show_info(
            "Medication resupplied",
            f'Stock is now {medication["currentQty"]}/{medication["maxStock"]}.',
        )
        self.resupply_var.set("")
        self.app_frame.refresh_all()

    def administer_medication(self):
        medication_id = self.medication_id_var.get().strip()
        patient_id = self._extract_identifier(self.patient_choice_var.get())
        if not medication_id or not patient_id:
            self.show_error(
                "Missing information",
                "Select a medication and a patient before administering medication.",
            )
            return

        try:
            medication_stock.administer_medication(
                medication_id,
                patient_id,
                int(self.dosage_var.get()),
            )
        except (TypeError, ValueError) as exc:
            self.show_error("Medication not administered", exc)
            return

        self.show_info("Medication administered", "The dosage was recorded successfully.")
        self.dosage_var.set("")
        self.app_frame.refresh_all()

    def clear_form(self):
        self.medication_id_var.set("")
        self.name_var.set("")
        self.category_var.set("")
        self.description_var.set("")
        self.max_stock_var.set("")
        self.reorder_level_var.set("")
        self.initial_qty_var.set("")
        self.patient_choice_var.set("")
        self.dosage_var.set("")
        self.resupply_var.set("")

    def _on_tree_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return

        medication_id = self.tree.item(selected[0], "values")[0]
        medication = medication_stock.get_medication(medication_id)
        self.medication_id_var.set(medication["id"])
        self.name_var.set(medication["name"])
        self.category_var.set(medication["category"])
        self.description_var.set(medication["description"])
        self.max_stock_var.set(str(medication["maxStock"]))
        self.reorder_level_var.set(str(medication["reorderLevel"]))
        self.initial_qty_var.set(str(medication["currentQty"]))

    def refresh(self):
        self.patient_choice.configure(values=self.app_frame.patient_options())
        self.tree.delete(*self.tree.get_children())
        for medication in medication_stock.list_medications():
            tag = "low" if medication["currentQty"] <= medication["reorderLevel"] else ""
            self.tree.insert(
                "",
                "end",
                values=(
                    medication["id"],
                    medication["name"],
                    medication["category"],
                    f'{medication["currentQty"]}/{medication["maxStock"]}',
                    medication["reorderLevel"],
                ),
                tags=(tag,),
            )
        self.tree.tag_configure("low", background="#ffe8d6")


class RemindersTab(BaseTab):
    def __init__(self, master, app_frame):
        super().__init__(master, app_frame)

        shell = ttk.Frame(self, style="App.TFrame")
        shell.pack(fill="both", expand=True)

        form = ttk.LabelFrame(
            shell,
            text="Medication Reminder",
            style="Section.TLabelframe",
            padding=14,
        )
        form.pack(side="left", fill="y", padx=(0, 10))

        self.reminder_id_var = tk.StringVar()
        self.patient_var = tk.StringVar()
        self.medication_var = tk.StringVar()
        self.dosage_var = tk.StringVar(value="1")
        self.frequency_var = tk.StringVar(value="60")
        self.next_due_var = tk.StringVar(value="60")
        self.snooze_var = tk.StringVar(value="5")
        self.notes_var = tk.StringVar()

        number_validate = (self.register(self._validate_numeric_input), "%P")

        ttk.Label(form, text="Reminder ID", style="Panel.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )
        ttk.Entry(
            form,
            textvariable=self.reminder_id_var,
            width=28,
            state="readonly",
        ).grid(row=0, column=1, sticky="ew", pady=(0, 8))

        ttk.Label(form, text="Patient", style="Panel.TLabel").grid(
            row=1, column=0, sticky="w", pady=(0, 6)
        )
        self.patient_choice = ttk.Combobox(
            form,
            textvariable=self.patient_var,
            width=26,
            state="readonly",
        )
        self.patient_choice.grid(row=1, column=1, sticky="ew", pady=(0, 8))

        ttk.Label(form, text="Medication", style="Panel.TLabel").grid(
            row=2, column=0, sticky="w", pady=(0, 6)
        )
        self.medication_choice = ttk.Combobox(
            form,
            textvariable=self.medication_var,
            width=26,
            state="readonly",
        )
        self.medication_choice.grid(row=2, column=1, sticky="ew", pady=(0, 8))

        for row, (label, variable) in enumerate(
            (
                ("Dosage", self.dosage_var),
                ("Frequency (minutes)", self.frequency_var),
                ("Next Due (min from now)", self.next_due_var),
                ("Notes", self.notes_var),
            ),
            start=3,
        ):
            ttk.Label(form, text=label, style="Panel.TLabel").grid(
                row=row, column=0, sticky="w", pady=(0, 6)
            )
            entry = ttk.Entry(form, textvariable=variable, width=28)
            if label in {"Dosage", "Frequency (minutes)", "Next Due (min from now)"}:
                entry.configure(validate="key", validatecommand=number_validate)
            entry.grid(row=row, column=1, sticky="ew", pady=(0, 8))

        ttk.Button(
            form,
            text="Add Reminder",
            style="App.TButton",
            command=self.add_reminder,
        ).grid(row=7, column=0, columnspan=2, sticky="ew", pady=(6, 6))
        ttk.Button(
            form,
            text="Administer Reminder",
            style="Accent.TButton",
            command=self.administer_reminder,
        ).grid(row=8, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        ttk.Label(form, text="Snooze (minutes)", style="Panel.TLabel").grid(
            row=9, column=0, sticky="w", pady=(0, 6)
        )
        snooze_entry = ttk.Entry(form, textvariable=self.snooze_var, width=28)
        snooze_entry.configure(validate="key", validatecommand=number_validate)
        snooze_entry.grid(row=9, column=1, sticky="ew", pady=(0, 8))
        ttk.Button(
            form,
            text="Snooze Reminder",
            style="Accent.TButton",
            command=self.snooze_reminder,
        ).grid(row=10, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        ttk.Button(
            form,
            text="Toggle Active",
            style="Accent.TButton",
            command=self.toggle_reminder,
        ).grid(row=11, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        ttk.Button(
            form,
            text="Delete Reminder",
            style="Accent.TButton",
            command=self.delete_reminder,
        ).grid(row=12, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        ttk.Button(
            form,
            text="Clear Form",
            style="Accent.TButton",
            command=self.clear_form,
        ).grid(row=13, column=0, columnspan=2, sticky="ew")

        table_frame = ttk.LabelFrame(
            shell,
            text="Reminder List",
            style="Section.TLabelframe",
            padding=12,
        )
        table_frame.pack(side="left", fill="both", expand=True)
        self.tree = self._make_tree(
            table_frame,
            ("id", "patient", "medication", "dose", "frequency", "due", "active"),
        )
        for column, heading, width in (
            ("id", "Reminder ID", 100),
            ("patient", "Patient", 100),
            ("medication", "Medication", 140),
            ("dose", "Dose", 70),
            ("frequency", "Every (min)", 90),
            ("due", "Next Due", 150),
            ("active", "Active", 80),
        ):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, anchor="center")
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def add_reminder(self):
        try:
            reminder = medication_reminders.add_reminder(
                patient_id=self._extract_identifier(self.patient_var.get()),
                medication_id=self._extract_identifier(self.medication_var.get()),
                dosage=int(self.dosage_var.get()),
                frequency_minutes=int(self.frequency_var.get()),
                next_due=self.next_due_var.get(),
                notes=self.notes_var.get(),
            )
        except (TypeError, ValueError) as exc:
            self.show_error("Reminder not added", exc)
            return

        self.show_info("Reminder added", f'Reminder {reminder["reminder_id"]} was added.')
        self.clear_form()
        self.app_frame.refresh_all()

    def administer_reminder(self):
        reminder_id = self.reminder_id_var.get().strip()
        if not reminder_id:
            self.show_error("No reminder selected", "Select a reminder to administer.")
            return

        try:
            medication_reminders.administer_reminder(reminder_id)
        except ValueError as exc:
            self.show_error("Reminder not administered", exc)
            return

        self.show_info("Reminder administered", f"Reminder {reminder_id} was administered.")
        self.app_frame.refresh_all()

    def snooze_reminder(self):
        reminder_id = self.reminder_id_var.get().strip()
        if not reminder_id:
            self.show_error("No reminder selected", "Select a reminder to snooze.")
            return

        try:
            delay_text = self.snooze_var.get().strip()
            delay_minutes = int(delay_text) if delay_text else medication_reminders.DEFAULT_SNOOZE_MINUTES
            medication_reminders.snooze_reminder(reminder_id, delay_minutes)
        except (TypeError, ValueError) as exc:
            self.show_error("Reminder not snoozed", exc)
            return

        self.show_info("Reminder snoozed", f"Reminder {reminder_id} was snoozed.")
        self.app_frame.refresh_all()

    def toggle_reminder(self):
        reminder_id = self.reminder_id_var.get().strip()
        if not reminder_id:
            self.show_error("No reminder selected", "Select a reminder to toggle.")
            return

        try:
            reminder = medication_reminders.toggle_reminder(reminder_id)
        except ValueError as exc:
            self.show_error("Reminder not updated", exc)
            return

        state = "active" if reminder.get("active", True) else "paused"
        self.show_info("Reminder updated", f"Reminder {reminder_id} is now {state}.")
        self.app_frame.refresh_all()

    def delete_reminder(self):
        reminder_id = self.reminder_id_var.get().strip()
        if not reminder_id:
            self.show_error("No reminder selected", "Select a reminder to delete.")
            return

        if not messagebox.askyesno(
            "Delete reminder",
            f"Delete reminder {reminder_id}?",
            parent=self,
        ):
            return

        try:
            medication_reminders.delete_reminder(reminder_id)
        except ValueError as exc:
            self.show_error("Reminder not deleted", exc)
            return

        self.show_info("Reminder deleted", f"Reminder {reminder_id} was deleted.")
        self.clear_form()
        self.app_frame.refresh_all()

    def clear_form(self):
        self.reminder_id_var.set("")
        self.patient_var.set("")
        self.medication_var.set("")
        self.dosage_var.set("1")
        self.frequency_var.set("60")
        self.next_due_var.set("60")
        self.snooze_var.set("5")
        self.notes_var.set("")

    def _on_tree_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return

        reminder_id = self.tree.item(selected[0], "values")[0]
        reminder = medication_reminders.get_reminder(reminder_id)
        self.reminder_id_var.set(reminder["reminder_id"])
        self.patient_var.set(self._choice_for_patient(reminder["patient_id"]))
        self.medication_var.set(self._choice_for_medication(reminder["medication_id"]))
        self.dosage_var.set(str(reminder["dosage"]))
        self.frequency_var.set(str(reminder["frequency_minutes"]))
        self.next_due_var.set("")
        self.snooze_var.set("5")
        self.notes_var.set(reminder.get("notes", ""))

    def _choice_for_patient(self, patient_id):
        for option in self.app_frame.patient_options():
            if option.startswith(f"{patient_id} - "):
                return option
        return patient_id

    def _choice_for_medication(self, medication_id):
        for option in self.app_frame.medication_options():
            if option.startswith(f"{medication_id} - "):
                return option
        return medication_id

    def refresh(self):
        self.patient_choice.configure(values=self.app_frame.patient_options())
        self.medication_choice.configure(values=self.app_frame.medication_options())

        self.tree.delete(*self.tree.get_children())
        for reminder in medication_reminders.list_reminders():
            self.tree.insert(
                "",
                "end",
                values=(
                    reminder["reminder_id"],
                    reminder["patient_id"],
                    reminder["medication_name"],
                    reminder["dosage"],
                    reminder["frequency_minutes"],
                    reminder["next_due"],
                    "Yes" if reminder.get("active", True) else "No",
                ),
            )
