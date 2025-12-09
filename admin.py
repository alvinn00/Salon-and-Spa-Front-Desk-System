import customtkinter as ctk
from tkinter import ttk, messagebox
from collections import Counter

STATUS_RULES = {
    "Pending": ["On Going", "Cancel", "No Show"],
    "On Going": ["Complete"],
    "Complete": [],
    "Cancel": [],
}


class AdminSystem:

    def __init__(self, root, master):
        self.root = root
        self.master = master
        self.current_admin = None
        self.admin_bg = "pink"
        self.selected_service_id = None

        self.create_admin_login_panel()
        self.create_admin_dashboard()
        self.create_waiting_panel()
        self.create_customers_panel()
        self.create_history_panel()
        self.create_statistics_panel()
        self.create_service_panel()

    def create_admin_login_panel(self):
        self.admin_login_panel = ctk.CTkFrame(self.root, fg_color=self.admin_bg)
        ctk.CTkLabel(self.admin_login_panel, text="Admin Login", font=("Bold", 30), text_color="black").pack(pady=20)

        form = ctk.CTkFrame(self.admin_login_panel, fg_color=self.admin_bg)
        form.pack(pady=10)

        ctk.CTkLabel(form, text="Username:", width=120, anchor="w", text_color="black").grid(row=0, column=0, pady=8)
        ctk.CTkLabel(form, text="Password:", width=120, anchor="w", text_color="black").grid(row=1, column=0, pady=8)

        self.login_user = ctk.CTkEntry(form, width=240)
        self.login_pass = ctk.CTkEntry(form, width=240, show="*")
        self.login_user.grid(row=0, column=1, pady=8)
        self.login_pass.grid(row=1, column=1, pady=8)

        btn_frame = ctk.CTkFrame(self.admin_login_panel, fg_color=self.admin_bg)
        btn_frame.pack(pady=14)

        ctk.CTkButton(btn_frame, text="Back", width=140, command=lambda: self.root.show_panel(self.root.home_panel)).grid(row=0, column=0, padx=8)
        ctk.CTkButton(btn_frame, text="Login", width=140, command=self.do_login).grid(row=0, column=1, padx=8)

    def do_login(self):
        u = self.login_user.get().strip()
        p = self.login_pass.get().strip()
        admins = getattr(self.master, "admins", {})
        if u in admins and admins[u] == p:
            self.current_admin = u
            self.root.show_panel(self.admin_main_panel)
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def create_admin_dashboard(self):
        self.admin_main_panel = ctk.CTkFrame(self.root, fg_color=self.admin_bg)
        ctk.CTkLabel(self.admin_main_panel, text="Admin Dashboard", font=("Arial", 28), text_color="black").pack(pady=16)

        nav = ctk.CTkFrame(self.admin_main_panel, fg_color=self.admin_bg)
        nav.pack(pady=10)

        ctk.CTkButton(nav, text="Waiting List", width=200, command=lambda: [self.refresh_waiting_table(), self.root.show_panel(self.waiting_panel)]).grid(row=0, column=0, padx=8, pady=8)
        ctk.CTkButton(nav, text="View Customers", width=200, command=lambda: [self.refresh_customers_table(), self.root.show_panel(self.customers_panel)]).grid(row=0, column=1, padx=8, pady=8)
        ctk.CTkButton(nav, text="Customer History", width=200, command=lambda: [self.refresh_history_table(), self.root.show_panel(self.history_panel)]).grid(row=1, column=0, padx=8, pady=8)
        ctk.CTkButton(nav, text="Service Management", width=200, command=lambda: self.root.show_panel(self.service_frame)).grid(row=2, column=0, padx=8, pady=8)
        ctk.CTkButton(nav, text="Statistics", width=200, command=lambda: [self.refresh_statistics(), self.root.show_panel(self.statistics_panel)]).grid(row=1, column=1, padx=8, pady=8)
        ctk.CTkButton(nav, text="Logout", width=200, command=lambda: self.root.show_panel(self.root.home_panel)).grid(row=2, column=1, padx=8, pady=8)

    def create_waiting_panel(self):
        self.waiting_panel = ctk.CTkFrame(self.root, fg_color=self.admin_bg)
        ctk.CTkLabel(self.waiting_panel, text="Waiting List", font=("Arial", 24), text_color="#ffffff").pack(pady=12)

        self.waiting_table = ttk.Treeview(self.waiting_panel, columns=("Ticket", "Name", "Contact", "Services", "Staff", "Time"), show="headings", selectmode="extended")
        for c in ("Ticket", "Name", "Contact", "Services", "Staff", "Time"):
            self.waiting_table.heading(c, text=c)
            self.waiting_table.column(c, width=120)
        self.waiting_table.pack(pady=12, fill="both", expand=True)

        nav = ctk.CTkFrame(self.waiting_panel, fg_color=self.admin_bg)
        nav.pack(pady=8)

        ctk.CTkButton(nav, text="Approve", width=140, command=self.approve_selected).grid(row=0, column=0, padx=6)
        ctk.CTkButton(nav, text="Remove", width=140, command=self.remove_selected).grid(row=0, column=1, padx=6)
        ctk.CTkButton(nav, text="Back", width=140, command=lambda: self.root.show_panel(self.admin_main_panel)).grid(row=0, column=2, padx=6)

    def refresh_waiting_table(self):
        self.waiting_table.delete(*self.waiting_table.get_children())
        wl = getattr(self.master, "waiting_list", {}) or {}
        for t, appt in wl.items():
            self.waiting_table.insert("", "end", values=(appt.get("ticket"), appt.get("name"), appt.get("contact"), appt.get("services"), appt.get("staff"), appt.get("requested_time")))

    def staff_is_busy(self, staff_name):
        return any(
            a.get("staff") == staff_name and a.get("status") not in ["Complete", "Cancel", "No Show"]
            for a in getattr(self.master, "appointments", [])
        )

    def approve_selected(self):
        sel = self.waiting_table.selection()
        if not sel:
            messagebox.showwarning("Select", "Select entry to approve")
            return
        db = getattr(self.master, "db", None)
        for s in sel:
            vals = self.waiting_table.item(s, "values")
            try:
                ticket = int(vals[0])
            except Exception:
                messagebox.showerror("Error", "Invalid ticket value")
                continue
            wl = getattr(self.master, "waiting_list", {})
            if ticket not in wl:
                continue
            appt = wl[ticket]
            staff = appt.get("staff")
            if self.staff_is_busy(staff):
                messagebox.showerror("Staff Busy", f"Cannot approve: Staff {staff} is still serving another customer.")
                continue
            appt_status = "Pending"
            appt_data = {
                "name": appt.get("name"),
                "contact": appt.get("contact"),
                "services": appt.get("services"),
                "staff": staff,
                "start_time": appt.get("requested_time"),
                "status": appt_status
            }
            if db:
                try:
                    new_ticket = db.add_appointment(appt_data["name"], appt_data["contact"], appt_data["services"], appt_data["staff"], appt_data["start_time"], appt_data["status"])
                    if new_ticket:
                        appt["ticket"] = new_ticket
                except Exception as e:
                    print("DB add_appointment failed:", e)
                    messagebox.showwarning("DB Warning", f"Could not save appointment to DB: {e}")
            appt["status"] = appt_status
            self.master.appointments.append(appt)
            del self.master.waiting_list[ticket]
            if db:
                try:
                    db.remove_waiting(ticket)
                except Exception:
                    pass
        self.refresh_waiting_table()
        self.refresh_customers_table()
        messagebox.showinfo("Approval", "Selected appointments processed")

    def remove_selected(self):
        sel = self.waiting_table.selection()
        if not sel:
            messagebox.showwarning("Select", "Select entry to remove")
            return
        db = getattr(self.master, "db", None)
        for s in sel:
            vals = self.waiting_table.item(s, "values")
            try:
                ticket = int(vals[0])
            except Exception:
                continue
            if ticket in getattr(self.master, "waiting_list", {}):
                del self.master.waiting_list[ticket]
            if db:
                try:
                    db.remove_waiting(ticket)
                except Exception:
                    pass
        self.refresh_waiting_table()
        messagebox.showinfo("Removed", "Selected waiting entries removed")

    def create_customers_panel(self):
        self.customers_panel = ctk.CTkFrame(self.root, fg_color=self.admin_bg)
        ctk.CTkLabel(self.customers_panel, text="Customer Appointments", font=("Arial", 24), text_color="#ffffff").pack(pady=12)
        self.customers_table = ttk.Treeview(self.customers_panel, columns=("Ticket", "Name", "Contact", "Services", "Staff", "Start", "Status"), show="headings", selectmode="browse")
        for c in ("Ticket", "Name", "Contact", "Services", "Staff", "Start", "Status"):
            self.customers_table.heading(c, text=c)
            self.customers_table.column(c, width=120)
        self.customers_table.pack(pady=12, fill="both", expand=True)
        self.customers_table.bind("<<TreeviewSelect>>", lambda e: self.on_customer_select())

        nav = ctk.CTkFrame(self.customers_panel, fg_color=self.admin_bg)
        nav.pack(pady=8)
        self.btn_on_going = ctk.CTkButton(nav, text="On Going", width=140, command=lambda: self.update_status("On Going"))
        self.btn_on_going.grid(row=0, column=0, padx=6)
        self.btn_no_show = ctk.CTkButton(nav, text="No Show", width=140, command=lambda: self.update_status("No Show"))
        self.btn_no_show.grid(row=0, column=1, padx=6)
        self.btn_cancel = ctk.CTkButton(nav, text="Cancel", width=140, command=lambda: self.update_status("Cancel"))
        self.btn_cancel.grid(row=0, column=2, padx=6)
        self.btn_complete = ctk.CTkButton(nav, text="Complete", width=140, command=lambda: self.update_status("Complete"))
        self.btn_complete.grid(row=0, column=3, padx=6)
        ctk.CTkButton(nav, text="Back", width=140, command=lambda: self.root.show_panel(self.admin_main_panel)).grid(row=0, column=4, padx=6)

        self.set_all_status_buttons_state("disabled")

    def set_all_status_buttons_state(self, state="normal"):
        self.btn_on_going.configure(state=state)
        self.btn_no_show.configure(state=state)
        self.btn_cancel.configure(state=state)
        self.btn_complete.configure(state=state)

    def on_customer_select(self):
        selected = self.customers_table.selection()
        if selected:
            self.set_all_status_buttons_state("normal")
        else:
            self.set_all_status_buttons_state("disabled")

    def update_status(self, status):
        sel = self.customers_table.selection()
        if not sel:
            return
        item = sel[0]
        vals = self.customers_table.item(item, "values")
        ticket = int(vals[0])

        appt = next((a for a in getattr(self.master, "appointments", []) if a.get("ticket") == ticket), None)
        if not appt:
            return

        current_status = appt.get("status")
        allowed = STATUS_RULES.get(current_status, [])

        if status not in allowed:
            messagebox.showerror("Invalid Status", f"Cannot change status from '{current_status}' to '{status}'.")
            return

        appt["status"] = status

        db = getattr(self.master, "db", None)
        if db:
            try:
                db.update_status(ticket, status)
            except Exception:
                pass
        self.refresh_customers_table()

    def refresh_customers_table(self):
        self.customers_table.delete(*self.customers_table.get_children())
        for appt in getattr(self.master, "appointments", []):
            self.customers_table.insert("", "end", values=(appt.get("ticket"), appt.get("name"), appt.get("contact"), appt.get("services"), appt.get("staff"), appt.get("start_time"), appt.get("status")))

    def create_history_panel(self):
        self.history_panel = ctk.CTkFrame(self.root, fg_color=self.admin_bg)
        ctk.CTkLabel(self.history_panel, text="Customer History", font=("Arial", 26), text_color="#ffffff").pack(pady=12)

        table_frame = ctk.CTkFrame(self.history_panel, fg_color=self.admin_bg)
        table_frame.pack(fill="both", expand=True)

        self.history_table = ttk.Treeview(table_frame, columns=("Ticket", "Name", "Contact", "Services", "Staff", "Start", "Status"), show="headings")
        for c in ("Ticket", "Name", "Contact", "Services", "Staff", "Start", "Status"):
            self.history_table.heading(c, text=c)
            self.history_table.column(c, width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.history_table.yview)
        self.history_table.configure(yscrollcommand=scrollbar.set)

        self.history_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ctk.CTkButton(self.history_panel, text="Back", width=180, command=lambda: self.root.show_panel(self.admin_main_panel)).pack(pady=8)

    def refresh_history_table(self):
        self.history_table.delete(*self.history_table.get_children())
        db = getattr(self.master, "db", None)
        if db:
            try:
                data = db.get_customers()
                data = sorted(data, key=lambda x: x.get("ticket", 0))
                for appt in data:
                    self.history_table.insert("", "end", values=(appt.get("ticket"), appt.get("name"), appt.get("contact"), appt.get("services"), appt.get("staff"), appt.get("start_time"), appt.get("status")))
            except Exception:
                pass

    def create_statistics_panel(self):
        self.statistics_panel = ctk.CTkFrame(self.root, fg_color=self.admin_bg)
        ctk.CTkLabel(self.statistics_panel, text="Salon Statistics", font=("Arial", 26), text_color="#ffffff").pack(pady=12)
        self.stats_label = ctk.CTkLabel(self.statistics_panel, text="", font=("Arial", 18))
        self.stats_label.pack(pady=20)
        ctk.CTkButton(self.statistics_panel, text="Back", width=200, command=lambda: self.root.show_panel(self.admin_main_panel)).pack(pady=8)

    def refresh_statistics(self):
        db = getattr(self.master, "db", None)
        if not db:
            self.stats_label.configure(text="Database not connected")
            return

        try:
            customers = db.get_customers()
        except Exception as e:
            self.stats_label.configure(text=f"Error loading customers: {e}")
            return

        staff_list = []
        service_list = []
        total_customers = 0

        for appt in customers:
            staff = appt.get("staff")
            sv = appt.get("services")
            status = appt.get("status")

            if staff:
                staff_list.append(staff)
            if sv:
                service_list.append(sv)
            if status == "Complete":
                total_customers += 1

        most_staff = Counter(staff_list).most_common(1)
        most_service = Counter(service_list).most_common(1)

        staff_text = most_staff[0][0] if most_staff else "None"
        service_text = most_service[0][0] if most_service else "None"

        result = f"Most Famous Staff: {staff_text}\n Most Famous Service: {service_text}\n Total Customers Served: {total_customers}"
        self.stats_label.configure(text=result)

        try:
            db.clear_statistics()
            staff_counts = Counter(staff_list)
            for staff_name, count in staff_counts.items():
                db.add_statistics(staff=staff_name, service=None, count=count)
            service_counts = Counter(service_list)
            for service_name, count in service_counts.items():
                db.add_statistics(staff=None, service=service_name, count=count)
        except Exception as e:
            print("Error updating statistics table:", e)

    def create_service_panel(self):
        self.service_frame = ctk.CTkFrame(self.root, fg_color=self.admin_bg)
        ctk.CTkLabel(self.service_frame, text="Service List Management", font=("Arial", 22, "bold"), text_color="#ffffff").pack(pady=12)

        form = ctk.CTkFrame(self.service_frame)
        form.pack(pady=10)

        self.sv_name = ctk.CTkEntry(form, placeholder_text="Service Name", width=200)
        self.sv_duration = ctk.CTkEntry(form, placeholder_text="Duration (minutes)", width=180)
        self.sv_name.grid(row=0, column=0, padx=5, pady=5)
        self.sv_duration.grid(row=0, column=1, padx=5, pady=5)

        btnf = ctk.CTkFrame(self.service_frame)
        btnf.pack(pady=10)
        ctk.CTkButton(btnf, text="Add Service", command=self.add_service).grid(row=0, column=0, padx=6)
        ctk.CTkButton(btnf, text="Update Service", command=self.update_service).grid(row=0, column=1, padx=6)
        ctk.CTkButton(btnf, text="Delete Service", command=self.delete_service).grid(row=0, column=2, padx=6)

        self.service_table = ttk.Treeview(self.service_frame, columns=("id", "name", "duration"), show="headings", height=12)
        self.service_table.heading("id", text="ID")
        self.service_table.heading("name", text="Service Name")
        self.service_table.heading("duration", text="Duration (mins)")
        self.service_table.column("id", width=60)
        self.service_table.column("name", width=180)
        self.service_table.column("duration", width=120)
        self.service_table.pack(fill="both", expand=True, pady=10)
        self.service_table.bind("<<TreeviewSelect>>", self.on_service_select)

        self.load_services()

        ctk.CTkButton(self.service_frame, text="Back", width=180, command=lambda: self.root.show_panel(self.admin_main_panel)).pack(pady=8)

    def load_services(self):
        for i in self.service_table.get_children():
            self.service_table.delete(i)
        services = getattr(self.master, "db", None) and self.master.db.get_services() or []
        for s in services:
            self.service_table.insert("", "end", values=(s["id"], s["name"], s["duration"]))

    def add_service(self):
        name = self.sv_name.get()
        duration = self.sv_duration.get()
        if not (name and duration):
            messagebox.showwarning("Missing Data", "Service name & duration are required.")
            return
        self.master.db.add_service(name, duration)
        messagebox.showinfo("Success", "Service added.")
        self.load_services()

    def on_service_select(self, event=None):
        try:
            data = self.service_table.item(self.service_table.selection()[0], "values")
            self.selected_service_id = data[0]
            self.sv_name.delete(0, "end")
            self.sv_duration.delete(0, "end")
            self.sv_name.insert(0, data[1])
            self.sv_duration.insert(0, data[2])
        except:
            pass

    def update_service(self):
        if not self.selected_service_id:
            messagebox.showwarning("Error", "Select a service first.")
            return
        name = self.sv_name.get()
        duration = self.sv_duration.get()
        self.master.db.update_service(self.selected_service_id, name, duration)
        messagebox.showinfo("Updated", "Service updated.")
        self.load_services()

    def delete_service(self):
        if not self.selected_service_id:
            messagebox.showwarning("Error", "Select a service first.")
            return
        if messagebox.askyesno("Confirm", "Delete this service?"):
            self.master.db.delete_service(self.selected_service_id)
            self.load_services()
