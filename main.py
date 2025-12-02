import customtkinter as ctk
from tkinter import ttk, messagebox

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

from customer import CustomerSystem
from admin import AdminSystem

class SalonSystem(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pa Salon ni Kap")
        self.geometry("980x640")

        self.admins = {"bacit": "bacit"}
        self.services = {
            "Haircut": 1,
            "Hair Color": 2,
            "Manicure": 1,
            "Pedicure": 1,
            "Massage": 2,
            "Facial": 1
        }
        self.staff_list = ["luffy", "zoro", "nami", "brook"]
        self.time_options = [f"{h}:00" for h in range(8, 21)]
        self.appointments = [] 
        self.waiting_list = {}   
        self.ticket_count = 0

        self.create_home_panel()
        self.customer_system = CustomerSystem(self)
        self.admin_system = AdminSystem(self)

        self.show_panel(self.home_panel)

    def show_panel(self, panel):
        for w in self.winfo_children():
            w.pack_forget()
        panel.pack(fill="both", expand=True)

    def next_ticket_number(self):
        self.ticket_count += 1
        return self.ticket_count

    def create_home_panel(self):
        self.home_panel = ctk.CTkFrame(self, fg_color="white")
        ctk.CTkLabel(self.home_panel, text="Pa Salon & Spa ni Kap", font=("Arial", 30), text_color="#ff69b4").pack(pady=40)

        ctk.CTkButton(self.home_panel, text="Book Appointment", width=280,
                       fg_color="#ffb6c1", hover_color="#ff69b4",
                       command=lambda: self.show_panel(self.customer_system.enter_panel)).pack(pady=10)

        ctk.CTkButton(self.home_panel, text="Admin Login", width=280,
                       fg_color="#ffb6c1", hover_color="#ff69b4",
                       command=lambda: self.show_panel(self.admin_system.admin_login_panel)).pack(pady=10)

        ctk.CTkButton(self.home_panel, text="About", width=280,
                       fg_color="#ffb6c1", hover_color="#ff69b4",
                       command=lambda: messagebox.showinfo("About", "Salon & Spa System - Demo")).pack(pady=10)


if __name__ == "__main__":
    app = SalonSystem()
    app.mainloop()
