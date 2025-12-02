import customtkinter as ctk
from tkinter import ttk, messagebox

class CustomerSystem:
    def __init__(self, root):
        self.root = root
        self.selected_services = []
        self.selected_staff = None
        self.selected_time = None

        self.entry_name = None
        self.entry_contact = None
        self.service_buttons = {}
        self.staff_buttons = {}

        self.panel_enter_info()
        self.panel_select_service()
        self.panel_select_time()
        self.panel_select_staff()
        self.panel_ticket()

    def panel_enter_info(self):
        self.enter_panel = ctk.CTkFrame(self.root, fg_color="white")
        ctk.CTkLabel(self.enter_panel, text="Enter Your Information", font=("Arial",20), text_color="#ff69b4").pack(pady=12)

        form = ctk.CTkFrame(self.enter_panel, fg_color="white")
        form.pack(pady=10)
        ctk.CTkLabel(form, text="Full Name:", width=120, anchor="w").grid(row=0,column=0,pady=8)
        ctk.CTkLabel(form, text="Contact Number:", width=120, anchor="w").grid(row=1,column=0,pady=8)

        self.entry_name = ctk.CTkEntry(form, width=320)
        self.entry_contact = ctk.CTkEntry(form, width=320)
        self.entry_name.grid(row=0,column=1,pady=8)
        self.entry_contact.grid(row=1,column=1,pady=8)

        nav = ctk.CTkFrame(self.enter_panel, fg_color="white")
        nav.pack(pady=16)
        ctk.CTkButton(nav, text="BACK", width=140, fg_color="#ffb6c1", hover_color="#ff69b4",
                      command=lambda:self.root.show_panel(self.root.home_panel)).grid(row=0,column=0,padx=8)
        ctk.CTkButton(nav, text="NEXT", width=140, fg_color="#ffb6c1", hover_color="#ff69b4",
                      command=self.go_to_service).grid(row=0,column=1,padx=8)

    def go_to_service(self):
        name = self.entry_name.get().strip()
        contact = self.entry_contact.get().strip()
        if name == "" or not contact.isdigit():
            messagebox.showerror("Error","Valid name and numeric contact required")
            return
        self.customer_name = name
        self.customer_contact = contact
        self.root.show_panel(self.service_panel)

    def panel_select_service(self):
        self.service_panel = ctk.CTkFrame(self.root, fg_color="white")
        ctk.CTkLabel(self.service_panel, text="Select Services (Max 4)", font=("Arial",20), text_color="#ff69b4").pack(pady=10)
        self.service_info_label = ctk.CTkLabel(self.service_panel, text="Selected: 0/4", font=("Arial",14), text_color="#ff69b4")
        self.service_info_label.pack(pady=6)

        grid = ctk.CTkFrame(self.service_panel, fg_color="white")
        grid.pack(pady=8)

        row = 0
        col = 0
        for service, duration in self.root.services.items():
            btn = ctk.CTkButton(grid, text=f"{service} ({duration}h)", width=200, height=50,
                                fg_color="#ffb6c1", hover_color="#ff69b4",
                                command=lambda s=service:self.toggle_service(s))
            btn.grid(row=row,column=col,padx=8,pady=8)
            self.service_buttons[service] = btn
            col += 1
            if col>=2:
                col=0
                row+=1

        nav = ctk.CTkFrame(self.service_panel, fg_color="white")
        nav.pack(pady=14)
        ctk.CTkButton(nav, text="BACK", width=140, fg_color="#ffb6c1", hover_color="#ff69b4",
                      command=lambda:self.root.show_panel(self.enter_panel)).grid(row=0,column=0,padx=8)
        ctk.CTkButton(nav, text="NEXT", width=140, fg_color="#ffb6c1", hover_color="#ff69b4",
                      command=lambda:self.root.show_panel(self.time_panel)).grid(row=0,column=1,padx=8)

    def toggle_service(self, s):
        if s in self.selected_services:
            self.selected_services.remove(s)
            self.service_buttons[s].configure(fg_color="#ffb6c1")
        else:
            if len(self.selected_services)>=4:
                messagebox.showwarning("Limit Reached","You can select up to 4 services only.")
                return
            self.selected_services.append(s)
            self.service_buttons[s].configure(fg_color="#ff69b4")
        self.service_info_label.configure(text=f"Selected: {len(self.selected_services)}/4")

    def panel_select_time(self):
        self.time_panel = ctk.CTkFrame(self.root, fg_color="white")
        ctk.CTkLabel(self.time_panel, text="Select Start Time", font=("Arial",20), text_color="#ff69b4").pack(pady=14)

        self.time_frame = ctk.CTkFrame(self.time_panel, fg_color="white")
        self.time_frame.pack(pady=12)

        row = 0
        col = 0
        for t in self.root.time_options:
            btn = ctk.CTkButton(self.time_frame, text=t, width=100,
                                fg_color="#ffb6c1", hover_color="#ff69b4",
                                command=lambda tt=t:self.select_time(tt))
            btn.grid(row=row,column=col,padx=4,pady=4)
            col += 1
            if col>=6:
                col=0
                row+=1

        nav = ctk.CTkFrame(self.time_panel, fg_color="white")
        nav.pack(pady=14)
        ctk.CTkButton(nav,text="BACK",width=140,fg_color="#ffb6c1",hover_color="#ff69b4",
                      command=lambda:self.root.show_panel(self.service_panel)).grid(row=0,column=0,padx=8)
        ctk.CTkButton(nav,text="NEXT",width=140,fg_color="#ffb6c1",hover_color="#ff69b4",
                      command=lambda:self.root.show_panel(self.staff_panel)).grid(row=0,column=1,padx=8)

    def select_time(self, t):
        self.selected_time = t
        self.update_staff_availability()

    def panel_select_staff(self):
        self.staff_panel = ctk.CTkFrame(self.root, fg_color="white")
        ctk.CTkLabel(self.staff_panel, text="Select Staff", font=("Arial",20), text_color="#ff69b4").pack(pady=14)

        self.staff_frame = ctk.CTkFrame(self.staff_panel, fg_color="white")
        self.staff_frame.pack(pady=12)

        self.staff_buttons = {}
        self.update_staff_availability()

        nav = ctk.CTkFrame(self.staff_panel, fg_color="white")
        nav.pack(pady=14)
        ctk.CTkButton(nav,text="BACK",width=140,fg_color="#ffb6c1",hover_color="#ff69b4",
                      command=lambda:self.root.show_panel(self.time_panel)).grid(row=0,column=0,padx=8)
        ctk.CTkButton(nav,text="NEXT",width=140,fg_color="#ffb6c1",hover_color="#ff69b4",
                      command=self.finish_ticket).grid(row=0,column=1,padx=8)

    def update_staff_availability(self):
        for w in self.staff_frame.winfo_children():
            w.destroy()
        row=0
        col=0
        for staff in self.root.staff_list:

            booked = any(appt["staff"]==staff and appt["start"]==self.selected_time for appt in self.root.appointments)
            btn = ctk.CTkButton(self.staff_frame, text=staff, width=140,
                                 fg_color="#ffb6c1" if not booked else "#d3d3d3",
                                 hover_color="#ff69b4" if not booked else "#d3d3d3",
                                 state="normal" if not booked else "disabled",
                                 command=lambda s=staff:self.select_staff(s))
            btn.grid(row=row,column=col,padx=8,pady=8)
            self.staff_buttons[staff] = btn
            col+=1
            if col>=3:
                col=0
                row+=1

    def select_staff(self, staff_name):
        self.selected_staff = staff_name
        for s,btn in self.staff_buttons.items():
            btn.configure(fg_color="#ffb6c1")
        self.staff_buttons[staff_name].configure(fg_color="#ff69b4")

    def panel_ticket(self):
        self.ticket_panel = ctk.CTkFrame(self.root, fg_color="white")
        ctk.CTkLabel(self.ticket_panel, text="Appointment Ticket (Pending Approval)", font=("Arial",20), text_color="#ff69b4").pack(pady=14)

        self.ticket_label = ctk.CTkLabel(self.ticket_panel,text="",font=("Arial",14),justify="left",text_color="#ff69b4")
        self.ticket_label.pack(pady=8)

        nav = ctk.CTkFrame(self.ticket_panel, fg_color="white")
        nav.pack(pady=12)
        ctk.CTkButton(nav,text="BACK",width=140,fg_color="#ffb6c1",hover_color="#ff69b4",
                      command=lambda:self.root.show_panel(self.staff_panel)).grid(row=0,column=0,padx=8)
        ctk.CTkButton(nav,text="FINISH (Send to Waiting List)",width=240,fg_color="#ffb6c1",hover_color="#ff69b4",
                      command=self.send_to_waiting).grid(row=0,column=1,padx=8)

    def finish_ticket(self):
        if not self.selected_services or not self.selected_staff:
            messagebox.showerror("Error","Select at least one service and staff")
            return
        services_str = ", ".join(self.selected_services)
        ticket_preview = f"Name: {self.customer_name}\nContact: {self.customer_contact}\nServices: {services_str}\nStaff: {self.selected_staff}\nStart: {self.selected_time}\n\nNote: Will go to waiting list."
        self.ticket_label.configure(text=ticket_preview)
        self.root.show_panel(self.ticket_panel)

    def send_to_waiting(self):
        ticket = self.root.next_ticket_number()
        entry = {
            "ticket": ticket,
            "name": self.customer_name,
            "contact": self.customer_contact,
            "services": ", ".join(self.selected_services),
            "staff": self.selected_staff,
            "requested_time": self.selected_time
        }

        existing = [k for k,v in self.root.waiting_list.items() if v["name"]==self.customer_name]
        for k in existing:
            del self.root.waiting_list[k]

        self.root.waiting_list[ticket] = entry
        messagebox.showinfo("Submitted", f"Ticket #{ticket} added to waiting list")

        self.selected_services.clear()
        self.selected_staff=None
        self.selected_time=None
        for b in self.service_buttons.values():
            b.configure(fg_color="#ffb6c1")
        self.entry_name.delete(0,"end")
        self.entry_contact.delete(0,"end")
        self.root.show_panel(self.root.home_panel)
