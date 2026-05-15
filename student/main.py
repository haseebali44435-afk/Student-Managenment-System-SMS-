import customtkinter as ctk # pyright: ignore[reportMissingImports]
from tkinter import messagebox, ttk
from datetime import datetime

# =========================
# THEME SETTINGS
# =========================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# =========================
# MAIN APPLICATION
# =========================

class StudentApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Student Management System")
        self.geometry("1400x800")
        self.resizable(True, True)

        # In-memory data store: roll -> student dict
        self.students = {}
        self.selected_student_roll = None

        # Build layout
        self.create_sidebar()
        self.create_main_area()

        # Show dashboard on launch
        self.navigate_to("Dashboard")

    # =========================
    # ENTER KEY NAVIGATION
    # =========================

    def _bind_enter_nav(self, entries, final_action=None):
        """Bind <Return> to move focus to next entry; last entry calls final_action."""
        for i, entry in enumerate(entries):
            if i + 1 < len(entries):
                nxt = entries[i + 1]
                entry.bind("<Return>", lambda e, n=nxt: n.focus_set())
            elif final_action:
                entry.bind("<Return>", lambda e: final_action())

    # =========================
    # SIDEBAR
    # =========================

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=210, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="🎓 SMS", font=("Arial", 26, "bold")).pack(pady=(22, 2))
        ctk.CTkLabel(self.sidebar, text="Student Management", font=("Arial", 11), text_color="gray").pack()
        ctk.CTkFrame(self.sidebar, height=1, fg_color="gray40").pack(fill="x", padx=15, pady=14)

        nav_items = [
            ("📊", "Dashboard"),
            ("👨‍🎓", "Students"),
            ("📋", "Attendance"),
            ("📝", "Marks"),
            ("💰", "Fees"),
            ("📈", "Analytics"),
            ("⚙️", "Settings"),
        ]

        self.nav_buttons = {}
        for icon, name in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}   {name}",
                anchor="w",
                fg_color="transparent",
                hover_color=("gray75", "gray30"),
                font=("Arial", 14),
                height=40,
                command=lambda n=name: self.navigate_to(n),
            )
            btn.pack(pady=3, padx=12, fill="x")
            self.nav_buttons[name] = btn

    # =========================
    # MAIN AREA & FRAME ROUTER
    # =========================

    def create_main_area(self):
        self.main_area = ctk.CTkFrame(self, corner_radius=0)
        self.main_area.pack(side="left", fill="both", expand=True)

        self.frames = {
            "Dashboard":  self.build_dashboard(),
            "Students":   self.build_students(),
            "Attendance": self.build_attendance(),
            "Marks":      self.build_marks(),
            "Fees":       self.build_fees(),
            "Analytics":  self.build_analytics(),
            "Settings":   self.build_settings(),
        }

    def navigate_to(self, page):
        for f in self.frames.values():
            f.pack_forget()

        for name, btn in self.nav_buttons.items():
            btn.configure(fg_color=("gray70", "gray32") if name == page else "transparent")

        self.frames[page].pack(fill="both", expand=True)

        refresh = {
            "Dashboard":  self.refresh_dashboard,
            "Students":   self.refresh_students_table,
            "Attendance": self.load_attendance_list,
            "Marks":      self.refresh_marks,
            "Fees":       self.refresh_fees,
            "Analytics":  self.refresh_analytics,
        }
        if page in refresh:
            refresh[page]()

    # =========================
    # HELPER: PAGE HEADER
    # =========================

    def page_header(self, parent, title):
        bar = ctk.CTkFrame(parent, height=55, corner_radius=0, fg_color=("gray88", "gray18"))
        bar.pack(fill="x")
        bar.pack_propagate(False)
        ctk.CTkLabel(bar, text=title, font=("Arial", 20, "bold")).pack(side="left", padx=20)

    # =========================
    # HELPER: STAT CARD
    # =========================

    def stat_card(self, parent, col, label, color):
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
        card.grid(row=0, column=col, padx=8, pady=8, sticky="ew")
        parent.columnconfigure(col, weight=1)
        ctk.CTkLabel(card, text=label, font=("Arial", 12)).pack(pady=(14, 2))
        val = ctk.CTkLabel(card, text="—", font=("Arial", 26, "bold"))
        val.pack(pady=(0, 14))
        return val

    # =========================
    # DASHBOARD
    # =========================

    def build_dashboard(self):
        f = ctk.CTkFrame(self.main_area, corner_radius=0)
        self.page_header(f, "📊  Dashboard Overview")

        cards_row = ctk.CTkFrame(f, fg_color="transparent")
        cards_row.pack(fill="x", padx=20, pady=16)

        self.d_total    = self.stat_card(cards_row, 0, "Total Students",  "#1f538d")
        self.d_present  = self.stat_card(cards_row, 1, "Present Today",   "#2d7a2d")
        self.d_pending  = self.stat_card(cards_row, 2, "Fees Pending",    "#8d1f1f")
        self.d_avgmarks = self.stat_card(cards_row, 3, "Average Marks",   "#6b3fa0")

        ctk.CTkLabel(f, text="Recent Students", font=("Arial", 15, "bold")).pack(anchor="w", padx=22, pady=(6, 2))

        tf = ctk.CTkFrame(f)
        tf.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("Name", "Roll", "Department", "Semester", "Attendance %", "Avg Marks")
        self.dash_tree = ttk.Treeview(tf, columns=cols, show="headings", height=14)
        for c in cols:
            self.dash_tree.heading(c, text=c)
            self.dash_tree.column(c, width=170, anchor="center")
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.dash_tree.yview)
        self.dash_tree.configure(yscrollcommand=sb.set)
        self.dash_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        return f

    def refresh_dashboard(self):
        self.d_total.configure(text=str(len(self.students)))

        today = datetime.now().strftime("%Y-%m-%d")
        present = sum(
            1 for s in self.students.values()
            if s.get("attendance", {}).get(today) == "Present"
        )
        self.d_present.configure(text=str(present))

        pending = sum(1 for s in self.students.values() if s.get("fees_status") == "Pending")
        self.d_pending.configure(text=str(pending))

        all_marks = [m for s in self.students.values() for m in s.get("marks", {}).values()]
        self.d_avgmarks.configure(
            text=str(round(sum(all_marks) / len(all_marks), 1)) if all_marks else "—"
        )

        for row in self.dash_tree.get_children():
            self.dash_tree.delete(row)

        for roll, s in self.students.items():
            att = s.get("attendance", {})
            att_pct = (
                f"{round(sum(1 for v in att.values() if v == 'Present') / len(att) * 100)}%"
                if att else "—"
            )
            marks = s.get("marks", {})
            avg_m = round(sum(marks.values()) / len(marks), 1) if marks else "—"
            self.dash_tree.insert("", "end", values=(s["name"], roll, s["department"], s["semester"], att_pct, avg_m))

    # =========================
    # STUDENTS
    # =========================

    def build_students(self):
        f = ctk.CTkFrame(self.main_area, corner_radius=0)
        self.page_header(f, "👨‍🎓  Student Management")

        # --- Form ---
        form = ctk.CTkFrame(f)
        form.pack(fill="x", padx=20, pady=12)

        fields = [
            ("Full Name *",   "sf_name"),
            ("Roll Number *", "sf_roll"),
            ("Department",    "sf_dept"),
            ("Semester",      "sf_sem"),
            ("Email",         "sf_email"),
            ("Phone",         "sf_phone"),
        ]
        for i, (ph, attr) in enumerate(fields):
            row, col = divmod(i, 3)
            e = ctk.CTkEntry(form, placeholder_text=ph, width=240)
            e.grid(row=row, column=col, padx=10, pady=8, sticky="w")
            setattr(self, attr, e)

        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.grid(row=2, column=0, columnspan=3, pady=8, sticky="w")

        ctk.CTkButton(btn_row, text="➕  Add",    width=130, command=self.add_student).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="✏️  Update", width=130, fg_color="#2d7a2d", command=self.update_student).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="🗑️  Delete", width=130, fg_color="#8d1f1f", command=self.delete_student).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="🧹  Clear",  width=130, fg_color="gray40",  command=self.clear_student_form).pack(side="left", padx=5)

        # --- Search bar ---
        sbar = ctk.CTkFrame(f, fg_color="transparent")
        sbar.pack(fill="x", padx=20, pady=(0, 8))
        self.s_search = ctk.CTkEntry(sbar, placeholder_text="🔍  Search by name, roll or department…", width=340)
        self.s_search.pack(side="left", padx=5)
        self.s_search.bind("<KeyRelease>", lambda e: self.search_students())
        ctk.CTkButton(sbar, text="Clear", width=70, fg_color="gray40", command=self.clear_student_search).pack(side="left", padx=4)

        # --- Table ---
        tf = ctk.CTkFrame(f)
        tf.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("Name", "Roll", "Department", "Semester", "Email", "Phone")
        self.student_tree = ttk.Treeview(tf, columns=cols, show="headings", height=16)
        for c in cols:
            self.student_tree.heading(c, text=c)
            self.student_tree.column(c, width=170, anchor="center")
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=sb.set)
        self.student_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.student_tree.bind("<<TreeviewSelect>>", self.on_student_select)

        # --- Enter key navigation across student form fields ---
        self._bind_enter_nav(
            [self.sf_name, self.sf_roll, self.sf_dept, self.sf_sem, self.sf_email, self.sf_phone],
            self.add_student
        )

        return f

    def refresh_students_table(self, data=None):
        for r in self.student_tree.get_children():
            self.student_tree.delete(r)
        src = data if data is not None else self.students
        for roll, s in src.items():
            self.student_tree.insert("", "end", iid=roll, values=(
                s["name"], roll, s["department"], s["semester"],
                s.get("email", ""), s.get("phone", "")
            ))

    def on_student_select(self, _event):
        sel = self.student_tree.selection()
        if not sel:
            return
        roll = sel[0]
        s = self.students.get(roll)
        if not s:
            return
        self.selected_student_roll = roll
        for attr, val in [("sf_name", s["name"]), ("sf_roll", roll),
                           ("sf_dept", s["department"]), ("sf_sem", s["semester"]),
                           ("sf_email", s.get("email", "")), ("sf_phone", s.get("phone", ""))]:
            w = getattr(self, attr)
            w.delete(0, "end")
            w.insert(0, val)

    def add_student(self):
        name = self.sf_name.get().strip()
        roll = self.sf_roll.get().strip()
        if not name or not roll:
            messagebox.showerror("Error", "Name and Roll Number are required!")
            return
        if roll in self.students:
            messagebox.showerror("Error", f"Roll number '{roll}' already exists!")
            return
        self.students[roll] = {
            "name": name, "department": self.sf_dept.get().strip(),
            "semester": self.sf_sem.get().strip(), "email": self.sf_email.get().strip(),
            "phone": self.sf_phone.get().strip(), "attendance": {}, "marks": {},
            "fees_status": "Pending", "fees_amount": 0,
        }
        self.refresh_students_table()
        self.clear_student_form()
        messagebox.showinfo("Success", f"Student '{name}' added!")

    def update_student(self):
        if not self.selected_student_roll:
            messagebox.showwarning("Warning", "Select a student to update.")
            return
        name = self.sf_name.get().strip()
        roll = self.sf_roll.get().strip()
        if not name or not roll:
            messagebox.showerror("Error", "Name and Roll Number are required!")
            return
        old = self.students.pop(self.selected_student_roll)
        old.update({"name": name, "department": self.sf_dept.get().strip(),
                    "semester": self.sf_sem.get().strip(), "email": self.sf_email.get().strip(),
                    "phone": self.sf_phone.get().strip()})
        self.students[roll] = old
        self.selected_student_roll = None
        self.refresh_students_table()
        self.clear_student_form()
        messagebox.showinfo("Updated", "Student updated successfully!")

    def delete_student(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a student to delete.")
            return
        roll = sel[0]
        name = self.students[roll]["name"]
        if messagebox.askyesno("Confirm", f"Delete student '{name}'?"):
            del self.students[roll]
            self.refresh_students_table()
            self.clear_student_form()
            messagebox.showinfo("Deleted", "Student deleted.")

    def clear_student_form(self):
        self.selected_student_roll = None
        for attr in ["sf_name", "sf_roll", "sf_dept", "sf_sem", "sf_email", "sf_phone"]:
            getattr(self, attr).delete(0, "end")

    def search_students(self):
        q = self.s_search.get().strip().lower()
        if not q:
            self.refresh_students_table(); return
        filtered = {r: s for r, s in self.students.items()
                    if q in s["name"].lower() or q in r.lower() or q in s["department"].lower()}
        self.refresh_students_table(filtered)

    def clear_student_search(self):
        self.s_search.delete(0, "end")
        self.refresh_students_table()

    # =========================
    # ATTENDANCE
    # =========================

    def build_attendance(self):
        f = ctk.CTkFrame(self.main_area, corner_radius=0)
        self.page_header(f, "📋  Attendance Management")

        ctrl = ctk.CTkFrame(f, fg_color="transparent")
        ctrl.pack(fill="x", padx=20, pady=12)

        ctk.CTkLabel(ctrl, text="Date (YYYY-MM-DD):").pack(side="left", padx=(0, 6))
        self.att_date = ctk.CTkEntry(ctrl, width=150)
        self.att_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.att_date.pack(side="left", padx=(0, 10))

        # Enter on date field loads attendance
        self.att_date.bind("<Return>", lambda e: self.load_attendance_list())

        ctk.CTkButton(ctrl, text="📋  Load",          width=120, command=self.load_attendance_list).pack(side="left", padx=4)
        ctk.CTkButton(ctrl, text="💾  Save",          width=120, fg_color="#2d7a2d", command=self.save_attendance).pack(side="left", padx=4)
        ctk.CTkButton(ctrl, text="✅  All Present",   width=130, command=lambda: self.mark_all_att("Present")).pack(side="left", padx=4)
        ctk.CTkButton(ctrl, text="❌  All Absent",    width=130, fg_color="#8d1f1f", command=lambda: self.mark_all_att("Absent")).pack(side="left", padx=4)

        # Summary labels
        sumbar = ctk.CTkFrame(f, fg_color="transparent")
        sumbar.pack(fill="x", padx=20)
        self.att_summary_lbl = ctk.CTkLabel(sumbar, text="", font=("Arial", 13))
        self.att_summary_lbl.pack(side="left")

        tf = ctk.CTkFrame(f)
        tf.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("Roll", "Name", "Department", "Semester", "Status")
        self.att_tree = ttk.Treeview(tf, columns=cols, show="headings", height=18)
        for c in cols:
            self.att_tree.heading(c, text=c)
            self.att_tree.column(c, width=180, anchor="center")
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.att_tree.yview)
        self.att_tree.configure(yscrollcommand=sb.set)
        self.att_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.att_tree.bind("<Double-Button-1>", self.toggle_attendance)

        ctk.CTkLabel(f, text="💡  Double-click a row to toggle Present / Absent",
                     text_color="gray", font=("Arial", 11)).pack(pady=4)
        return f

    def load_attendance_list(self):
        date = self.att_date.get().strip()
        for r in self.att_tree.get_children():
            self.att_tree.delete(r)
        present_count = 0
        for roll, s in self.students.items():
            status = s.get("attendance", {}).get(date, "Absent")
            tag = "pres" if status == "Present" else "abs"
            if status == "Present":
                present_count += 1
            self.att_tree.insert("", "end", iid=roll,
                                  values=(roll, s["name"], s["department"], s["semester"], status),
                                  tags=(tag,))
        self.att_tree.tag_configure("pres", background="#1a3d1a")
        self.att_tree.tag_configure("abs",  background="#3d1a1a")
        total = len(self.students)
        self.att_summary_lbl.configure(
            text=f"  Present: {present_count}   Absent: {total - present_count}   Total: {total}"
        )

    def toggle_attendance(self, _event):
        sel = self.att_tree.selection()
        if not sel:
            return
        roll = sel[0]
        date = self.att_date.get().strip()
        cur = self.students[roll].get("attendance", {}).get(date, "Absent")
        self.students[roll].setdefault("attendance", {})[date] = "Absent" if cur == "Present" else "Present"
        self.load_attendance_list()

    def mark_all_att(self, status):
        date = self.att_date.get().strip()
        for roll in self.students:
            self.students[roll].setdefault("attendance", {})[date] = status
        self.load_attendance_list()

    def save_attendance(self):
        date = self.att_date.get().strip()
        messagebox.showinfo("Saved", f"Attendance for {date} saved successfully!")

    # =========================
    # MARKS
    # =========================

    def build_marks(self):
        f = ctk.CTkFrame(self.main_area, corner_radius=0)
        self.page_header(f, "📝  Marks Management")

        form = ctk.CTkFrame(f)
        form.pack(fill="x", padx=20, pady=12)

        fields = [("Roll Number *", "mf_roll"), ("Subject *", "mf_subj"), ("Marks (0-100) *", "mf_val")]
        for i, (ph, attr) in enumerate(fields):
            ctk.CTkLabel(form, text=ph + ":").grid(row=0, column=i * 2, padx=8, pady=8, sticky="e")
            e = ctk.CTkEntry(form, width=160)
            e.grid(row=0, column=i * 2 + 1, padx=8, pady=8)
            setattr(self, attr, e)

        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.grid(row=1, column=0, columnspan=6, pady=6, sticky="w")
        ctk.CTkButton(btn_row, text="➕  Add Marks",    width=140, command=self.add_marks).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="🗑️  Delete Entry", width=140, fg_color="#8d1f1f", command=self.delete_marks).pack(side="left", padx=5)

        # Filter row
        fbar = ctk.CTkFrame(f, fg_color="transparent")
        fbar.pack(fill="x", padx=20, pady=(0, 6))
        ctk.CTkLabel(fbar, text="Filter by Roll:").pack(side="left", padx=(0, 6))
        self.marks_filter = ctk.CTkEntry(fbar, width=180)
        self.marks_filter.pack(side="left", padx=(0, 6))
        ctk.CTkButton(fbar, text="Filter",   width=80, command=self.filter_marks).pack(side="left", padx=4)
        ctk.CTkButton(fbar, text="Show All", width=80, fg_color="gray40", command=self.refresh_marks).pack(side="left", padx=4)

        tf = ctk.CTkFrame(f)
        tf.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("Roll", "Name", "Subject", "Marks", "Grade")
        self.marks_tree = ttk.Treeview(tf, columns=cols, show="headings", height=18)
        for c in cols:
            self.marks_tree.heading(c, text=c)
            self.marks_tree.column(c, width=180, anchor="center")
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.marks_tree.yview)
        self.marks_tree.configure(yscrollcommand=sb.set)
        self.marks_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # --- Enter key navigation across marks form fields ---
        self._bind_enter_nav(
            [self.mf_roll, self.mf_subj, self.mf_val],
            self.add_marks
        )

        return f

    @staticmethod
    def grade(m):
        return "A+" if m >= 90 else "A" if m >= 80 else "B" if m >= 70 else "C" if m >= 60 else "D" if m >= 50 else "F"

    def refresh_marks(self, data=None):
        for r in self.marks_tree.get_children():
            self.marks_tree.delete(r)
        src = data if data is not None else self.students
        for roll, s in src.items():
            for subj, m in s.get("marks", {}).items():
                self.marks_tree.insert("", "end", values=(roll, s["name"], subj, m, self.grade(m)))

    def filter_marks(self):
        roll = self.marks_filter.get().strip()
        self.refresh_marks({r: s for r, s in self.students.items() if r == roll} if roll else None)

    def add_marks(self):
        roll  = self.mf_roll.get().strip()
        subj  = self.mf_subj.get().strip()
        val_s = self.mf_val.get().strip()
        if not roll or not subj or not val_s:
            messagebox.showerror("Error", "All fields are required!"); return
        if roll not in self.students:
            messagebox.showerror("Error", f"Roll '{roll}' not found!"); return
        try:
            val = int(val_s)
            if not (0 <= val <= 100): raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Marks must be 0–100!"); return
        self.students[roll]["marks"][subj] = val
        self.refresh_marks()
        for attr in ["mf_roll", "mf_subj", "mf_val"]:
            getattr(self, attr).delete(0, "end")
        messagebox.showinfo("Success", f"Marks saved for {self.students[roll]['name']} – {subj}!")

    def delete_marks(self):
        sel = self.marks_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a marks entry to delete."); return
        vals = self.marks_tree.item(sel[0])["values"]
        roll, subj = str(vals[0]), str(vals[2])
        if roll in self.students and subj in self.students[roll]["marks"]:
            del self.students[roll]["marks"][subj]
            self.refresh_marks()
            messagebox.showinfo("Deleted", "Marks entry removed.")

    # =========================
    # FEES
    # =========================

    def build_fees(self):
        f = ctk.CTkFrame(self.main_area, corner_radius=0)
        self.page_header(f, "💰  Fees Management")

        form = ctk.CTkFrame(f)
        form.pack(fill="x", padx=20, pady=12)

        ctk.CTkLabel(form, text="Roll Number:").grid(row=0, column=0, padx=8, pady=8, sticky="e")
        self.ff_roll = ctk.CTkEntry(form, width=150); self.ff_roll.grid(row=0, column=1, padx=8)

        ctk.CTkLabel(form, text="Amount (PKR):").grid(row=0, column=2, padx=8, sticky="e")
        self.ff_amount = ctk.CTkEntry(form, width=150); self.ff_amount.grid(row=0, column=3, padx=8)

        ctk.CTkLabel(form, text="Status:").grid(row=0, column=4, padx=8, sticky="e")
        self.ff_status_var = ctk.StringVar(value="Paid")
        ctk.CTkComboBox(form, values=["Paid", "Pending", "Partial"],
                        variable=self.ff_status_var, width=130).grid(row=0, column=5, padx=8)

        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.grid(row=1, column=0, columnspan=6, pady=6, sticky="w")
        ctk.CTkButton(btn_row, text="💾  Update Fees",      width=150, command=self.update_fees).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="✅  Mark All Paid",    width=150, fg_color="#2d7a2d", command=self.mark_all_paid).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="⚠️  Mark All Pending", width=160, fg_color="#8d5f00", command=self.mark_all_pending).pack(side="left", padx=5)

        # Summary cards
        cards = ctk.CTkFrame(f, fg_color="transparent")
        cards.pack(fill="x", padx=20, pady=6)
        self.f_collected = self.stat_card(cards, 0, "Total Collected",  "#1f538d")
        self.f_pend_amt  = self.stat_card(cards, 1, "Pending Amount",   "#8d1f1f")
        self.f_paid_cnt  = self.stat_card(cards, 2, "Students Paid",    "#2d7a2d")
        self.f_pend_cnt  = self.stat_card(cards, 3, "Students Pending", "#8d5f00")

        tf = ctk.CTkFrame(f)
        tf.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        cols = ("Roll", "Name", "Department", "Amount (PKR)", "Status")
        self.fees_tree = ttk.Treeview(tf, columns=cols, show="headings", height=14)
        for c in cols:
            self.fees_tree.heading(c, text=c)
            self.fees_tree.column(c, width=190, anchor="center")
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.fees_tree.yview)
        self.fees_tree.configure(yscrollcommand=sb.set)
        self.fees_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.fees_tree.bind("<<TreeviewSelect>>", self.on_fees_select)

        # --- Enter key navigation across fees form fields ---
        self._bind_enter_nav(
            [self.ff_roll, self.ff_amount],
            self.update_fees
        )

        return f

    def refresh_fees(self):
        for r in self.fees_tree.get_children():
            self.fees_tree.delete(r)
        collected = pending_amt = paid_cnt = pending_cnt = 0
        for roll, s in self.students.items():
            status = s.get("fees_status", "Pending")
            amount = s.get("fees_amount", 0)
            tag    = status.lower()
            self.fees_tree.insert("", "end", iid=roll,
                                   values=(roll, s["name"], s["department"], f"PKR {amount:,}", status),
                                   tags=(tag,))
            if status == "Paid":
                collected += amount; paid_cnt += 1
            elif status == "Pending":
                pending_amt += amount; pending_cnt += 1
        self.fees_tree.tag_configure("paid",    background="#1a3d1a")
        self.fees_tree.tag_configure("pending", background="#3d1a1a")
        self.fees_tree.tag_configure("partial", background="#3d3a1a")
        self.f_collected.configure(text=f"PKR {collected:,}")
        self.f_pend_amt.configure(text=f"PKR {pending_amt:,}")
        self.f_paid_cnt.configure(text=str(paid_cnt))
        self.f_pend_cnt.configure(text=str(pending_cnt))

    def on_fees_select(self, _event):
        sel = self.fees_tree.selection()
        if not sel: return
        roll = sel[0]; s = self.students.get(roll)
        if not s: return
        self.ff_roll.delete(0, "end");   self.ff_roll.insert(0, roll)
        self.ff_amount.delete(0, "end"); self.ff_amount.insert(0, str(s.get("fees_amount", 0)))
        self.ff_status_var.set(s.get("fees_status", "Pending"))

    def update_fees(self):
        roll = self.ff_roll.get().strip()
        if not roll:
            messagebox.showerror("Error", "Roll number is required!"); return
        if roll not in self.students:
            messagebox.showerror("Error", f"Roll '{roll}' not found!"); return
        try:
            amount = int(self.ff_amount.get().strip() or 0)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number!"); return
        self.students[roll]["fees_status"] = self.ff_status_var.get()
        self.students[roll]["fees_amount"] = amount
        self.refresh_fees()
        messagebox.showinfo("Updated", f"Fees updated for {self.students[roll]['name']}!")

    def mark_all_paid(self):
        if messagebox.askyesno("Confirm", "Mark ALL students as Paid?"):
            for roll in self.students: self.students[roll]["fees_status"] = "Paid"
            self.refresh_fees()

    def mark_all_pending(self):
        if messagebox.askyesno("Confirm", "Mark ALL students as Pending?"):
            for roll in self.students: self.students[roll]["fees_status"] = "Pending"
            self.refresh_fees()

    # =========================
    # ANALYTICS
    # =========================

    def build_analytics(self):
        f = ctk.CTkFrame(self.main_area, corner_radius=0)
        self.page_header(f, "📈  Analytics & Reports")

        cards = ctk.CTkFrame(f, fg_color="transparent")
        cards.pack(fill="x", padx=20, pady=14)
        self.an_total = self.stat_card(cards, 0, "Total Students",    "#1f538d")
        self.an_att   = self.stat_card(cards, 1, "Avg Attendance %",  "#2d7a2d")
        self.an_marks = self.stat_card(cards, 2, "Average Marks",     "#6b3fa0")
        self.an_fees  = self.stat_card(cards, 3, "Fees Collection %", "#8d5f00")

        ctk.CTkLabel(f, text="Department-wise Breakdown", font=("Arial", 15, "bold")).pack(anchor="w", padx=22, pady=(6, 2))
        df = ctk.CTkFrame(f); df.pack(fill="x", padx=20, pady=(0, 10))
        dcols = ("Department", "Students", "Avg Marks", "Avg Attendance %", "Fees Paid")
        self.dept_tree = ttk.Treeview(df, columns=dcols, show="headings", height=5)
        for c in dcols:
            self.dept_tree.heading(c, text=c); self.dept_tree.column(c, width=200, anchor="center")
        self.dept_tree.pack(fill="x")

        ctk.CTkLabel(f, text="🏆  Top Performers (by Avg Marks)", font=("Arial", 15, "bold")).pack(anchor="w", padx=22, pady=(6, 2))
        tf = ctk.CTkFrame(f); tf.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        tcols = ("Rank", "Name", "Roll", "Department", "Avg Marks", "Attendance %")
        self.top_tree = ttk.Treeview(tf, columns=tcols, show="headings", height=9)
        for c in tcols:
            self.top_tree.heading(c, text=c); self.top_tree.column(c, width=160, anchor="center")
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.top_tree.yview)
        self.top_tree.configure(yscrollcommand=sb.set)
        self.top_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        return f

    def refresh_analytics(self):
        total = len(self.students)
        self.an_total.configure(text=str(total))

        att_pcts = []
        for s in self.students.values():
            att = s.get("attendance", {})
            if att:
                att_pcts.append(sum(1 for v in att.values() if v == "Present") / len(att) * 100)
        self.an_att.configure(text=f"{round(sum(att_pcts)/len(att_pcts),1)}%" if att_pcts else "—")

        all_m = [m for s in self.students.values() for m in s.get("marks", {}).values()]
        self.an_marks.configure(text=str(round(sum(all_m)/len(all_m), 1)) if all_m else "—")

        paid = sum(1 for s in self.students.values() if s.get("fees_status") == "Paid")
        self.an_fees.configure(text=f"{round(paid/total*100,1)}%" if total else "—")

        # Department table
        for r in self.dept_tree.get_children(): self.dept_tree.delete(r)
        dept_map = {}
        for roll, s in self.students.items():
            d = s["department"] or "Unknown"
            dept_map.setdefault(d, {"cnt": 0, "marks": [], "att": [], "paid": 0})
            dept_map[d]["cnt"] += 1
            dept_map[d]["marks"].extend(s.get("marks", {}).values())
            att = s.get("attendance", {})
            if att:
                dept_map[d]["att"].append(sum(1 for v in att.values() if v == "Present") / len(att) * 100)
            if s.get("fees_status") == "Paid":
                dept_map[d]["paid"] += 1

        for dept, d in dept_map.items():
            am = round(sum(d["marks"])/len(d["marks"]), 1) if d["marks"] else "—"
            aa = f"{round(sum(d['att'])/len(d['att']), 1)}%" if d["att"] else "—"
            self.dept_tree.insert("", "end", values=(dept, d["cnt"], am, aa, d["paid"]))

        # Top performers
        for r in self.top_tree.get_children(): self.top_tree.delete(r)
        scored = []
        for roll, s in self.students.items():
            m = s.get("marks", {})
            avg_m = sum(m.values()) / len(m) if m else 0
            att = s.get("attendance", {})
            att_p = sum(1 for v in att.values() if v == "Present") / len(att) * 100 if att else 0
            scored.append((roll, s["name"], s["department"], avg_m, att_p))
        scored.sort(key=lambda x: x[3], reverse=True)
        for rank, (roll, name, dept, avg_m, att_p) in enumerate(scored[:10], 1):
            self.top_tree.insert("", "end",
                                  values=(rank, name, roll, dept, round(avg_m, 1), f"{round(att_p, 1)}%"))

    # =========================
    # SETTINGS
    # =========================

    def build_settings(self):
        f = ctk.CTkFrame(self.main_area, corner_radius=0)
        self.page_header(f, "⚙️  Settings")

        # Appearance card
        ap = ctk.CTkFrame(f); ap.pack(fill="x", padx=20, pady=14)
        ctk.CTkLabel(ap, text="Appearance", font=("Arial", 15, "bold")).pack(anchor="w", padx=14, pady=(12, 4))

        row1 = ctk.CTkFrame(ap, fg_color="transparent"); row1.pack(fill="x", padx=14, pady=6)
        ctk.CTkLabel(row1, text="Theme Mode:", width=130, anchor="w").pack(side="left")
        self.theme_var = ctk.StringVar(value="Dark")
        ctk.CTkComboBox(row1, values=["Dark", "Light", "System"],
                        variable=self.theme_var, width=160,
                        command=lambda v: ctk.set_appearance_mode(v)).pack(side="left", padx=8)

        row2 = ctk.CTkFrame(ap, fg_color="transparent"); row2.pack(fill="x", padx=14, pady=6)
        ctk.CTkLabel(row2, text="UI Scale:", width=130, anchor="w").pack(side="left")
        self.scale_slider = ctk.CTkSlider(row2, from_=0.8, to=1.4, number_of_steps=6, width=200)
        self.scale_slider.set(1.0); self.scale_slider.pack(side="left", padx=8)
        ctk.CTkButton(row2, text="Apply Scale", width=110,
                      command=lambda: ctk.set_widget_scaling(self.scale_slider.get())).pack(side="left", padx=6)
        ctk.CTkButton(row2, text="Reset (1×)", width=100, fg_color="gray40",
                      command=self._reset_scale).pack(side="left", padx=4)

        ctk.CTkFrame(ap, height=1, fg_color="gray40").pack(fill="x", padx=14, pady=8)

        # Data card
        dm = ctk.CTkFrame(f); dm.pack(fill="x", padx=20, pady=6)
        ctk.CTkLabel(dm, text="Data Management", font=("Arial", 15, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
        row3 = ctk.CTkFrame(dm, fg_color="transparent"); row3.pack(fill="x", padx=14, pady=8)
        ctk.CTkButton(row3, text="🗑️  Clear All Data", width=160, fg_color="#8d1f1f", command=self._clear_data).pack(side="left", padx=5)

        # About card
        ab = ctk.CTkFrame(f); ab.pack(fill="x", padx=20, pady=6)
        ctk.CTkLabel(ab, text="About", font=("Arial", 15, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
        ctk.CTkLabel(ab,
                     text="Student Management System  v2.0\n"
                          "Built with Python 3 & CustomTkinter\n"
                          "Features: Students · Attendance · Marks · Fees · Analytics",
                     justify="left", text_color="gray").pack(anchor="w", padx=18, pady=(0, 14))

        return f

    def _reset_scale(self):
        self.scale_slider.set(1.0); ctk.set_widget_scaling(1.0)

    def _clear_data(self):
        if messagebox.askyesno("Confirm", "Delete ALL student data? This cannot be undone!"):
            self.students = {}
            messagebox.showinfo("Cleared", "All data has been cleared.")

# =========================
# RUN
# =========================

if __name__ == "__main__":
    app = StudentApp()
    app.mainloop()