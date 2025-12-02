import customtkinter as ctk
from tkinter import ttk, messagebox

class AdminSystem:
    def __init__(self, root):
        self.root = root
        self.current_admin = None
        self.create_admin_login_panel()
        self.create_admin_dashboard()
        self.create_waiting_panel()
        self.create_customers_panel()

    def create_admin_login_panel(self):
        self.admin_login_panel = ctk.CTkFrame(self.root)
        ctk.CTkLabel(self.admin_login_panel,text="Admin Login",font=("Arial",26)).pack(pady=20)

        form = ctk.CTkFrame(self.admin_login_panel)
        form.pack(pady=10)
        ctk.CTkLabel(form,text="Username:",width=120,anchor="w").grid(row=0,column=0,pady=8)
        ctk.CTkLabel(form,text="Password:",width=120,anchor="w").grid(row=1,column=0,pady=8)

        self.login_user = ctk.CTkEntry(form,width=240)
        self.login_pass = ctk.CTkEntry(form,width=240,show="*")
        self.login_user.grid(row=0,column=1,pady=8)
        self.login_pass.grid(row=1,column=1,pady=8)

        btn_frame = ctk.CTkFrame(self.admin_login_panel)
        btn_frame.pack(pady=14)
        ctk.CTkButton(btn_frame,text="Back",width=140,command=lambda:self.root.show_panel(self.root.home_panel)).grid(row=0,column=0,padx=8)
        ctk.CTkButton(btn_frame,text="Login",width=140,command=self.do_login).grid(row=0,column=1,padx=8)

    def do_login(self):
        u = self.login_user.get().strip()
        p = self.login_pass.get().strip()
        if u in self.root.admins and self.root.admins[u]==p:
            self.current_admin = u
            self.root.show_panel(self.admin_main_panel)
        else:
            messagebox.showerror("Error","Invalid credentials")

    def create_admin_dashboard(self):
        self.admin_main_panel = ctk.CTkFrame(self.root)
        ctk.CTkLabel(self.admin_main_panel,text="Admin Dashboard",font=("Arial",28)).pack(pady=16)
        nav = ctk.CTkFrame(self.admin_main_panel)
        nav.pack(pady=10)

        ctk.CTkButton(nav,text="Waiting List",width=200,command=lambda:[self.refresh_waiting_table(),self.root.show_panel(self.waiting_panel)]).grid(row=0,column=0,padx=8,pady=8)
        ctk.CTkButton(nav,text="View Customers",width=200,command=lambda:[self.refresh_customers_table(),self.root.show_panel(self.customers_panel)]).grid(row=0,column=1,padx=8,pady=8)
        ctk.CTkButton(nav,text="Logout",width=200,command=lambda:self.root.show_panel(self.root.home_panel)).grid(row=1,column=0,padx=8,pady=8)

    def create_waiting_panel(self):
        self.waiting_panel = ctk.CTkFrame(self.root)
        ctk.CTkLabel(self.waiting_panel,text="Waiting List",font=("Arial",24)).pack(pady=12)
        self.waiting_table = ttk.Treeview(self.waiting_panel, columns=("Ticket","Name","Contact","Services","Staff","Time"), show="headings")
        for c in ("Ticket","Name","Contact","Services","Staff","Time"):
            self.waiting_table.heading(c,text=c)
        self.waiting_table.pack(pady=12)

        nav = ctk.CTkFrame(self.waiting_panel)
        nav.pack(pady=8)
        ctk.CTkButton(nav,text="Approve",width=140,command=self.approve_selected).grid(row=0,column=0,padx=6)
        ctk.CTkButton(nav,text="Remove",width=140,command=self.remove_selected).grid(row=0,column=1,padx=6)
        ctk.CTkButton(nav,text="Back",width=140,command=lambda:self.root.show_panel(self.admin_main_panel)).grid(row=0,column=2,padx=6)

    def refresh_waiting_table(self):
        self.waiting_table.delete(*self.waiting_table.get_children())
        for ticket, appt in self.root.waiting_list.items():
            self.waiting_table.insert("", "end", values=(appt["ticket"], appt["name"], appt["contact"], appt["services"], appt["staff"], appt["requested_time"]))

    def approve_selected(self):
        sel = self.waiting_table.selection()
        if not sel:
            messagebox.showwarning("Select","Select entry to approve")
            return
        for s in sel:
            vals = self.waiting_table.item(s,"values")
            entry = {
                "ticket": vals[0],
                "name": vals[1],
                "contact": vals[2],
                "services": vals[3],
                "staff": vals[4],
                "start": vals[5],
                "status": "On Going"
            }
            self.root.appointments.append(entry)

            if int(vals[0]) in self.root.waiting_list:
                del self.root.waiting_list[int(vals[0])]
        messagebox.showinfo("Approved","Selected appointments approved")
        self.refresh_waiting_table()
        self.refresh_customers_table()

    def remove_selected(self):
        sel = self.waiting_table.selection()
        if not sel:
            messagebox.showwarning("Select","Select entry to remove")
            return
        for s in sel:
            vals = self.waiting_table.item(s,"values")
            if int(vals[0]) in self.root.waiting_list:
                del self.root.waiting_list[int(vals[0])]
        self.refresh_waiting_table()

    def create_customers_panel(self):
        self.customers_panel = ctk.CTkFrame(self.root)
        ctk.CTkLabel(self.customers_panel,text="Customer Appointments",font=("Arial",24)).pack(pady=12)
        self.customers_table = ttk.Treeview(self.customers_panel, columns=("Ticket","Name","Contact","Services","Staff","Start","Status"), show="headings")
        for c in ("Ticket","Name","Contact","Services","Staff","Start","Status"):
            self.customers_table.heading(c,text=c)
        self.customers_table.pack(pady=12)

        nav = ctk.CTkFrame(self.customers_panel)
        nav.pack(pady=8)
        ctk.CTkButton(nav,text="No Show",width=140,command=lambda:self.update_status("No Show")).grid(row=0,column=0,padx=6)
        ctk.CTkButton(nav,text="Cancel",width=140,command=lambda:self.update_status("Cancel")).grid(row=0,column=1,padx=6)
        ctk.CTkButton(nav,text="Complete",width=140,command=lambda:self.update_status("Complete")).grid(row=0,column=2,padx=6)
        ctk.CTkButton(nav,text="Back",width=140,command=lambda:self.root.show_panel(self.admin_main_panel)).grid(row=0,column=3,padx=6)

    def refresh_customers_table(self):
        self.customers_table.delete(*self.customers_table.get_children())
        for appt in self.root.appointments:
            self.customers_table.insert("", "end", values=(appt["ticket"], appt["name"], appt["contact"], appt["services"], appt["staff"], appt["start"], appt["status"]))

    def update_status(self, status):
        sel = self.customers_table.selection()
        if not sel:
            messagebox.showwarning("Select","Select appointment to update")
            return
        for s in sel:
            vals = self.customers_table.item(s,"values")
            for appt in self.root.appointments:
                if appt["ticket"]==vals[0]:
                    appt["status"]=status
        self.refresh_customers_table()
