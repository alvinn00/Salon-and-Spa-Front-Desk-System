import customtkinter as ctk
from tkinter import ttk, messagebox, BooleanVar, StringVar
from collections import Counter
from datetime import datetime
from database import Database

class CustomerSystem:
    def __init__(self, master):
        self.master = master
        self.selected_services = []
        self.selected_staff = None
        self.customer_name = ""
        self.customer_contact = ""

        self.create_panels()

    def create_panels(self):
        self.create_select_service_panel()
        self.create_select_staff_panel()
        self.create_enter_panel()
        self.create_confirmation_panel()

    def load_services_from_db(self):
        if hasattr(self.master, "db") and self.master.db:
            services_list = self.master.db.get_services() 
            self.master.services = {"All Services": {s["name"]: s for s in services_list}}

    def create_select_service_panel(self):
        self.load_services_from_db()  
        self.select_service_panel = ctk.CTkFrame(self.master, fg_color="#f0f0f5")
        ctk.CTkLabel(self.select_service_panel, text="Select Service", font=("Arial", 24)).pack(pady=10)

        self.service_scroll = ctk.CTkScrollableFrame(self.select_service_panel, width=750, height=400)
        self.service_scroll.pack(padx=20, pady=10, fill="both", expand=True)

        self.service_vars = {}
        row = 0
        col = 0
        for category, services in self.master.services.items():
            ctk.CTkLabel(self.service_scroll, text=category, font=("Arial", 18)).grid(row=row, column=0, columnspan=4, pady=10)
            row += 1
            col = 0
            for s_name in services.keys():
                var = BooleanVar()
                cb = ctk.CTkCheckBox(self.service_scroll, text=s_name, variable=var)
                cb.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")
                self.service_vars[s_name] = var
                col += 1
                if col > 3:
                    col = 0
                    row += 1
            row += 1

        btn_frame = ctk.CTkFrame(self.select_service_panel, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Back", command=lambda: self.master.show_panel(self.master.home_panel)).grid(row=0, column=0, padx=10)
        ctk.CTkButton(btn_frame, text="Next", command=self.go_to_staff).grid(row=0, column=1, padx=10)

    def go_to_staff(self):
        self.selected_services = [name for name, var in self.service_vars.items() if var.get()]
        if not self.selected_services:
            messagebox.showwarning("Selection Error", "Please select at least one service.")
            return
        self.master.show_panel(self.select_staff_panel)

    def create_select_staff_panel(self):
        self.select_staff_panel = ctk.CTkFrame(self.master, fg_color="#f0f0f5")
        ctk.CTkLabel(self.select_staff_panel, text="Select Staff", font=("Arial", 24)).pack(pady=10)

        self.staff_scroll = ctk.CTkScrollableFrame(self.select_staff_panel, width=750, height=400)
        self.staff_scroll.pack(padx=20, pady=10, fill="both", expand=True)

        self.staff_var = StringVar()
        row = 0
        col = 0
        for staff in self.master.staff_list:
            rb = ctk.CTkRadioButton(self.staff_scroll, text=staff, variable=self.staff_var, value=staff)
            rb.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")
            col += 1
            if col > 2:
                col = 0
                row += 1

        btn_frame = ctk.CTkFrame(self.select_staff_panel, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Back", command=lambda: self.master.show_panel(self.select_service_panel)).grid(row=0, column=0, padx=10)
        ctk.CTkButton(btn_frame, text="Next", command=self.go_to_enter).grid(row=0, column=1, padx=10)

    def go_to_enter(self):
        self.selected_staff = self.staff_var.get()
        if not self.selected_staff:
            messagebox.showwarning("Selection Error", "Please select a staff.")
            return
        self.master.show_panel(self.enter_panel)

    def create_enter_panel(self):
        self.enter_panel = ctk.CTkFrame(self.master, fg_color="#f0f0f5")
        ctk.CTkLabel(self.enter_panel, text="Enter Your Details", font=("Arial", 24)).pack(pady=20)

        self.name_entry = ctk.CTkEntry(self.enter_panel, placeholder_text="Name")
        self.name_entry.pack(pady=5)

        def only_numbers(char):
            return char.isdigit() or char == ""

        vcmd = (self.master.register(only_numbers), "%P")    
        self.contact_entry = ctk.CTkEntry(self.enter_panel, placeholder_text="Contact", validate="key", validatecommand=vcmd)
        self.contact_entry.pack(pady=5)

        btn_frame = ctk.CTkFrame(self.enter_panel, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Back", command=lambda: self.master.show_panel(self.select_staff_panel)).grid(row=0, column=0, padx=10)
        ctk.CTkButton(btn_frame, text="Next", command=self.go_to_confirmation).grid(row=0, column=1, padx=10)

    def go_to_confirmation(self):
        self.customer_name = self.name_entry.get().strip()
        self.customer_contact = self.contact_entry.get().strip()
        if not self.customer_name or not self.customer_contact:
            messagebox.showwarning("Input Error", "Please enter your name and contact.")
            return
        self.update_confirmation()
        self.master.show_panel(self.confirmation_panel)

    def create_confirmation_panel(self):
        self.confirmation_panel = ctk.CTkFrame(self.master, fg_color="#f0f0f5")
        ctk.CTkLabel(self.confirmation_panel, text="Confirm Walk-in", font=("Arial", 24)).pack(pady=10)

        self.confirm_label = ctk.CTkLabel(self.confirmation_panel, text="", font=("Arial", 16))
        self.confirm_label.pack(pady=10)

        ctk.CTkButton(self.confirmation_panel, text="Confirm", command=self.confirm_appointment).pack(pady=10)
        ctk.CTkButton(self.confirmation_panel, text="Cancel", command=lambda: self.master.show_panel(self.master.home_panel)).pack(pady=10)

    def update_confirmation(self):
        text = f"Name: {self.customer_name}\nContact: {self.customer_contact}\n"
        text += f"Services: {', '.join(self.selected_services)}\n"
        text += f"Time: Walk-in\nStaff: {self.selected_staff}"
        self.confirm_label.configure(text=text)

    def confirm_appointment(self):
        ticket = self.master.next_ticket_number()
        services_str = ", ".join(self.selected_services)
        current_time = datetime.now().strftime("%H:%M")

        self.master.waiting_list[ticket] = {
            "ticket": ticket,
            "name": self.customer_name,
            "contact": self.customer_contact,
            "services": services_str,
            "staff": self.selected_staff,
            "requested_time": current_time,
            "status": "Walk-in"
        }

        if hasattr(self.master, "db") and self.master.db:
            try:
                self.master.db.add_waiting(
                    name=self.customer_name,
                    contact=self.customer_contact,
                    services=services_str,
                    staff=self.selected_staff,
                    requested_time=current_time
                )
            except Exception as e:
                print("DB Warning:", e)

        if hasattr(self.master, "admin_system") and self.master.admin_system:
            self.master.admin_system.refresh_waiting_table()

        messagebox.showinfo("Success", f"Walk-in confirmed!\nTicket No: {ticket}")
        self.master.show_panel(self.master.home_panel)

        self.selected_services = []
        self.selected_staff = None
        self.customer_name = ""
        self.customer_contact = ""
        self.name_entry.delete(0, "end")
        self.contact_entry.delete(0, "end")
        for var in self.service_vars.values():
            var.set(False)

