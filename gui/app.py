import datetime
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

try:
    import winsound
except ImportError:
    winsound = None

from auth import auth_system
from modules import (
    ehr,
    medication_reminders,
    medication_stock,
    medical_images,
    room_booking,
    staff_availability,
)


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
        self.geometry("1440x900")
        self.minsize(1180, 780)
        self.configure(bg=PAGE_BG)

        self._configure_style()
        self.current_frame = None
        self.show_login()

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(".", font=("Segoe UI", 10), foreground=TEXT)
        style.configure("App.TFrame", background=PAGE_BG)
        style.configure("Panel.TFrame", background=PANEL_BG)
        style.configure("Card.TFrame", background=CARD_BG, relief="flat")
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

        shell = ttk.Frame(self, style="App.TFrame")
        shell.place(relx=0.5, rely=0.5, anchor="center")

        hero = tk.Frame(shell, bg=ACCENT, padx=28, pady=24)
        hero.grid(row=0, column=0, sticky="nsew")

        form = ttk.Frame(shell, style="Panel.TFrame", padding=28)
        form.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            hero,
            text="Hospital\nManagement\nSystem",
            bg=ACCENT,
            fg="white",
            font=("Georgia", 28, "bold"),
            justify="left",
        ).pack(anchor="w")
        tk.Label(
            hero,
            text=(
                "Desktop NEA build with secure login, patient records, medication "
                "stock, bookings, reminders, staffing, and medical images."
            ),
            bg=ACCENT,
            fg="#e7eef2",
            font=("Segoe UI", 11),
            wraplength=280,
            justify="left",
        ).pack(anchor="w", pady=(18, 0))

        ttk.Label(form, text="Welcome back", style="Header.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            form,
            text="Use an existing account or register a new staff member.",
            style="SubHeader.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 18))

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

        for index, (label, variable) in enumerate(fields, start=2):
            ttk.Label(form, text=label, style="Panel.TLabel").grid(
                row=index, column=0, sticky="w", pady=(0, 6)
            )
            if label == "Password":
                widget = ttk.Entry(form, textvariable=variable, show="*", width=28)
            elif label == "Role":
                widget = ttk.Combobox(
                    form,
                    textvariable=variable,
                    width=26,
                    state="readonly",
                    values=("Doctor", "Nurse", "Admin", "Receptionist", "Radiographer"),
                )
            else:
                widget = ttk.Entry(form, textvariable=variable, width=28)
            widget.grid(row=index, column=1, sticky="ew", pady=(0, 10))

        ttk.Label(
            form,
            text=auth_system.get_signup_key_hint(),
            style="SubHeader.TLabel",
            wraplength=280,
        ).grid(row=6, column=0, columnspan=2, sticky="w", pady=(4, 14))
        ttk.Button(form, text="Login", style="App.TButton", command=self.login).grid(
            row=7, column=0, sticky="ew", pady=(0, 8)
        )
        ttk.Button(
            form,
            text="Register",
            style="Accent.TButton",
            command=self.register,
        ).grid(row=7, column=1, sticky="ew", padx=(10, 0), pady=(0, 8))

        form.columnconfigure(1, weight=1)
        shell.columnconfigure(1, weight=1)

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
        self._build_notebook()
        self._schedule_reminder_check()

    def _build_header(self):
        header = ttk.Frame(self, style="App.TFrame")
        header.pack(fill="x", pady=(0, 16))

        title_block = ttk.Frame(header, style="App.TFrame")
        title_block.pack(side="left", fill="x", expand=True)
        ttk.Label(
            title_block,
            text="Hospital Operations Dashboard",
            style="Header.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            title_block,
            text=(
                "Manage clinical records, staffing, stock, bookings, and follow-up "
                "reminders from one place."
            ),
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
            text=f'{self.user["role"]} • {self.user["userID"]}',
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

    def _build_notebook(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.dashboard_tab = DashboardTab(notebook, self)
        self.patients_tab = PatientsTab(notebook, self)
        self.medication_tab = MedicationTab(notebook, self)
        self.rooms_tab = RoomsTab(notebook, self)
        self.availability_tab = AvailabilityTab(notebook, self)
        self.images_tab = ImagesTab(notebook, self)
        self.reminders_tab = RemindersTab(notebook, self)

        self.tabs = [
            self.dashboard_tab,
            self.patients_tab,
            self.medication_tab,
            self.rooms_tab,
            self.availability_tab,
            self.images_tab,
            self.reminders_tab,
        ]

        notebook.add(self.dashboard_tab, text="Dashboard")
        notebook.add(self.patients_tab, text="Patients")
        notebook.add(self.medication_tab, text="Medication")
        notebook.add(self.rooms_tab, text="Rooms")
        notebook.add(self.availability_tab, text="Staff")
        notebook.add(self.images_tab, text="Images")
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

    def staff_options(self):
        return [
            f'{user["userID"]} - {user["username"]} ({user["role"]})'
            for user in auth_system.list_users()
        ]

    def _schedule_reminder_check(self):
        self._check_due_reminders()
        self.reminder_check_job = self.after(15000, self._schedule_reminder_check)

    def _check_due_reminders(self):
        for reminder in medication_reminders.list_reminders(due_only=True):
            reminder_id = reminder["reminder_id"]

            if reminder_id in self.reminder_popup_windows:
                popup = self.reminder_popup_windows[reminder_id]
                if popup.winfo_exists():
                    continue
                self.reminder_popup_windows.pop(reminder_id, None)

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
        self._play_reminder_alarm()

        try:
            patient = ehr.get_patient(reminder["patient_id"])
            patient_name = f'{patient["first_name"]} {patient["last_name"]}'.strip()
        except ValueError:
            patient_name = reminder["patient_id"]

        body = (
            f'Medication: {reminder["medication_name"]}\n'
            f'Patient: {patient_name}\n'
            f'Dosage: {reminder["dosage"]}\n'
            f'Frequency: every {reminder["frequency_minutes"]} minutes\n'
            f'Due: {reminder["next_due"]}'
        )

        ttk.Frame(popup, style="Panel.TFrame", padding=16).pack(fill="both", expand=True)
        container = popup.winfo_children()[0]
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

    def _play_reminder_alarm(self):
        if winsound is not None:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:
            self.bell()


class BaseTab(ttk.Frame):
    def __init__(self, master, app_frame):
        super().__init__(master, style="App.TFrame", padding=12)
        self.app_frame = app_frame

    def show_error(self, title, error):
        messagebox.showerror(title, str(error))

    def show_info(self, title, message):
        messagebox.showinfo(title, message)

    def refresh(self):
        raise NotImplementedError

    @staticmethod
    def _extract_identifier(combined_value):
        if not combined_value:
            return ""
        return combined_value.split(" - ", 1)[0].strip()

    def _make_tree(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return tree


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
            ("bookings", "Upcoming Bookings"),
            ("staff", "Scheduled Staff"),
            ("due", "Due Reminders"),
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

        bookings_frame = ttk.LabelFrame(
            lower,
            text="Upcoming Bookings",
            style="Section.TLabelframe",
            padding=12,
        )
        bookings_frame.pack(side="left", fill="both", expand=True, padx=8)
        self.booking_tree = self._make_tree(
            bookings_frame,
            ("booking", "room", "patient", "start"),
        )
        for column, heading, width in (
            ("booking", "Booking", 90),
            ("room", "Room", 90),
            ("patient", "Patient", 90),
            ("start", "Start", 150),
        ):
            self.booking_tree.heading(column, text=heading)
            self.booking_tree.column(column, width=width, anchor="center")

        reminders_frame = ttk.LabelFrame(
            lower,
            text="Due Reminders",
            style="Section.TLabelframe",
            padding=12,
        )
        reminders_frame.pack(side="left", fill="both", expand=True, padx=(8, 0))
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

    def refresh(self):
        patients = ehr.list_patients()
        medications = medication_stock.list_medications()
        low_stock_items = medication_stock.list_medications(low_stock_only=True)
        upcoming_bookings = room_booking.list_bookings(upcoming_only=True)[:10]
        staff_items = staff_availability.list_availability()
        due_reminders = medication_reminders.list_reminders(due_only=True)[:10]

        self.cards["patients"].configure(text=str(len(patients)))
        self.cards["medications"].configure(text=str(len(medications)))
        self.cards["low_stock"].configure(text=str(len(low_stock_items)))
        self.cards["bookings"].configure(text=str(len(upcoming_bookings)))
        self.cards["staff"].configure(text=str(len(staff_items)))
        self.cards["due"].configure(text=str(len(due_reminders)))

        self._fill_tree(
            self.low_stock_tree,
            [
                (item["id"], item["name"], f'{item["currentQty"]}/{item["maxStock"]}')
                for item in low_stock_items[:10]
            ],
        )
        self._fill_tree(
            self.booking_tree,
            [
                (
                    item["booking_id"],
                    item["room_id"],
                    item["patient_id"],
                    item["start_time"],
                )
                for item in upcoming_bookings
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
                for item in due_reminders
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

        form = ttk.LabelFrame(
            body,
            text="Patient Details",
            style="Section.TLabelframe",
            padding=14,
        )
        form.pack(side="left", fill="y", padx=(0, 10))

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
            width=30,
            height=7,
            wrap="word",
            font=("Segoe UI", 10),
        )

        fields = [
            ("Patient ID", self.patient_id_var, True),
            ("First Name", self.first_name_var, False),
            ("Last Name", self.last_name_var, False),
            ("Email", self.email_var, False),
            ("Phone", self.phone_var, False),
            ("Date of Birth", self.dob_var, False),
            ("Condition", self.condition_var, False),
            ("Current Medication", self.medication_var, False),
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
            entry.grid(row=row, column=1, sticky="ew", pady=(0, 8))

        ttk.Label(form, text="Notes", style="Panel.TLabel").grid(
            row=len(fields),
            column=0,
            sticky="nw",
            pady=(0, 6),
        )
        self.notes_text.grid(row=len(fields), column=1, sticky="ew", pady=(0, 10))

        buttons = ttk.Frame(form, style="Panel.TFrame")
        buttons.grid(row=len(fields) + 1, column=0, columnspan=2, sticky="ew")
        ttk.Button(
            buttons,
            text="Add Patient",
            style="App.TButton",
            command=self.add_patient,
        ).pack(side="left", fill="x", expand=True)
        ttk.Button(
            buttons,
            text="Update",
            style="Accent.TButton",
            command=self.update_patient,
        ).pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(
            buttons,
            text="Delete",
            style="App.TButton",
            command=self.delete_patient,
        ).pack(side="left", fill="x", expand=True)
        ttk.Button(
            form,
            text="Clear Form",
            style="Accent.TButton",
            command=self.clear_form,
        ).grid(row=len(fields) + 2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        table_frame = ttk.LabelFrame(
            body,
            text="Patient Records",
            style="Section.TLabelframe",
            padding=12,
        )
        table_frame.pack(side="left", fill="both", expand=True)

        self.tree = self._make_tree(
            table_frame,
            ("id", "name", "dob", "condition", "medication"),
        )
        for column, heading, width in (
            ("id", "Patient ID", 100),
            ("name", "Name", 180),
            ("dob", "DOB", 120),
            ("condition", "Condition", 180),
            ("medication", "Medication", 160),
        ):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, anchor="center")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        form.columnconfigure(1, weight=1)

    def _payload(self):
        return {
            "first_name": self.first_name_var.get(),
            "last_name": self.last_name_var.get(),
            "email": self.email_var.get(),
            "phone": self.phone_var.get(),
            "dob": self.dob_var.get(),
            "condition": self.condition_var.get(),
            "medication": self.medication_var.get(),
            "notes": self.notes_text.get("1.0", "end").strip(),
        }

    def add_patient(self):
        try:
            patient = ehr.add_patient(**self._payload())
        except ValueError as exc:
            self.show_error("Patient not added", exc)
            return

        self.show_info("Patient added", f'Created patient {patient["patient_id"]}.')
        self.clear_form()
        self.app_frame.refresh_all()

    def update_patient(self):
        patient_id = self.patient_id_var.get()
        if not patient_id:
            self.show_error("Update patient", "Select a patient first.")
            return

        try:
            ehr.update_patient(patient_id=patient_id, **self._payload())
        except ValueError as exc:
            self.show_error("Patient not updated", exc)
            return

        self.show_info("Patient updated", f"Saved changes to {patient_id}.")
        self.app_frame.refresh_all()

    def delete_patient(self):
        patient_id = self.patient_id_var.get()
        if not patient_id:
            self.show_error("Delete patient", "Select a patient first.")
            return

        if not messagebox.askyesno("Delete patient", f"Delete patient {patient_id}?"):
            return

        try:
            ehr.delete_patient(patient_id)
        except ValueError as exc:
            self.show_error("Patient not deleted", exc)
            return

        self.clear_form()
        self.app_frame.refresh_all()

    def clear_form(self):
        for variable in (
            self.patient_id_var,
            self.first_name_var,
            self.last_name_var,
            self.email_var,
            self.phone_var,
            self.condition_var,
            self.medication_var,
        ):
            variable.set("")
        self.dob_var.set(datetime.date.today().strftime("%Y-%m-%d"))
        self.notes_text.delete("1.0", "end")

    def on_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        patient_id = self.tree.item(selected[0], "values")[0]
        patient = ehr.get_patient(patient_id)
        self.patient_id_var.set(patient["patient_id"])
        self.first_name_var.set(patient.get("first_name", ""))
        self.last_name_var.set(patient.get("last_name", ""))
        self.email_var.set(patient.get("email", ""))
        self.phone_var.set(patient.get("phone", ""))
        self.dob_var.set(patient.get("dob", ""))
        self.condition_var.set(patient.get("condition", ""))
        self.medication_var.set(patient.get("medication", ""))
        self.notes_text.delete("1.0", "end")
        self.notes_text.insert("1.0", patient.get("notes", ""))

    def refresh(self):
        patients = ehr.list_patients(self.search_var.get())
        self.tree.delete(*self.tree.get_children())
        for patient in patients:
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

        left = ttk.LabelFrame(
            body,
            text="Inventory Actions",
            style="Section.TLabelframe",
            padding=14,
        )
        left.pack(side="left", fill="y", padx=(0, 10))

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
            ttk.Label(left, text=label, style="Panel.TLabel").grid(
                row=row,
                column=0,
                sticky="w",
                pady=(0, 6),
            )
            entry = ttk.Entry(left, textvariable=variable, width=28)
            if readonly:
                entry.configure(state="readonly")
            entry.grid(row=row, column=1, sticky="ew", pady=(0, 8))

        ttk.Button(
            left,
            text="Add Medication",
            style="App.TButton",
            command=self.add_medication,
        ).grid(row=7, column=0, columnspan=2, sticky="ew", pady=(6, 6))

        ttk.Separator(left, orient="horizontal").grid(
            row=8,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=8,
        )
        ttk.Label(left, text="Resupply Amount", style="Panel.TLabel").grid(
            row=9,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        ttk.Entry(left, textvariable=self.resupply_var, width=28).grid(
            row=9,
            column=1,
            sticky="ew",
            pady=(0, 8),
        )
        ttk.Button(
            left,
            text="Resupply",
            style="Accent.TButton",
            command=self.resupply_medication,
        ).grid(row=10, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        ttk.Label(left, text="Patient", style="Panel.TLabel").grid(
            row=11,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        self.patient_choice = ttk.Combobox(
            left,
            textvariable=self.patient_choice_var,
            width=26,
        )
        self.patient_choice.grid(row=11, column=1, sticky="ew", pady=(0, 8))
        ttk.Label(left, text="Dosage", style="Panel.TLabel").grid(
            row=12,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        ttk.Entry(left, textvariable=self.dosage_var, width=28).grid(
            row=12,
            column=1,
            sticky="ew",
            pady=(0, 8),
        )
        ttk.Button(
            left,
            text="Administer",
            style="App.TButton",
            command=self.administer_medication,
        ).grid(row=13, column=0, columnspan=2, sticky="ew")
        ttk.Button(
            left,
            text="Clear Form",
            style="Accent.TButton",
            command=self.clear_form,
        ).grid(row=14, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        right = ttk.LabelFrame(
            body,
            text="Medication Stock",
            style="Section.TLabelframe",
            padding=12,
        )
        right.pack(side="left", fill="both", expand=True)

        self.tree = self._make_tree(
            right,
            ("id", "name", "category", "stock", "reorder"),
        )
        for column, heading, width in (
            ("id", "Medication ID", 110),
            ("name", "Name", 190),
            ("category", "Category", 140),
            ("stock", "Stock", 120),
            ("reorder", "Reorder Level", 120),
        ):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, anchor="center")

        self.tree.tag_configure("low", background="#f7d9c9")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        left.columnconfigure(1, weight=1)

    def add_medication(self):
        try:
            medication = medication_stock.add_medication(
                self.name_var.get(),
                self.category_var.get(),
                self.description_var.get(),
                int(self.max_stock_var.get()),
                int(self.reorder_level_var.get()),
                int(self.initial_qty_var.get() or self.max_stock_var.get()),
            )
        except (ValueError, TypeError) as exc:
            self.show_error("Medication not added", exc)
            return

        self.show_info("Medication added", f'Created medication {medication["id"]}.')
        self.clear_form()
        self.app_frame.refresh_all()

    def resupply_medication(self):
        medication_id = self.medication_id_var.get()
        if not medication_id:
            self.show_error("Resupply medication", "Select a medication first.")
            return

        try:
            medication_stock.resupply_medication(
                medication_id,
                int(self.resupply_var.get()),
            )
        except (ValueError, TypeError) as exc:
            self.show_error("Medication not resupplied", exc)
            return

        self.resupply_var.set("")
        self.app_frame.refresh_all()

    def administer_medication(self):
        medication_id = self.medication_id_var.get()
        patient_id = self._extract_identifier(self.patient_choice_var.get())

        if not medication_id:
            self.show_error("Administer medication", "Select a medication first.")
            return

        try:
            medication_stock.administer_medication(
                medication_id,
                patient_id,
                int(self.dosage_var.get()),
            )
        except (ValueError, TypeError) as exc:
            self.show_error("Medication not administered", exc)
            return

        self.dosage_var.set("")
        self.app_frame.refresh_all()

    def clear_form(self):
        for variable in (
            self.medication_id_var,
            self.name_var,
            self.category_var,
            self.description_var,
            self.max_stock_var,
            self.reorder_level_var,
            self.initial_qty_var,
            self.patient_choice_var,
            self.dosage_var,
            self.resupply_var,
        ):
            variable.set("")

    def on_select(self, _event):
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


class RoomsTab(BaseTab):
    def __init__(self, master, app_frame):
        super().__init__(master, app_frame)

        container = ttk.Frame(self, style="App.TFrame")
        container.pack(fill="both", expand=True)

        left_shell = ttk.Frame(container, style="App.TFrame")
        left_shell.pack(side="left", fill="y", padx=(0, 10))

        self.left_canvas = tk.Canvas(
            left_shell,
            bg=PAGE_BG,
            highlightthickness=0,
            width=360,
        )
        left_scrollbar = ttk.Scrollbar(
            left_shell,
            orient="vertical",
            command=self.left_canvas.yview,
        )
        self.left_canvas.configure(yscrollcommand=left_scrollbar.set)

        self.left_form_container = ttk.Frame(self.left_canvas, style="App.TFrame")
        self.left_canvas_window = self.left_canvas.create_window(
            (0, 0),
            window=self.left_form_container,
            anchor="nw",
        )

        self.left_form_container.bind(
            "<Configure>",
            self._update_left_scroll_region,
        )
        self.left_canvas.bind(
            "<Configure>",
            self._resize_left_scroll_window,
        )

        self.left_canvas.pack(side="left", fill="y")
        left_scrollbar.pack(side="right", fill="y")

        left = self.left_form_container

        room_frame = ttk.LabelFrame(
            left,
            text="Add Room",
            style="Section.TLabelframe",
            padding=14,
        )
        room_frame.pack(fill="x")
        self.room_id_var = tk.StringVar()
        self.room_label_var = tk.StringVar()
        self.room_type_var = tk.StringVar(value="Consultation")
        self.capacity_var = tk.StringVar(value="1")
        self.room_notes_var = tk.StringVar()

        for row, (label, variable, readonly) in enumerate(
            (
                ("Room ID", self.room_id_var, True),
                ("Label", self.room_label_var, False),
                ("Type", self.room_type_var, False),
                ("Capacity", self.capacity_var, False),
                ("Notes", self.room_notes_var, False),
            )
        ):
            ttk.Label(room_frame, text=label, style="Panel.TLabel").grid(
                row=row,
                column=0,
                sticky="w",
                pady=(0, 6),
            )
            entry = ttk.Entry(room_frame, textvariable=variable, width=28)
            if readonly:
                entry.configure(state="readonly")
            entry.grid(row=row, column=1, sticky="ew", pady=(0, 8))

        ttk.Button(
            room_frame,
            text="Add Room",
            style="App.TButton",
            command=self.add_room,
        ).grid(row=5, column=0, columnspan=2, sticky="ew")
        ttk.Button(
            room_frame,
            text="Delete Room",
            style="Accent.TButton",
            command=self.delete_room,
        ).grid(row=6, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        booking_frame = ttk.LabelFrame(
            left,
            text="Create Booking",
            style="Section.TLabelframe",
            padding=14,
        )
        booking_frame.pack(fill="x", pady=(12, 0))

        self.booking_room_var = tk.StringVar()
        self.staff_choice_var = tk.StringVar()
        self.booking_patient_var = tk.StringVar()
        default_start = datetime.datetime.now().replace(
            minute=0,
            second=0,
            microsecond=0,
        )
        self.start_time_var = tk.StringVar(
            value=default_start.strftime("%Y-%m-%d %H:%M")
        )
        self.end_time_var = tk.StringVar(
            value=(default_start + datetime.timedelta(hours=1)).strftime(
                "%Y-%m-%d %H:%M"
            )
        )
        self.purpose_var = tk.StringVar(value="Consultation")
        self.detail_booking_id_var = tk.StringVar(value="Select a booking")
        self.detail_room_var = tk.StringVar(value="-")
        self.detail_staff_var = tk.StringVar(value="-")
        self.detail_patient_var = tk.StringVar(value="-")
        self.detail_time_var = tk.StringVar(value="-")
        self.detail_purpose_var = tk.StringVar(value="-")
        self.detail_status_var = tk.StringVar(value="-")

        ttk.Label(booking_frame, text="Room", style="Panel.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        self.room_choice = ttk.Combobox(
            booking_frame,
            textvariable=self.booking_room_var,
            width=26,
        )
        self.room_choice.grid(row=0, column=1, sticky="ew", pady=(0, 8))
        ttk.Label(booking_frame, text="Staff", style="Panel.TLabel").grid(
            row=1,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        self.staff_choice = ttk.Combobox(
            booking_frame,
            textvariable=self.staff_choice_var,
            width=26,
        )
        self.staff_choice.grid(row=1, column=1, sticky="ew", pady=(0, 8))
        ttk.Label(booking_frame, text="Patient", style="Panel.TLabel").grid(
            row=2,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        self.patient_choice = ttk.Combobox(
            booking_frame,
            textvariable=self.booking_patient_var,
            width=26,
        )
        self.patient_choice.grid(row=2, column=1, sticky="ew", pady=(0, 8))

        for row, label, variable in (
            (3, "Start", self.start_time_var),
            (4, "End", self.end_time_var),
            (5, "Purpose", self.purpose_var),
        ):
            ttk.Label(booking_frame, text=label, style="Panel.TLabel").grid(
                row=row,
                column=0,
                sticky="w",
                pady=(0, 6),
            )
            ttk.Entry(booking_frame, textvariable=variable, width=28).grid(
                row=row,
                column=1,
                sticky="ew",
                pady=(0, 8),
            )

        ttk.Button(
            booking_frame,
            text="Find Available Rooms",
            style="Accent.TButton",
            command=self.find_available_rooms,
        ).grid(row=6, column=0, columnspan=2, sticky="ew")
        self.available_rooms_label = ttk.Label(
            booking_frame,
            text="",
            style="SubHeader.TLabel",
            wraplength=280,
        )
        self.available_rooms_label.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(8, 6),
        )
        ttk.Button(
            booking_frame,
            text="Create Booking",
            style="App.TButton",
            command=self.create_booking,
        ).grid(row=8, column=0, columnspan=2, sticky="ew")
        ttk.Button(
            booking_frame,
            text="Cancel Selected Booking",
            style="Accent.TButton",
            command=self.cancel_booking,
        ).grid(row=9, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        details_frame = ttk.LabelFrame(
            left,
            text="Booking Details",
            style="Section.TLabelframe",
            padding=14,
        )
        details_frame.pack(fill="x", pady=(12, 0))

        detail_fields = (
            ("Booking", self.detail_booking_id_var),
            ("Room", self.detail_room_var),
            ("Staff", self.detail_staff_var),
            ("Patient", self.detail_patient_var),
            ("Time", self.detail_time_var),
            ("Purpose", self.detail_purpose_var),
            ("Status", self.detail_status_var),
        )

        for row, (label, variable) in enumerate(detail_fields):
            ttk.Label(details_frame, text=label, style="Panel.TLabel").grid(
                row=row,
                column=0,
                sticky="nw",
                pady=(0, 6),
            )
            ttk.Label(
                details_frame,
                textvariable=variable,
                style="Panel.TLabel",
                wraplength=250,
                justify="left",
            ).grid(row=row, column=1, sticky="w", pady=(0, 6))

        room_frame.columnconfigure(1, weight=1)
        booking_frame.columnconfigure(1, weight=1)
        details_frame.columnconfigure(1, weight=1)

        right = ttk.Frame(container, style="App.TFrame")
        right.pack(side="left", fill="both", expand=True)

        rooms_table = ttk.LabelFrame(
            right,
            text="Rooms",
            style="Section.TLabelframe",
            padding=12,
        )
        rooms_table.pack(fill="both", expand=True, pady=(0, 10))
        self.rooms_tree = self._make_tree(
            rooms_table,
            ("id", "label", "type", "capacity", "status"),
        )
        for column, heading, width in (
            ("id", "Room ID", 90),
            ("label", "Label", 130),
            ("type", "Type", 150),
            ("capacity", "Capacity", 90),
            ("status", "Status", 120),
        ):
            self.rooms_tree.heading(column, text=heading)
            self.rooms_tree.column(column, width=width, anchor="center")
        self.rooms_tree.bind("<<TreeviewSelect>>", self.on_room_select)

        bookings_table = ttk.LabelFrame(
            right,
            text="Bookings",
            style="Section.TLabelframe",
            padding=12,
        )
        bookings_table.pack(fill="both", expand=True)
        self.bookings_tree = self._make_tree(
            bookings_table,
            ("id", "room", "staff", "patient", "start", "end"),
        )
        for column, heading, width in (
            ("id", "Booking ID", 90),
            ("room", "Room", 90),
            ("staff", "Staff", 90),
            ("patient", "Patient", 90),
            ("start", "Start", 150),
            ("end", "End", 150),
        ):
            self.bookings_tree.heading(column, text=heading)
            self.bookings_tree.column(column, width=width, anchor="center")
        self.bookings_tree.bind("<<TreeviewSelect>>", self.on_booking_select)

    def _update_left_scroll_region(self, _event):
        self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))

    def _resize_left_scroll_window(self, event):
        self.left_canvas.itemconfigure(self.left_canvas_window, width=event.width)

    def add_room(self):
        try:
            room = room_booking.add_room(
                self.room_label_var.get(),
                self.room_type_var.get(),
                int(self.capacity_var.get()),
                self.room_notes_var.get(),
            )
        except (ValueError, TypeError) as exc:
            self.show_error("Room not added", exc)
            return

        self.show_info("Room added", f'Created room {room["room_id"]}.')
        self.room_label_var.set("")
        self.room_notes_var.set("")
        self.capacity_var.set("1")
        self.app_frame.refresh_all()

    def delete_room(self):
        room_id = self.room_id_var.get()
        if not room_id:
            self.show_error("Delete room", "Select a room first.")
            return

        try:
            room_booking.delete_room(room_id)
        except ValueError as exc:
            self.show_error("Room not deleted", exc)
            return

        self.room_id_var.set("")
        self.app_frame.refresh_all()

    def find_available_rooms(self):
        try:
            available = room_booking.list_available_rooms(
                self.start_time_var.get(),
                self.end_time_var.get(),
            )
        except ValueError as exc:
            self.show_error("Availability lookup failed", exc)
            return

        labels = ", ".join(room["room_label"] for room in available)
        self.available_rooms_label.configure(
            text=labels or "No rooms available for that timeslot."
        )

    def create_booking(self):
        try:
            booking = room_booking.create_booking(
                self._extract_identifier(self.booking_room_var.get()),
                self._extract_identifier(self.staff_choice_var.get()),
                self._extract_identifier(self.booking_patient_var.get()),
                self.start_time_var.get(),
                self.end_time_var.get(),
                self.purpose_var.get(),
            )
        except ValueError as exc:
            self.show_error("Booking not created", exc)
            return

        self.show_info("Booking created", f'Created booking {booking["booking_id"]}.')
        self.app_frame.refresh_all()
        self._set_booking_details(booking["booking_id"])

    def cancel_booking(self):
        selected = self.bookings_tree.selection()
        if not selected:
            self.show_error("Cancel booking", "Select a booking first.")
            return

        booking_id = self.bookings_tree.item(selected[0], "values")[0]
        try:
            room_booking.cancel_booking(booking_id)
        except ValueError as exc:
            self.show_error("Booking not cancelled", exc)
            return

        self.app_frame.refresh_all()
        self._clear_booking_details()

    def on_room_select(self, _event):
        selected = self.rooms_tree.selection()
        if not selected:
            return

        room_id, label, room_type, capacity, _status = self.rooms_tree.item(
            selected[0],
            "values",
        )
        self.room_id_var.set(room_id)
        self.room_label_var.set(label)
        self.room_type_var.set(room_type)
        self.capacity_var.set(capacity)
        self.booking_room_var.set(f"{room_id} - {label}")

    def on_booking_select(self, _event):
        selected = self.bookings_tree.selection()
        if not selected:
            self._clear_booking_details()
            return

        booking_id = self.bookings_tree.item(selected[0], "values")[0]
        self._set_booking_details(booking_id)

    def _booking_lookup_maps(self):
        rooms = {
            room["room_id"]: room
            for room in room_booking.list_rooms()
        }
        staff = {
            user["userID"]: user
            for user in auth_system.list_users()
        }
        patients = {
            patient["patient_id"]: patient
            for patient in ehr.list_patients()
        }
        return rooms, staff, patients

    def _set_booking_details(self, booking_id):
        booking = next(
            (
                booking_item
                for booking_item in room_booking.list_bookings()
                if booking_item["booking_id"] == booking_id
            ),
            None,
        )

        if booking is None:
            self._clear_booking_details()
            return

        rooms, staff, patients = self._booking_lookup_maps()
        room = rooms.get(booking["room_id"], {})
        staff_member = staff.get(booking["staff_id"], {})
        patient = patients.get(booking["patient_id"], {})

        room_name = room.get("room_label", booking["room_id"])
        staff_name = staff_member.get("username", booking["staff_id"])
        patient_name = " ".join(
            part
            for part in (
                patient.get("first_name", "").strip(),
                patient.get("last_name", "").strip(),
            )
            if part
        ) or booking["patient_id"]

        start_time = datetime.datetime.strptime(
            booking["start_time"],
            "%Y-%m-%d %H:%M",
        )
        end_time = datetime.datetime.strptime(
            booking["end_time"],
            "%Y-%m-%d %H:%M",
        )
        now = datetime.datetime.now()

        if now < start_time:
            booking_status = "Upcoming"
        elif start_time <= now < end_time:
            booking_status = "In progress"
        else:
            booking_status = "Completed"

        self.detail_booking_id_var.set(booking["booking_id"])
        self.detail_room_var.set(f'{booking["room_id"]} - {room_name}')
        self.detail_staff_var.set(
            f'{booking["staff_id"]} - {staff_name} ({staff_member.get("role", "Staff")})'
        )
        self.detail_patient_var.set(f'{booking["patient_id"]} - {patient_name}')
        self.detail_time_var.set(f'{booking["start_time"]} to {booking["end_time"]}')
        self.detail_purpose_var.set(booking.get("purpose", "Consultation"))
        self.detail_status_var.set(booking_status)

    def _clear_booking_details(self):
        self.detail_booking_id_var.set("Select a booking")
        self.detail_room_var.set("-")
        self.detail_staff_var.set("-")
        self.detail_patient_var.set("-")
        self.detail_time_var.set("-")
        self.detail_purpose_var.set("-")
        self.detail_status_var.set("-")

    def refresh(self):
        room_options = [
            f'{room["room_id"]} - {room["room_label"]}'
            for room in room_booking.list_rooms()
        ]
        self.room_choice.configure(values=room_options)
        self.staff_choice.configure(values=self.app_frame.staff_options())
        self.patient_choice.configure(values=self.app_frame.patient_options())

        self.rooms_tree.delete(*self.rooms_tree.get_children())
        for room in room_booking.list_rooms():
            self.rooms_tree.insert(
                "",
                "end",
                values=(
                    room["room_id"],
                    room["room_label"],
                    room["room_type"],
                    room["capacity"],
                    room["status"],
                ),
            )

        self.bookings_tree.delete(*self.bookings_tree.get_children())
        for booking in room_booking.list_bookings():
            self.bookings_tree.insert(
                "",
                "end",
                values=(
                    booking["booking_id"],
                    booking["room_id"],
                    booking["staff_id"],
                    booking["patient_id"],
                    booking["start_time"],
                    booking["end_time"],
                ),
            )

        selected = self.bookings_tree.selection()
        if selected:
            booking_id = self.bookings_tree.item(selected[0], "values")[0]
            self._set_booking_details(booking_id)
        else:
            self._clear_booking_details()


class AvailabilityTab(BaseTab):
    def __init__(self, master, app_frame):
        super().__init__(master, app_frame)

        shell = ttk.Frame(self, style="App.TFrame")
        shell.pack(fill="both", expand=True)

        form = ttk.LabelFrame(
            shell,
            text="Schedule Staff",
            style="Section.TLabelframe",
            padding=14,
        )
        form.pack(side="left", fill="y", padx=(0, 10))

        self.staff_var = tk.StringVar()
        self.shift_date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.shift_start_var = tk.StringVar(value="09:00")
        self.shift_end_var = tk.StringVar(value="17:00")
        self.status_var = tk.StringVar(value="Calculated automatically")
        self.notes_var = tk.StringVar()
        self.record_id_var = tk.StringVar()

        ttk.Label(form, text="Record ID", style="Panel.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        ttk.Entry(
            form,
            textvariable=self.record_id_var,
            width=28,
            state="readonly",
        ).grid(row=0, column=1, sticky="ew", pady=(0, 8))

        ttk.Label(form, text="Staff Member", style="Panel.TLabel").grid(
            row=1,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        self.staff_choice = ttk.Combobox(form, textvariable=self.staff_var, width=26)
        self.staff_choice.grid(row=1, column=1, sticky="ew", pady=(0, 8))

        for row, label, variable in (
            (2, "Shift Date", self.shift_date_var),
            (3, "Shift Start", self.shift_start_var),
            (4, "Shift End", self.shift_end_var),
            (5, "Notes", self.notes_var),
        ):
            ttk.Label(form, text=label, style="Panel.TLabel").grid(
                row=row,
                column=0,
                sticky="w",
                pady=(0, 6),
            )
            widget = ttk.Entry(form, textvariable=variable, width=28)
            widget.grid(row=row, column=1, sticky="ew", pady=(0, 8))

        ttk.Label(form, text="Current Status", style="Panel.TLabel").grid(
            row=6,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        ttk.Entry(
            form,
            textvariable=self.status_var,
            width=28,
            state="readonly",
        ).grid(row=6, column=1, sticky="ew", pady=(0, 4))
        ttk.Label(
            form,
            text="Derived from shift times and active room bookings.",
            style="SubHeader.TLabel",
            wraplength=260,
        ).grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 8))

        ttk.Button(
            form,
            text="Add Availability",
            style="App.TButton",
            command=self.add_availability,
        ).grid(row=8, column=0, columnspan=2, sticky="ew")
        ttk.Button(
            form,
            text="Delete Selected",
            style="Accent.TButton",
            command=self.delete_availability,
        ).grid(row=9, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        form.columnconfigure(1, weight=1)

        table = ttk.LabelFrame(
            shell,
            text="Availability Records",
            style="Section.TLabelframe",
            padding=12,
        )
        table.pack(side="left", fill="both", expand=True)

        self.tree = self._make_tree(
            table,
            ("id", "staff", "role", "date", "start", "end", "status"),
        )
        for column, heading, width in (
            ("id", "Record", 90),
            ("staff", "Staff", 160),
            ("role", "Role", 120),
            ("date", "Date", 110),
            ("start", "Start", 90),
            ("end", "End", 90),
            ("status", "Status", 110),
        ):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, anchor="center")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def add_availability(self):
        try:
            record = staff_availability.add_availability(
                self._extract_identifier(self.staff_var.get()),
                self.shift_date_var.get(),
                self.shift_start_var.get(),
                self.shift_end_var.get(),
                self.notes_var.get(),
            )
        except ValueError as exc:
            self.show_error("Availability not added", exc)
            return

        self.show_info("Availability added", f'Created shift {record["availability_id"]}.')
        self.record_id_var.set("")
        self.app_frame.refresh_all()

    def delete_availability(self):
        availability_id = self.record_id_var.get()
        if not availability_id:
            self.show_error("Delete availability", "Select a record first.")
            return

        try:
            staff_availability.delete_availability(availability_id)
        except ValueError as exc:
            self.show_error("Availability not deleted", exc)
            return

        self.record_id_var.set("")
        self.app_frame.refresh_all()

    def on_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.record_id_var.set(values[0])
        self.staff_var.set(values[1])
        self.shift_date_var.set(values[3])
        self.shift_start_var.set(values[4])
        self.shift_end_var.set(values[5])
        self.status_var.set(values[6])

    def refresh(self):
        self.staff_choice.configure(values=self.app_frame.staff_options())
        self.tree.delete(*self.tree.get_children())
        self.status_var.set("Calculated automatically")
        for record in staff_availability.list_availability():
            display_staff = (
                f'{record["staff_id"]} - {record["staff_name"]} ({record["role"]})'
            )
            self.tree.insert(
                "",
                "end",
                values=(
                    record["availability_id"],
                    display_staff,
                    record["role"],
                    record["shift_date"],
                    record["shift_start"],
                    record["shift_end"],
                    record["status"],
                ),
            )


class ImagesTab(BaseTab):
    def __init__(self, master, app_frame):
        super().__init__(master, app_frame)

        shell = ttk.Frame(self, style="App.TFrame")
        shell.pack(fill="both", expand=True)

        form = ttk.LabelFrame(
            shell,
            text="Attach Medical Image",
            style="Section.TLabelframe",
            padding=14,
        )
        form.pack(side="left", fill="y", padx=(0, 10))

        self.image_id_var = tk.StringVar()
        self.patient_var = tk.StringVar()
        self.image_type_var = tk.StringVar(value="X-Ray")
        self.body_part_var = tk.StringVar()
        self.captured_on_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.file_path_var = tk.StringVar()
        self.notes_var = tk.StringVar()
        self.preview_caption_var = tk.StringVar(value="Choose or select an image to preview it here.")
        self.preview_photo = None

        ttk.Label(form, text="Image ID", style="Panel.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        ttk.Entry(
            form,
            textvariable=self.image_id_var,
            state="readonly",
            width=28,
        ).grid(row=0, column=1, sticky="ew", pady=(0, 8))
        ttk.Label(form, text="Patient", style="Panel.TLabel").grid(
            row=1,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        self.patient_choice = ttk.Combobox(form, textvariable=self.patient_var, width=26)
        self.patient_choice.grid(row=1, column=1, sticky="ew", pady=(0, 8))

        for row, label, variable in (
            (2, "Image Type", self.image_type_var),
            (3, "Body Part", self.body_part_var),
            (4, "Captured On", self.captured_on_var),
            (6, "Notes", self.notes_var),
        ):
            ttk.Label(form, text=label, style="Panel.TLabel").grid(
                row=row,
                column=0,
                sticky="w",
                pady=(0, 6),
            )
            if label == "Image Type":
                widget = ttk.Combobox(
                    form,
                    textvariable=variable,
                    width=26,
                    state="readonly",
                    values=("X-Ray", "MRI", "CT Scan", "Ultrasound", "Photo"),
                )
            else:
                widget = ttk.Entry(form, textvariable=variable, width=28)
            widget.grid(row=row, column=1, sticky="ew", pady=(0, 8))

        ttk.Label(form, text="File Path", style="Panel.TLabel").grid(
            row=5,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        ttk.Entry(form, textvariable=self.file_path_var, width=28).grid(
            row=5,
            column=1,
            sticky="ew",
            pady=(0, 8),
        )
        ttk.Button(
            form,
            text="Browse",
            style="Accent.TButton",
            command=self.browse_file,
        ).grid(row=5, column=2, padx=(8, 0), pady=(0, 8))

        ttk.Button(
            form,
            text="Add Image",
            style="App.TButton",
            command=self.add_image,
        ).grid(row=7, column=0, columnspan=3, sticky="ew")
        ttk.Button(
            form,
            text="Delete Selected",
            style="Accent.TButton",
            command=self.delete_image,
        ).grid(row=8, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        form.columnconfigure(1, weight=1)

        right = ttk.Frame(shell, style="App.TFrame")
        right.pack(side="left", fill="both", expand=True)

        table = ttk.LabelFrame(
            right,
            text="Medical Image Register",
            style="Section.TLabelframe",
            padding=12,
        )
        table.pack(fill="x", pady=(0, 10))

        self.tree = self._make_tree(
            table,
            ("id", "patient", "type", "body", "date", "image"),
        )
        for column, heading, width in (
            ("id", "Image ID", 110),
            ("patient", "Patient", 100),
            ("type", "Type", 120),
            ("body", "Body Part", 140),
            ("date", "Captured On", 120),
            ("image", "Image", 220),
        ):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, anchor="center")
        self.tree.configure(height=7)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        preview_frame = ttk.LabelFrame(
            right,
            text="Image Preview",
            style="Section.TLabelframe",
            padding=12,
        )
        preview_frame.pack(fill="both", expand=True)

        self.preview_label = tk.Label(
            preview_frame,
            bg="white",
            fg=MUTED,
            text="No image selected",
            font=("Segoe UI", 10),
            width=64,
            height=24,
            relief="solid",
            bd=1,
            anchor="center",
            justify="center",
        )
        self.preview_label.pack(fill="both", expand=True)
        ttk.Label(
            preview_frame,
            textvariable=self.preview_caption_var,
            style="SubHeader.TLabel",
            wraplength=520,
        ).pack(anchor="w", pady=(8, 0))

    def browse_file(self):
        selected_path = filedialog.askopenfilename(
            title="Choose image file",
            filetypes=(
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff"),
                ("All files", "*.*"),
            ),
        )
        if selected_path:
            self.file_path_var.set(str(Path(selected_path)))
            self._update_preview(selected_path)

    def add_image(self):
        try:
            image = medical_images.add_medical_image(
                self._extract_identifier(self.patient_var.get()),
                self.image_type_var.get(),
                self.body_part_var.get(),
                self.captured_on_var.get(),
                self.file_path_var.get(),
                self.app_frame.user["username"],
                self.notes_var.get(),
            )
        except ValueError as exc:
            self.show_error("Image not added", exc)
            return

        self.show_info("Medical image added", f'Created image record {image["image_id"]}.')
        self._update_preview(image["file_path"])
        self.image_id_var.set("")
        self.notes_var.set("")
        self.app_frame.refresh_all()

    def delete_image(self):
        image_id = self.image_id_var.get()
        if not image_id:
            self.show_error("Delete image", "Select an image first.")
            return

        try:
            medical_images.delete_medical_image(image_id)
        except ValueError as exc:
            self.show_error("Image not deleted", exc)
            return

        self.image_id_var.set("")
        self.file_path_var.set("")
        self._clear_preview()
        self.app_frame.refresh_all()

    def on_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return

        image_id = self.tree.item(selected[0], "values")[0]
        image_record = medical_images.get_medical_image(image_id)
        patient_id = image_record["patient_id"]
        self.image_id_var.set(image_id)
        patient = ehr.get_patient(patient_id)
        self.patient_var.set(
            f'{patient_id} - {patient["first_name"]} {patient["last_name"]}'
        )
        self.image_type_var.set(image_record["image_type"])
        self.body_part_var.set(image_record["body_part"])
        self.captured_on_var.set(image_record["captured_on"])
        self.file_path_var.set(image_record["file_path"])
        self.notes_var.set(image_record.get("notes", ""))
        self._update_preview(image_record["file_path"])

    def refresh(self):
        self.patient_choice.configure(values=self.app_frame.patient_options())
        self.tree.delete(*self.tree.get_children())
        for image in medical_images.list_medical_images():
            self.tree.insert(
                "",
                "end",
                values=(
                    image["image_id"],
                    image["patient_id"],
                    image["image_type"],
                    image["body_part"],
                    image["captured_on"],
                    Path(image["file_path"]).name if image["file_path"] else "No file",
                ),
            )

    def _clear_preview(self, message="No image selected"):
        self.preview_photo = None
        self.preview_label.configure(image="", text=message)
        self.preview_caption_var.set("Choose or select an image to preview it here.")

    def _update_preview(self, file_path):
        path = Path(file_path)

        if not file_path or not path.exists():
            self._clear_preview("Image file not found")
            return

        try:
            photo = tk.PhotoImage(file=str(path))
        except tk.TclError:
            self.preview_photo = None
            self.preview_label.configure(
                image="",
                text="Preview unavailable for this file type.\nUse PNG or GIF for built-in preview.",
            )
            self.preview_caption_var.set(str(path))
            return

        max_width = 900
        max_height = 520
        width = photo.width()
        height = photo.height()
        width_scale = max(1, (width + max_width - 1) // max_width)
        height_scale = max(1, (height + max_height - 1) // max_height)
        scale = max(width_scale, height_scale)

        if scale > 1:
            photo = photo.subsample(scale, scale)

        self.preview_photo = photo
        self.preview_label.configure(image=self.preview_photo, text="")
        self.preview_caption_var.set(str(path))


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
        self.next_due_var = tk.StringVar(
            value=(datetime.datetime.now() + datetime.timedelta(minutes=60)).strftime(
                "%Y-%m-%d %H:%M"
            )
        )
        self.notes_var = tk.StringVar()

        ttk.Label(form, text="Reminder ID", style="Panel.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        ttk.Entry(
            form,
            textvariable=self.reminder_id_var,
            state="readonly",
            width=28,
        ).grid(row=0, column=1, sticky="ew", pady=(0, 8))

        ttk.Label(form, text="Patient", style="Panel.TLabel").grid(
            row=1,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        self.patient_choice = ttk.Combobox(form, textvariable=self.patient_var, width=26)
        self.patient_choice.grid(row=1, column=1, sticky="ew", pady=(0, 8))
        ttk.Label(form, text="Medication", style="Panel.TLabel").grid(
            row=2,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        self.medication_choice = ttk.Combobox(
            form,
            textvariable=self.medication_var,
            width=26,
        )
        self.medication_choice.grid(row=2, column=1, sticky="ew", pady=(0, 8))

        for row, label, variable in (
            (3, "Dosage", self.dosage_var),
            (4, "Frequency (mins)", self.frequency_var),
            (5, "Next Due", self.next_due_var),
            (6, "Notes", self.notes_var),
        ):
            ttk.Label(form, text=label, style="Panel.TLabel").grid(
                row=row,
                column=0,
                sticky="w",
                pady=(0, 6),
            )
            ttk.Entry(form, textvariable=variable, width=28).grid(
                row=row,
                column=1,
                sticky="ew",
                pady=(0, 8),
            )

        ttk.Button(
            form,
            text="Add Reminder",
            style="App.TButton",
            command=self.add_reminder,
        ).grid(row=7, column=0, columnspan=2, sticky="ew")
        ttk.Button(
            form,
            text="Administer Now",
            style="Accent.TButton",
            command=self.administer_selected_reminder,
        ).grid(row=8, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(
            form,
            text="Later (5 mins)",
            style="App.TButton",
            command=self.snooze_selected_reminder,
        ).grid(row=9, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(
            form,
            text="Toggle Active",
            style="Accent.TButton",
            command=self.toggle_reminder,
        ).grid(row=10, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(
            form,
            text="Delete Selected",
            style="App.TButton",
            command=self.delete_reminder,
        ).grid(row=11, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        form.columnconfigure(1, weight=1)

        table = ttk.LabelFrame(
            shell,
            text="Reminder Schedule",
            style="Section.TLabelframe",
            padding=12,
        )
        table.pack(side="left", fill="both", expand=True)

        self.tree = self._make_tree(
            table,
            (
                "id",
                "patient",
                "medication",
                "dosage",
                "frequency",
                "next_due",
                "status",
            ),
        )
        for column, heading, width in (
            ("id", "Reminder ID", 110),
            ("patient", "Patient", 90),
            ("medication", "Medication", 150),
            ("dosage", "Dosage", 80),
            ("frequency", "Every (mins)", 110),
            ("next_due", "Next Due", 150),
            ("status", "Status", 100),
        ):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, anchor="center")

        self.tree.tag_configure("due", background="#f7d9c9")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def add_reminder(self):
        try:
            reminder = medication_reminders.add_reminder(
                self._extract_identifier(self.patient_var.get()),
                self._extract_identifier(self.medication_var.get()),
                int(self.dosage_var.get()),
                int(self.frequency_var.get()),
                self.next_due_var.get(),
                self.notes_var.get(),
            )
        except (ValueError, TypeError) as exc:
            self.show_error("Reminder not added", exc)
            return

        self.show_info("Reminder added", f'Created reminder {reminder["reminder_id"]}.')
        self.app_frame.refresh_all()

    def administer_selected_reminder(self):
        reminder_id = self.reminder_id_var.get()
        if not reminder_id:
            self.show_error("Administer reminder", "Select a reminder first.")
            return

        try:
            medication_reminders.administer_reminder(reminder_id)
        except ValueError as exc:
            self.show_error("Reminder not administered", exc)
            return

        self.app_frame.refresh_all()

    def snooze_selected_reminder(self):
        reminder_id = self.reminder_id_var.get()
        if not reminder_id:
            self.show_error("Snooze reminder", "Select a reminder first.")
            return

        try:
            medication_reminders.snooze_reminder(reminder_id, 5)
        except ValueError as exc:
            self.show_error("Reminder not snoozed", exc)
            return

        self.app_frame.refresh_all()

    def toggle_reminder(self):
        reminder_id = self.reminder_id_var.get()
        if not reminder_id:
            self.show_error("Toggle reminder", "Select a reminder first.")
            return

        try:
            medication_reminders.toggle_reminder(reminder_id)
        except ValueError as exc:
            self.show_error("Reminder not updated", exc)
            return

        self.app_frame.refresh_all()

    def delete_reminder(self):
        reminder_id = self.reminder_id_var.get()
        if not reminder_id:
            self.show_error("Delete reminder", "Select a reminder first.")
            return

        try:
            medication_reminders.delete_reminder(reminder_id)
        except ValueError as exc:
            self.show_error("Reminder not deleted", exc)
            return

        self.reminder_id_var.set("")
        self.app_frame.refresh_all()

    def on_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        reminder_id, patient_id, medication_name, dosage, frequency, next_due, _status = (
            values
        )
        self.reminder_id_var.set(reminder_id)
        patient = ehr.get_patient(patient_id)
        self.patient_var.set(
            f'{patient_id} - {patient["first_name"]} {patient["last_name"]}'
        )
        matched_medication = next(
            (
                option
                for option in self.app_frame.medication_options()
                if option.endswith(f" - {medication_name}")
            ),
            "",
        )
        self.medication_var.set(matched_medication)
        self.dosage_var.set(str(dosage))
        self.frequency_var.set(str(frequency))
        self.next_due_var.set(next_due)

    def refresh(self):
        self.patient_choice.configure(values=self.app_frame.patient_options())
        self.medication_choice.configure(values=self.app_frame.medication_options())
        now = datetime.datetime.now()

        self.tree.delete(*self.tree.get_children())
        for reminder in medication_reminders.list_reminders():
            next_due = datetime.datetime.strptime(
                reminder["next_due"],
                "%Y-%m-%d %H:%M",
            )
            is_due = reminder.get("active", True) and next_due <= now
            status = "Active" if reminder.get("active", True) else "Paused"
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
                    status,
                ),
                tags=("due",) if is_due else (),
            )
