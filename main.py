from database import Database
import customtkinter as ctk
from tkinter import messagebox
from customer import CustomerSystem
from admin import AdminSystem

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class SalonSystem(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pa Salon ni Kap")
        self.geometry("980x640")

        self.admins = {"bacit": "bacit"}

        self.db = Database()

        self.services = self.load_services_from_db()

        self.staff_list = ["Luffy", "Zoro", "Nami", "Usopp", "Sanji", "Chopper", "Robin", "Franky", "Brook", "Jinbe",
                           "Ace", "Sabo", "Law", "Ivankov", "Koala", "Belo Betty", "Hack", "Bartholomew Kuma",
                           "Kid", "Killer", "Capone", "Drake", "Bonney", "Jewelry Bonney", "X Drake", "Kozuki Oden",
                           "Akainu", "Kizaru", "Fujitora", "Smoker", "Tashigi", "Sengoku", "Garp", "Sentomaru",
                           "Blackbeard", "Crocodile", "Doflamingo", "Mihawk", "Hancock", "Buggy", "Perona", "Jozu",
                           "Shanks", "Whitebeard", "Big Mom", "Kaido", "Charlotte Katakuri", "Charlotte Smoothie", "King", "Queen",
                            "Carrot", "Vivi", "Rebecca", "Bartolomeo", "Foxy", "Eustass Kid", "Magellan", "Hody Jones", "Arlong"]
        self.time_options = [f"{h}:00" for h in range(8, 21)]
        self.appointments = []
        self.waiting_list = {}
        self.ticket_count = 0

        self.create_home_panel()
        self.customer_system = CustomerSystem(self)
        self.admin_system = AdminSystem(self, self)
        self.show_panel(self.home_panel)

    def show_panel(self, panel):
        for w in self.winfo_children():
            w.pack_forget()
        panel.pack(fill="both", expand=True)

    def next_ticket_number(self):
        self.ticket_count += 1
        return self.ticket_count

    def create_home_panel(self):
        self.home_panel = ctk.CTkFrame(self, fg_color="Gray")
        ctk.CTkLabel(
            self.home_panel,
            text="Pa Salon & Spa ni Kap",
            font=("Arial", 30),
            text_color="Red"
        ).pack(pady=40)

        ctk.CTkButton(
            self.home_panel,
            text="Enter",
            width=280,
            fg_color="Blue",
            hover_color="Black",
            command=lambda: self.show_panel(self.customer_system.select_service_panel)
        ).pack(pady=10)

        ctk.CTkButton(
            self.home_panel,
            text="Admin",
            width=280,
            fg_color="Blue",
            hover_color="Black",
            command=lambda: self.show_panel(self.admin_system.admin_login_panel)
        ).pack(pady=10)

        ctk.CTkButton(
            self.home_panel,
            text="About",
            width=280,
            fg_color="Blue",
            hover_color="Black",
            command=lambda: messagebox.showinfo("About Pa Salon & Spa ni Kap",
                                                "Welcome to Pa Salon & Spa ni Kap!\n\n"
                                                "Your go-to place for relaxation, beauty, and self-care.\n"
                                                "We offer rejuvenating facials, soothing massages, stylish haircuts, "
                                                "and creative nail art all personalized to make you look and feel your best.\n\n"
                                                "Visit us and experience top-notch service in a clean and welcoming environment!") ).pack(pady=10)

    def load_services_from_db(self):
        services = {}
        if self.db:
            data = self.db.get_services()  
            for item in data:
                category = "Other"
                name = item["name"]
                if "Hair" in name:
                    category = "Hair"
                elif "Facial" in name:
                    category = "Facial"
                elif "Massage" in name:
                    category = "Massage"
                elif "Wax" in name:
                    category = "Waxing"
                elif "Nail" in name or "Pedicure" in name:
                    category = "Nails"

                if category not in services:
                    services[category] = {}
                services[category][name] = item["duration"]
        return services


if __name__ == "__main__":
    app = SalonSystem()
    app.mainloop()
