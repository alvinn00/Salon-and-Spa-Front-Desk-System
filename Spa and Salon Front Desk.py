
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import simpledialog
from datetime import datetime, timedelta
from datetime import datetime
import datetime
import datetime as dt
import mysql.connector
from mysql.connector import Error
import hashlib
import os


users = {}
staff_schedules = {}
reservations = []
customer_balance = {}

def create_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="salon"
        )
        return conn
    except Error as e:
        print("Database connection failed:", e)
        return None

def get_users_from_db():
    try:
        conn = create_connection()
        if not conn:
            return {}

        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT username, password, role, category, specialty FROM users")
        result = cursor.fetchall()
        conn.close()

        users_dict = {}
        for row in result:
            users_dict[row["username"]] = {
                "password": row["password"],
                "role": row["role"],
                "category": row.get("category"),
                "specialty": row.get("specialty")
            }
        return users_dict

    except Error as e:
        print("Error loading users:", e)
        return {}



def insert_reservation_to_db(customer, staff, service, date, time, duration,
                             status="Pending", payment_method="Cash"):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        date_str = date.strftime("%Y-%m-%d")
        time_str = time.strftime("%H:%M:%S")

        sql = """
        INSERT INTO reservations
        (customer_name, staff_name, service_name, date, time, duration_minutes, payment_method, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (customer, staff, service, date_str, time_str, duration, payment_method, status))
        conn.commit()
        new_id = cursor.lastrowid  
        conn.close()

        reservations.append({
            "id": new_id,
            "customer": customer,
            "staff": staff,
            "service": service,
            "date": date,
            "time": time,
            "duration": duration,
            "status": status,
            "payment_method": payment_method,
            "rating": None,
            "comment": ""
        })

        return True
    except Exception as e:
        print("Error inserting reservation:", e)
        return False



def get_staff_schedules_from_db():
    try:
        conn = create_connection()
        if not conn:
            return {}

        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT staff_name, work_date, start_time, end_time FROM staff_schedules")
        result = cursor.fetchall()
        conn.close()

        schedules = {}
        for row in result:
            staff = row["staff_name"]  
            if staff not in schedules:
                schedules[staff] = []
            schedules[staff].append({
                "date": row["work_date"],
                "start": row["start_time"],
                "end": row["end_time"]
            })
        return schedules

    except Error as e:
        print("Error loading schedules:", e)
        return {}


def update_reservation_status_db(reservation_id, new_status):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = "UPDATE reservations SET status = %s WHERE id = %s"
        cursor.execute(sql, (new_status, reservation_id))
        conn.commit()
        conn.close()
        print(f"Reservation {reservation_id} status updated to {new_status}")
    except Exception as e:
        print("Error updating reservation:", e)


def create_user(username, password, role="Customer", name=None, category=None, specialty=None, email=None, phone=None):
    try:
        conn = create_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        
        sql = """
        INSERT INTO users (username, password, role, name, category, specialty, email, phone)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (username, password, role, name, category, specialty, email, phone))
        conn.commit()
        conn.close()

        users[username] = {"password": password, "role": role}

        print(f"User '{username}' created successfully!")
        return True

    except mysql.connector.IntegrityError:
        print("Error: Username already exists.")
        return False
    except Error as e:
        print("Error inserting user:", e)
        return False

def create_customers(username, password, name=None, email=None, phone=None):
    try:
        conn = create_connection()
        if not conn:
            print("Cannot connect to DB!")
            return False

        cursor = conn.cursor()

        sql = """
        INSERT INTO users (username, password, role, name, email, phone)
        VALUES (%s, %s, 'Customer', %s, %s, %s)
        """

        cursor.execute(sql, (username, password, name, email, phone))
        conn.commit()

        print("Customer created successfully:", username)
        conn.close()
        return True

    except mysql.connector.IntegrityError as e:
        print("Username already exists:", e)
        return False
    except Error as e:
        print("Database error:", e)
        return False


def register():
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    name = entry_name.get().strip()
    email = entry_email.get().strip()
    phone = entry_phone.get().strip()

    if not username or not password:
        messagebox.showerror("Error", "Username and password are required!")
        return

    if create_customers(username, password, name, email, phone):
        messagebox.showinfo("Success", "Customer registered successfully!")
    else:
        messagebox.showerror("Error", "Failed to register customer.")


def assign_staff_specialty(staff_username, category):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        if category in services:
            for svc_name, svc_info in services[category].items():
                sql = """
                INSERT INTO staff_specialties (staff_id, category, service_name, price, description, duration_minutes)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    staff_username,
                    category,
                    svc_name,
                    svc_info["price"],
                    svc_info["description"],
                    svc_info["duration"]
                ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Error assigning staff specialty:", e)
        return False


def get_staff_for_service(category, service_name):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        sql = """
        SELECT staff_id FROM staff_specialties
        WHERE category = %s AND service_name = %s
        """
        cursor.execute(sql, (category, service_name))
        result = cursor.fetchall()

        conn.close()

        return [row[0] for row in result]

    except Exception as e:
        print("Error fetching staff specialties:", e)
        return []

def get_staff_services_from_db(staff_username):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
        SELECT category, service_name, price, duration_minutes
        FROM staff_specialties
        WHERE staff_id = %s
        """
        cursor.execute(sql, (staff_username,))
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        print("Error fetching staff services:", e)
        return []


def update_staff_and_price(event):
    selected_service = service_box.get()
    if not selected_service:
        staff_box['values'] = []
        staff_box.set('')
        price_label.config(text="₱0")
        return

    parts = selected_service.split(" - ")
    svc_category = parts[0]
    svc_name_only = parts[1]
    price = parts[2] if len(parts) >= 3 else "₱0"
    price_label.config(text=price)

    available_staff = []
    for u, d in users.items():
        if d.get("role") == "Staff":
            
            staff_specialties = d.get("specialty") or ""
            staff_specialties_list = [s.strip() for s in staff_specialties.split(",")] if staff_specialties else []

            if d.get("category") == svc_category or svc_name_only in staff_specialties_list:
                available_staff.append(u)

    staff_box['values'] = available_staff
    staff_box.set('')
    if available_staff:
        staff_box.current(0)  

def update_reservation_status(new_status, is_completion=False):
    sel = listbox.curselection()
    if not sel:
        messagebox.showwarning("Select", "Please select a reservation first.")
        return

    idx_in_own = sel[0]
    true_index = own_indices[idx_in_own]   
    res = reservations[true_index]         

    res["status"] = new_status
    if is_completion:
        res["completion_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    res_id = res.get("id")
    if not res_id:
        messagebox.showerror("Error", "Reservation ID not found!")
        return

    update_reservation_status_db(res_id, new_status)

    messagebox.showinfo("Updated", f"Reservation marked as {new_status}!")
    update_win.destroy()
    open_update_gui()


def update_reservation_status_db(reservation_id, new_status):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = "UPDATE reservations SET status = %s WHERE id = %s"
        cursor.execute(sql, (new_status, reservation_id))
        conn.commit()
        conn.close()
        print(f"Reservation {reservation_id} status updated to {new_status}")
    except Exception as e:
        print("Error updating reservation:", e)

def get_reservations_from_db():
    try:
        conn = create_connection()
        if not conn:
            return []

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, customer_name, staff_name, service_name, date, time, duration_minutes,
                   status, payment_method, rating, comment
            FROM reservations
        """)
        result = cursor.fetchall()
        conn.close()

        reservations_list = []
        for row in result:
            time_val = row["time"]
            if isinstance(time_val, datetime.timedelta):
                time_val = (datetime.datetime.min + time_val).time()

            reservations_list.append({
                "id": row["id"],
                "customer": row["customer_name"],
                "staff": row["staff_name"],
                "service": row["service_name"],
                "date": row["date"],
                "time": time_val,
                "duration": row["duration_minutes"],
                "status": row["status"],
                "payment_method": row["payment_method"],
                "rating": row["rating"],     
                "comment": row["comment"]    
            })

        return reservations_list
    except Exception as e:
        print("Error loading reservations:", e)
        return []


def update_reservation_rating_db(res_id, rating, comment):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = """
        UPDATE reservations
        SET rating = %s, comment = %s
        WHERE id = %s
        """
        cursor.execute(sql, (rating, comment, res_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Error updating rating:", e)
        return False


def load_data_from_db():
    global users, staff_schedules, reservations

    users.update(get_users_from_db())
    staff_schedules.update(get_staff_schedules_from_db())
    reservations.clear()
    reservations.extend(get_reservations_from_db())

    print("Data loaded from DB successfully.")
    print(f"Users: {list(users.keys())}")
    print(f"Staff schedules: {staff_schedules}")
    print(f"Reservations: {reservations}")

if __name__ == "__main__":
    load_data_from_db()



services = {
    "Hair & Scalp Care": {
        "Haircut": {"price": 250, "description": "Professional haircut for both men and women.", "duration": 60, "gender": "B"},
        "Hair Wash & Blow Dry": {"price": 200, "description": "Hair wash followed by blow drying.", "duration": 60, "gender": "B"},
        "Hair Styling (Curls, Straight, Updo)": {"price": 500, "description": "Special styling for occasions.", "duration": 60, "gender": "F"},
        "Hair Coloring (Full, Highlights, Balayage, Ombre)": {"price": 1200, "description": "Hair coloring and highlights.", "duration": 60, "gender": "B"},
        "Hair Rebonding / Relaxing": {"price": 1500, "description": "Straightening treatment for hair.", "duration": 60, "gender": "F"},
        "Keratin Treatment / Brazilian Blowout": {"price": 1800, "description": "Smoothens hair and reduces frizz.", "duration": 60, "gender": "B"},
        "Hot Oil / Hair Spa Treatment": {"price": 650, "description": "Deep conditioning for healthy hair.", "duration": 60, "gender": "B"},
        "Scalp Treatment (Anti-Dandruff, Hair Fall Control)": {"price": 500, "description": "Scalp care treatment.", "duration": 60, "gender": "B"},
        "Deep Conditioning Mask": {"price": 450, "description": "Repairs and nourishes hair.", "duration": 60, "gender": "B"}
    },

    "Facial & Skin Care": {
        "Basic Facial Cleaning": {"price": 400, "description": "Cleanses skin and removes impurities.", "duration": 60, "gender": "B"},
        "Deep Cleansing Facial": {"price": 600, "description": "Deep pore cleansing for refreshed skin.", "duration": 60, "gender": "B"},
        "Whitening Facial": {"price": 750, "description": "Brightens and evens skin tone.", "duration": 60, "gender": "F"},
        "Anti-Aging / Rejuvenating Facial": {"price": 800, "description": "Reduces fine lines and rejuvenates skin.", "duration": 60, "gender": "F"},
        "Acne Treatment Facial": {"price": 700, "description": "Cleanses and treats acne-prone skin.", "duration": 60, "gender": "B"},
        "Hydrating Facial": {"price": 650, "description": "Moisturizes and nourishes skin.", "duration": 60, "gender": "B"},
        "Diamond Peel / Microdermabrasion": {"price": 800, "description": "Exfoliation for smooth skin.", "duration": 60, "gender": "B"},
        "Oxygen Facial": {"price": 750, "description": "Skin hydration and glow using oxygen therapy.", "duration": 60, "gender": "B"},
        "Collagen Facial": {"price": 850, "description": "Boosts skin elasticity and firmness.", "duration": 60, "gender": "F"},
        "LED Light Therapy Facial": {"price": 700, "description": "Treats acne, wrinkles, and skin pigmentation.", "duration": 60, "gender": "B"}
    },

    "Eye & Brow Care": {
        "Eyebrow Shaping (Wax / Thread)": {"price": 250, "description": "Clean and defined eyebrows.", "duration": 60, "gender": "B"},
        "Eyebrow Tinting / Henna Brow": {"price": 300, "description": "Tints and enhances eyebrow color.", "duration": 60, "gender": "F"},
        "Eyelash Extension / Lift": {"price": 500, "description": "Enhances lashes for a fuller look.", "duration": 60, "gender": "F"},
        "Eyelash Tinting": {"price": 350, "description": "Colors eyelashes for definition.", "duration": 60, "gender": "F"}
    },

    "Nail & Hand Care": {
        "Manicure (Basic, Gel, Spa)": {"price": 200, "description": "Complete hand and nail care.", "duration": 60, "gender": "B"},
        "Hand Spa Treatment": {"price": 300, "description": "Relaxing hand treatment.", "duration": 60, "gender": "B"},
        "Paraffin Wax Treatment": {"price": 350, "description": "Softens and nourishes hands.", "duration": 60, "gender": "F"},
        "Nail Art / Nail Extension": {"price": 500, "description": "Creative nail designs or extensions.", "duration": 60, "gender": "F"},
        "Polish Change": {"price": 150, "description": "Quick polish change for nails.", "duration": 60, "gender": "F"},
        "Arm Whitening / Scrub": {"price": 400, "description": "Brightens and exfoliates arms.", "duration": 60, "gender": "F"},
        "Arm Waxing": {"price": 250, "description": "Removes unwanted hair on arms.", "duration": 60, "gender": "B"}
    },

    "Foot & Leg Care": {
        "Pedicure (Basic, Gel, Spa)": {"price": 250, "description": "Complete foot care and polish.", "duration": 60, "gender": "B"},
        "Foot Spa / Foot Scrub": {"price": 350, "description": "Relaxing foot treatment.", "duration": 60, "gender": "B"},
        "Callus Removal": {"price": 300, "description": "Removes hardened skin on feet.", "duration": 60, "gender": "B"},
        "Foot Massage / Reflexology": {"price": 400, "description": "Massage focused on feet and pressure points.", "duration": 60, "gender": "B"},
        "Paraffin Foot Treatment": {"price": 350, "description": "Softens and nourishes feet.", "duration": 60, "gender": "F"},
        "Leg Whitening / Scrub": {"price": 450, "description": "Brightens and exfoliates legs.", "duration": 60, "gender": "F"},
        "Leg Waxing": {"price": 300, "description": "Removes unwanted hair on legs.", "duration": 60, "gender": "B"}
    },

    "Massage & Body Therapy": {
        "Swedish Massage": {"price": 500, "description": "Gentle full-body massage for relaxation.", "duration": 60, "gender": "B"},
        "Shiatsu Massage": {"price": 550, "description": "Pressure-point massage for muscle tension relief.", "duration": 60, "gender": "B"},
        "Thai Massage": {"price": 600, "description": "Traditional Thai stretching and massage.", "duration": 60, "gender": "B"},
        "Aromatherapy Massage": {"price": 600, "description": "Massage with essential oils for relaxation.", "duration": 60, "gender": "B"},
        "Hot Stone Massage": {"price": 700, "description": "Heated stones massage for muscle relaxation.", "duration": 60, "gender": "B"},
        "Ventosa / Cupping Therapy": {"price": 650, "description": "Vacuum cups therapy for blood circulation.", "duration": 60, "gender": "B"},
        "Deep Tissue Massage": {"price": 700, "description": "Targets deep muscles for tension relief.", "duration": 60, "gender": "B"},
        "Signature Full Body Massage": {"price": 800, "description": "Full body massage with signature techniques.", "duration": 60, "gender": "B"},
        "Prenatal / Postnatal Massage": {"price": 650, "description": "Gentle massage for pregnant or postpartum clients.", "duration": 60, "gender": "F"}
    },

    "Body Treatments & Skin Specialty": {
        "Full Body Scrub (Salt, Sugar, Coffee, Milk, Whitening)": {"price": 700, "description": "Exfoliates and refreshes entire body.", "duration": 60, "gender": "B"},
        "Full Body Whitening Treatment": {"price": 800, "description": "Brightens skin tone.", "duration": 60, "gender": "F"},
        "Body Wrap (Mud, Clay, Seaweed, Chocolate)": {"price": 800, "description": "Hydrating or detoxifying body wrap.", "duration": 60, "gender": "B"},
        "Detoxifying Body Treatment": {"price": 750, "description": "Removes toxins and rejuvenates skin.", "duration": 60, "gender": "B"},
        "Slimming / Firming Treatment": {"price": 850, "description": "Tightens and tones body areas.", "duration": 60, "gender": "F"}
    },

    "Hair Removal / Waxing": {
        "Full Body Wax": {"price": 1200, "description": "Removes hair from the entire body.", "duration": 60, "gender": "B"},
        "Half / Full Leg Wax": {"price": 600, "description": "Removes hair from legs.", "duration": 60, "gender": "B"},
        "Underarm Wax": {"price": 300, "description": "Removes hair from underarms.", "duration": 60, "gender": "B"},
        "Arm Wax": {"price": 250, "description": "Removes hair from arms.", "duration": 60, "gender": "B"},
        "Bikini / Brazilian Wax": {"price": 700, "description": "Intimate area hair removal.", "duration": 60, "gender": "F"},
        "Back Wax": {"price": 400, "description": "Removes hair from back area.", "duration": 60, "gender": "M"},
        "Facial Wax (Lips, Chin, Eyebrows)": {"price": 250, "description": "Removes facial hair for a clean finish.", "duration": 60, "gender": "B"}
    },

    "Special & Wellness Packages": {
        "Bride-to-Be Package (Hair, Makeup, Spa, Nails)": {"price": 2500, "description": "Complete pampering for brides.", "duration": 60, "gender": "F"},
        "Couple Spa Package": {"price": 2000, "description": "Relaxing spa experience for couples.", "duration": 60, "gender": "B"},
        "Relax & Glow Package (Massage + Facial + Foot Spa)": {"price": 1800, "description": "Combined massage, facial, and foot spa.", "duration": 60, "gender": "B"},
        "Total Makeover Package (Hair Color + Treatment + Mani + Pedi + Facial)": {"price": 3000, "description": "Full hair, nails, and facial makeover.", "duration": 60, "gender": "F"},
        "Stress Relief Package (Full Body Massage + Foot Reflex + Body Scrub)": {"price": 2000, "description": "Complete stress relief package.", "duration": 60, "gender": "B"}
    }
}

reservations = []      


rated_staff = {}

ratings = []

root = tk.Tk()
root.title("Fleur d’Iris Salon & Spa System")
root.geometry("800x600")
root.config(bg="white")



def clear_frame():
    for widget in root.winfo_children():
        widget.destroy()

def show_panel(panel_function):
    clear_frame()
    panel_function()


def main_menu():
    clear_frame()

    try:
        bg_image = Image.open(r"C:\Users\nhel\Desktop\Salon Image\salon.jpg").resize((800, 600))
        bg_photo = ImageTk.PhotoImage(bg_image) 
        bg_label = tk.Label(root, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        canvas = tk.Canvas(root, width=800, height=600, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")
        canvas.image = bg_photo
    except Exception as e:
        print(f"Background image not loaded: {e}")
        canvas = tk.Canvas(root, width=800, height=600, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

    frame = tk.Frame(canvas, bg="", bd=0, highlightthickness=0)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text="Fleur d’Iris Salon & Spa",
             font=("Brush Script MT", 40, "bold"),
             fg="black").pack(pady=10)

    def open_login(role):
        login_screen(role)

    def show_about():
        about_win = tk.Toplevel(root)
        about_win.title("About Fleur d’Iris")
        about_win.geometry("600x500")
        about_win.resizable(False, False)

        bg_path = r"C:\Users\nhel\Desktop\Salon Image\salon.jpg"
        bg_image = Image.open(bg_path).resize((600, 500))
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(about_win, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        panel = tk.Frame(about_win, bg="white", bd=2, relief="groove")
        panel.place(relx=0.5, rely=0.5, anchor="center", width=450, height=380)

        tk.Label(panel, text="Fleur d’Iris Salon System",
                 font=("Arial Rounded MT Bold", 22),
                 fg="black", bg="white").pack(pady=15)

        tk.Label(panel,
                 text="A Salon & Spa Management System\n"
                      "made for appointments, customers,\n"
                      "employees, and service handling.",
                 font=("Arial", 14),
                 fg="black", bg="white",
                 justify="center").pack(pady=10)

        tk.Label(panel, text="Contact Details:",
                 font=("Arial Rounded MT Bold", 16),
                 fg="black", bg="white").pack(pady=10)

        tk.Label(panel,
                 text="Email: bacitalvin@gmail.com\n"
                      "Phone: 09469125585\n"
                      "Address: Wawa, Nasugbu, Batangas",
                 font=("Arial", 13),
                 fg="black", bg="white",
                 justify="center").pack()

        tk.Button(panel, text="Close",
                  font=("Arial", 14, "bold"),
                  bg="pink", fg="black",
                  width=12, command=about_win.destroy).pack(pady=20)

    btn_style = {"bg": "white", "fg": "black",
                 "font": ("Arial", 18, "bold"),
                 "width": 20, "height": 1, "bd": 0}

    tk.Button(frame, text="Login as Admin", command=lambda: open_login("Admin"), **btn_style).pack(pady=10)
    tk.Button(frame, text="Login as Staff", command=lambda: open_login("Staff"), **btn_style).pack(pady=10)
    tk.Button(frame, text="Login as Customer", command=lambda: open_login("Customer"), **btn_style).pack(pady=10)
    tk.Button(frame, text="Register", command=register_screen, **btn_style).pack(pady=10)
    tk.Button(frame, text="About", command=show_about, **btn_style).pack(pady=10)
    tk.Button(frame, text="Exit", command=root.destroy, **btn_style).pack(pady=10)



def login_screen(role):
    clear_frame()
    root.config(bg="white")

    bg_path = r"C:\Users\nhel\Desktop\Salon Image\mountain.jpg"
    bg_image = Image.open(bg_path)
    bg_image = bg_image.resize((800, 600))  
    bg_photo = ImageTk.PhotoImage(bg_image)

    canvas = tk.Canvas(root, width=800, height=600, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    canvas.bg = bg_photo
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    canvas.create_text(400, 80, text=f"{role.upper()} LOGIN", font=("Arial Rounded MT Bold", 32), fill="white")

    canvas.create_text(400, 180, text="Username:", font=("Arial", 20, "bold"), fill="white")
    username_entry = tk.Entry(canvas, font=("Arial", 18), width=25, bd=3)
    canvas.create_window(400, 230, window=username_entry)

    canvas.create_text(400, 300, text="Password:", font=("Arial", 20, "bold"), fill="white")
    password_entry = tk.Entry(canvas, show="*", font=("Arial", 18), width=25, bd=3)
    canvas.create_window(400, 350, window=password_entry)

    def do_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if username not in users:
            messagebox.showerror("Error", "Invalid username or password.")
            return

        if users[username]["password"] == password and users[username]["role"] == role:
            messagebox.showinfo("Login Success", f"Welcome {username}!")    
            if role == "Admin":
                admin_menu()
            elif role == "Staff":
                staff_menu(username)
            elif role == "Customer":
                customer_menu(username)
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    login_btn = tk.Button(canvas, text="Login", font=("Arial", 18, "bold"), bg="pink", fg="black", width=12, command=do_login)
    canvas.create_window(400, 430, window=login_btn)

    back_btn = tk.Button(canvas, text="Back", font=("Arial", 18, "bold"), bg="pink", fg="black", width=12, command=main_menu)
    canvas.create_window(400, 490, window=back_btn)




def register_screen():
    clear_frame()
    
    main_frame = tk.Frame(root, bg="white")
    main_frame.place(relx=0.5, rely=0.5, anchor="center") 

    tk.Label(main_frame, text="REGISTER ACCOUNT",
             font=("Arial Rounded MT Bold", 20), 
             fg="pink", bg="white").pack(pady=10)

    def validate_numeric(P):
        
        if P.isdigit() or P == "":
            return True
        return False

    vcmd_numeric = main_frame.register(validate_numeric)


    tk.Label(main_frame, text="Full Name:", font=("Arial", 14, "bold"), fg="black", bg="white").pack()
    fullname_entry = tk.Entry(main_frame, font=("Arial", 14), width=15, bd=3, relief="solid")
    fullname_entry.pack(pady=2)

    tk.Label(main_frame, text="Email Address:", font=("Arial", 14, "bold"), fg="black", bg="white").pack()
    email_entry = tk.Entry(main_frame, font=("Arial", 14), width=15, bd=3, relief="solid")
    email_entry.pack(pady=2)

    tk.Label(main_frame, text="Contact Number:", font=("Arial", 14, "bold"), fg="black", bg="white").pack()
    contact_entry = tk.Entry(
        main_frame, 
        font=("Arial", 14), 
        width=15, 
        bd=3, 
        relief="solid",
        validate="key",                    
        validatecommand=(vcmd_numeric, '%P') 
    )
    contact_entry.pack(pady=2)


    tk.Label(main_frame, text="Username:", font=("Arial", 14, "bold"), fg="black", bg="white").pack()
    username_entry = tk.Entry(main_frame, font=("Arial", 14), width=15, bd=3, relief="solid")
    username_entry.pack(pady=2)

    tk.Label(main_frame, text="Password:", font=("Arial", 14, "bold"), fg="black", bg="white").pack()
    password_entry = tk.Entry(main_frame, show="*", font=("Arial", 14), width=15, bd=3, relief="solid")
    password_entry.pack(pady=2)

    tk.Label(main_frame, text="Role:", font=("Arial", 14, "bold"), fg="black", bg="white").pack()
    role_combo = ttk.Combobox(main_frame, values=["Admin", "Staff", "Customer"], font=("Arial", 12), width=10, state="readonly")
    role_combo.pack(pady=2)
    role_combo.set("Customer") 

    specialty_label = tk.Label(main_frame, text="Specialty (for Staff only):",
                               font=("Arial", 14, "bold"), fg="black", bg="white")

    specialties = list(services.keys())

    specialty_combo = ttk.Combobox(main_frame, values=specialties, font=("Arial", 12), width=25, state="readonly")

    def on_role_change(event):
        
        if role_combo.get() == "Staff":
            specialty_label.pack()
            specialty_combo.pack(pady=5)
        else:
            specialty_label.pack_forget()
            specialty_combo.pack_forget()

    role_combo.bind("<<ComboboxSelected>>", on_role_change)

    def create_account():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        role = role_combo.get().strip()
        specialty = specialty_combo.get().strip()
        
        full_name = fullname_entry.get().strip()
        email = email_entry.get().strip()
        contact = contact_entry.get().strip()

        if not username or not password or not role or not full_name or not email or not contact:
            messagebox.showerror("Error", "All fields are required. Please fill in all details.")
            return
        
        if not contact.isdigit() and contact != "":
             messagebox.showerror("Error", "Contact number must contain only digits.")
             return
             
        if username in users:
            messagebox.showerror("Error", "Username already exists.")
            return

        user_data = {
            "password": password,
            "role": role,
            "name": full_name,
            "email": email,
            "contact": contact
        }

        if role == "Staff":
            if not specialty:
                messagebox.showerror("Error", "Please select a specialty for staff.")
                return

            success = create_user(
               username=username,
               password=password,
               role="Staff",
               name=full_name,
               category=specialty
            )

            if success:
              users[username] = user_data
              messagebox.showinfo("Success", f"Staff account for {username} created successfully in category: {specialty}!")
            else:
               messagebox.showerror("Error", f"Failed to register {username}.")
               return


        elif role == "Customer":
            
            success = create_customers(username, password, full_name, email, contact)
            if success:
                users[username] = user_data
                messagebox.showinfo("Success", f"Customer account for {username} created successfully!")
            else:
                messagebox.showerror("Error", f"Failed to register {username}.")
                return


        elif role == "Admin" or role == "Staff":
            success = create_user(username, password, role, name=full_name, email=email, phone=contact, specialty=specialty if role=="Staff" else None)
            if success:
                users[username] = user_data
                messagebox.showinfo("Success", f"{role} account for {username} created successfully!")
            else:
                messagebox.showerror("Error", f"Failed to register {username}.")
            return

            
        
        main_menu()

    tk.Button(main_frame, text="Register", font=("Arial", 14, "bold"),
             bg="pink", fg="black", width=12, command=create_account).pack(pady=10)

    tk.Button(main_frame, text="Back", font=("Arial", 14, "bold"),
             bg="pink", fg="black", width=12, command=main_menu).pack(pady=5)
    

def validate_numeric(P):
    
    return P.isdigit() or P == ""
vcmd_numeric = root.register(validate_numeric)

def confirm_delete(username):
    global users, reservations, staff_schedules
    
    response = messagebox.askyesno("Confirm Deletion", 
                                   f"Are you sure you want to permanently delete the Staff account for {username}?\n\n"
                                   f" WARNING: This will also update all their pending reservations to 'Pending - Staff Unavailable'.")
    
    if not response:
        return

    pending_count = 0
    
    for res in reservations:
        if res.get("staff") == username:
            if res.get("status") in ("Pending", "Confirmed", "Awaiting Payment"):
                res["status"] = "Pending - Staff Unavailable"
                res["staff"] = "Unassigned" 
                pending_count += 1

    if username in users:
        del users[username]
        
    if username in staff_schedules:
        del staff_schedules[username]
        
    messagebox.showinfo("Success", 
                        f"Staff account for {username} has been deleted.\n"
                        f"Total {pending_count} pending reservations were updated.")
    
    manage_registration() 

def delete_user_form(role):
    if role != "Staff":
        messagebox.showerror("Error", "This function is only for deleting Staff accounts.")
        return

    clear_frame()
    tk.Label(root, text="DELETE STAFF ACCOUNT", font=("Arial Rounded MT Bold", 26), fg="red", bg="white").pack(pady=20)

    staff_list = [u for u, d in users.items() if d.get("role") == "Staff"]
    
    if not staff_list:
        tk.Label(root, text="No Staff accounts found.", font=("Arial", 16), bg="white").pack(pady=10)
        tk.Button(root, text="Back", font=("Arial", 16), command=manage_registration).pack(pady=20)
        return

    tk.Label(root, text="Select Staff to Delete:", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
    
    staff_box = ttk.Combobox(root, values=staff_list, font=("Arial", 14), width=30, state="readonly")
    staff_box.pack(pady=5)
    
    if staff_list:
        staff_box.set(staff_list[0]) 

    def delete_selected():
        selected_staff = staff_box.get()
        if not selected_staff:
            messagebox.showerror("Error", "Please select a staff member to delete.")
            return

        confirm_delete(selected_staff)
        
    tk.Button(root, text="Delete Selected Staff", font=("Arial", 16, "bold"),
              bg="red", fg="white", width=25, command=delete_selected).pack(pady=20)
              
    tk.Button(root, text="Cancel", font=("Arial", 16),
              bg="gray", fg="white", width=25, command=manage_registration).pack(pady=10)


def add_user_form(role):
    global vcmd_numeric, services
    clear_frame()
    tk.Label(root, text=f"ADD NEW {role.upper()}", font=("Arial Rounded MT Bold", 26), fg="pink", bg="white").pack(pady=20)

    form_frame = tk.Frame(root, bg="white")
    form_frame.pack(pady=10, padx=20)
    
    fields = [
        ("Full Name:", "fullname_entry"),
        ("Email Address:", "email_entry"),
        ("Contact Number:", "contact_entry", True), 
        ("Username:", "username_entry"),
        ("Password:", "password_entry", False, True)
    ]

    entries = {}
    
    for i, (label_text, key, *options) in enumerate(fields):
        tk.Label(form_frame, text=label_text, font=("Arial", 14, "bold"), bg="white").grid(row=i, column=0, sticky="w", pady=5, padx=10)
        
        is_numeric = options[0] if len(options) > 0 else False
        is_password = options[1] if len(options) > 1 else False
        
        entry_kwargs = {"font": ("Arial", 14), "width": 25, "bd": 1, "relief": "solid"}
        
        if is_numeric:
            entry_kwargs["validate"] = "key"
            entry_kwargs["validatecommand"] = (vcmd_numeric, '%P')
        
        if is_password:
            entry_kwargs["show"] = "*"
            
        entry = tk.Entry(form_frame, **entry_kwargs)
        entry.grid(row=i, column=1, pady=5, padx=10)
        entries[key] = entry
    
    specialty_combo = None
    if role == "Staff":
        tk.Label(form_frame, text="Service Category:", font=("Arial", 14, "bold"), bg="white").grid(row=len(fields), column=0, sticky="w", pady=5, padx=10)
        
        specialties = sorted(list(services.keys()))
        specialty_combo = ttk.Combobox(form_frame, values=specialties, font=("Arial", 14), width=23, state="readonly")
        specialty_combo.grid(row=len(fields), column=1, pady=5, padx=10)
    
    def finalize_user_creation():
        global users, staff_schedules
        username = entries["username_entry"].get().strip()
        password = entries["password_entry"].get().strip()
        full_name = entries["fullname_entry"].get().strip()
        email = entries["email_entry"].get().strip()
        contact = entries["contact_entry"].get().strip()
        
        if not all([username, password, full_name, email, contact]):
            messagebox.showerror("Error", "All user fields must be filled.")
            return

        if username in users:
            messagebox.showerror("Error", "Username already exists. Please choose another one.")
            return

        user_data = {
            "password": password,
            "role": role,
            "name": full_name,
            "email": email,
            "contact": contact
        }

        if role == "Staff":
            if not specialty:
                messagebox.showerror("Error", "Please select a specialty for staff.")
                return

            success = create_user(
                username=username,
                password=password,
                role="Staff",
                name=full_name,
                category=specialty,
                email=email,
                phone=contact
            )

            if success:

                assign_staff_specialty(username, specialty)

                user_data["category"] = specialty
                users[username] = user_data
                staff_schedules[username] = [] 

                messagebox.showinfo("Success", f"New Staff account created: {username} ({specialty}).")
            else:
                messagebox.showerror("Error", f"Failed to register {username}.")
                return    

        elif role == "Customer":
            success = create_customers(username, password, full_name, email, contact)
            if success:
                users[username] = user_data
                messagebox.showinfo("Success", f"New Customer account created: {username}.")
            else:
                messagebox.showerror("Error", f"Failed to register {username}.")
                return

        manage_registration() 

    tk.Button(root, text=f"Confirm Add {role}", font=("Arial", 16, "bold"),
              bg="pink", fg="black", width=20, 
              command=finalize_user_creation).pack(pady=15)
              
    tk.Button(root, text="Cancel", font=("Arial", 16),
              bg="gray", fg="white", width=20, 
              command=manage_registration).pack(pady=5)


def manage_registration():
    clear_frame()
    tk.Label(root, text="MANAGE USER REGISTRATIONS", font=("Arial Rounded MT Bold", 26), fg="pink", bg="white").pack(pady=20)
    
    tk.Button(root, text="Add New Customer", font=("Arial", 16, "bold"),
              bg="#ADD8E6", fg="black", width=30, height=2,
              command=lambda: add_user_form("Customer")).pack(pady=10)
              
    tk.Button(root, text="Add New Staff", font=("Arial", 16, "bold"),
              bg="#90EE90", fg="black", width=30, height=2,
              command=lambda: add_user_form("Staff")).pack(pady=10)
    
    tk.Button(root, text="Delete Staff Account", font=("Arial", 16, "bold"),
              bg="#FF6347", fg="white", width=30, height=2,
              command=lambda: delete_user_form("Staff")).pack(pady=10)
              
    tk.Button(root, text="Back to Admin Menu", font=("Arial", 16, "bold"),
              bg="gray", fg="white", width=30, command=admin_menu).pack(pady=30)

# ADMIN MENU

def admin_menu():
    clear_frame()
    tk.Label(root, text="ADMIN MENU", font=("Arial Rounded MT Bold", 26),
             fg="pink", bg="white").pack(pady=20)

    btn = {"bg": "pink", "fg": "black", "font": ("Arial", 16, "bold"),
           "width": 25, "height": 1, "bd": 0}

  
    def view_users_panel():
        clear_frame()

        try:
            bg_image = Image.open(r"C:\Users\nhel\Desktop\Salon Image\page.jpg").resize((800, 600))
            bg_photo = ImageTk.PhotoImage(bg_image)
            bg_label = tk.Label(root, image=bg_photo)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            bg_label.image = bg_photo
        except:
            root.config(bg="white")

        tk.Label(root, text="ALL USERS",
                 font=("Arial Rounded MT Bold", 20),
                 fg="pink", bg="#fcd6e0").pack(pady=10)

        canvas = tk.Canvas(root, bg="white", highlightthickness=0)
        v_scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        v_scrollbar.pack(side="right", fill="y")

        if users:
            for u, d in users.items():
                
                specialty_or_category = d.get("category", "N/A")
                
                if specialty_or_category == "N/A":
                    specialty_or_category = d.get("service", "N/A")

                tk.Label(scroll_frame, text=f" {u} | Role: {d['role']} | Specialty: {specialty_or_category}",
                         font=("Arial", 12), fg="black", bg="white").pack(anchor="w", padx=20, pady=5)
        else:
            tk.Label(scroll_frame, text="No users available.", font=("Arial", 12),
                     fg="gray", bg="white").pack(pady=20)

        tk.Button(root, text="Back", command=admin_menu,
                  bg="pink", fg="black", font=("Arial", 14, "bold")).pack(pady=10)

    
    def change_staff_role_panel():
        clear_frame()
        tk.Label(root, text="CHANGE STAFF ROLE",
                 font=("Arial Rounded MT Bold", 22),
                 fg="pink", bg="white").pack(pady=20)

        staff_list = [u for u, d in users.items() if d.get("role") == "Staff"]

        if not staff_list:
            tk.Label(root, text="No staff available.", font=("Arial", 14), fg="gray", bg="white").pack()
            tk.Button(root, text="Back", command=admin_menu, bg="gray", fg="white").pack(pady=5)
            return

        tk.Label(root, text="Select Staff:", font=("Arial", 14), bg="white").pack()
        staff_combo = ttk.Combobox(root, values=staff_list, font=("Arial", 12), state="readonly")
        staff_combo.pack(pady=10)

        tk.Label(root, text="Select New Specialty Category:", font=("Arial", 14), bg="white").pack()

        roles = list(services.keys()) 

        role_combo = ttk.Combobox(root, values=roles, font=("Arial", 12), state="readonly")
        role_combo.pack(pady=10)

        def apply_change():
            staff = staff_combo.get()
            new_category = role_combo.get()

            if not staff or not new_category:
                messagebox.showerror("Error", "Please select both staff and category.")
                return
            
            if staff in users:
                users[staff]["category"] = new_category 

                new_services_data = services.get(new_category, {})
                
                staff_specialty = {}
                for service_name, details in new_services_data.items():
                    staff_specialty[service_name] = {
                        "price": details.get("price", 0),
                        "description": details.get("description", ""),
                        "duration": details.get("duration", 60) 
                    }
                
                users[staff]["specialty"] = staff_specialty

                messagebox.showinfo("Success", f"{staff}'s Specialty Category and Assigned Services are now: {new_category}")
            else:
                messagebox.showerror("Error", "Staff user not found.")


        tk.Button(root, text="Apply Change", command=apply_change,
                  bg="pink", fg="black", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Button(root, text="Back", command=admin_menu,
                  bg="gray", fg="white", font=("Arial", 12, "bold")).pack(pady=10)


    def view_reservations_panel():
        clear_frame()
        tk.Label(root, text="ALL RESERVATIONS", font=("Arial Rounded MT Bold", 20),
                 fg="pink", bg="#fcd6e0").pack(pady=10)

        canvas = tk.Canvas(root, bg="white", highlightthickness=0)
        v_scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        v_scrollbar.pack(side="right", fill="y")

        if reservations:
            for r in reservations:
                
                try:
                    time_display = datetime.strptime(r['time'], "%H:%M").strftime("%I:%M %p").lstrip('0')
                except:
                    time_display = r.get('time', 'N/A')
                    
                tk.Label(scroll_frame, text=f"👤 {r['customer']} | Service: {r['service']} | Staff: {r['staff']} | {r.get('date', 'N/A')} @ {time_display} | Status: {r['status']}",
                         font=("Arial", 12), fg="black", bg="white").pack(anchor="w", padx=20, pady=5)
        else:
            tk.Label(scroll_frame, text="No reservations yet.", font=("Arial", 12), fg="gray", bg="white").pack(pady=20)

        tk.Button(root, text="Back", command=admin_menu,
                  bg="pink", fg="black", font=("Arial", 14, "bold")).pack(pady=10)

  
    def manage_services_panel():
        clear_frame()
        tk.Label(root, text="MANAGE SERVICES", font=("Arial Rounded MT Bold", 20),
                 fg="pink", bg="white").pack(pady=10)
        tk.Label(root, text="Feature coming soon...", font=("Arial", 14), bg="white").pack(pady=50)
        tk.Button(root, text="Back", command=admin_menu, bg="gray", fg="white").pack(pady=5)

    
    def staff_schedule_panel():
        clear_frame()
        tk.Label(root, text="STAFF SCHEDULE", font=("Arial Rounded MT Bold", 20),
                 fg="pink", bg="white").pack(pady=10)

        canvas = tk.Canvas(root, bg="white", highlightthickness=0)
        v_scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        v_scrollbar.pack(side="right", fill="y")

        if staff_schedules:
            for staff_name, schedules in staff_schedules.items():
                tk.Label(scroll_frame, text=f"👤 STAFF: {staff_name}",
                         font=("Arial Rounded MT Bold", 14),
                         fg="pink", bg="white").pack(anchor="w", padx=10, pady=10)

                if schedules:
                    for s in schedules:
                        tk.Label(scroll_frame,
                                 text=f"   🗓 {s['date']} | {s['start']} - {s['end']}",
                                 font=("Arial", 12),
                                 fg="black", bg="white").pack(anchor="w", padx=30, pady=3)
                else:
                    tk.Label(scroll_frame,
                             text="   No schedules yet.",
                             font=("Arial", 12),
                             fg="gray", bg="white").pack(anchor="w", padx=30, pady=3)
        else:
            tk.Label(scroll_frame,
                     text="No staff schedules found.",
                     font=("Arial", 14),
                     fg="gray", bg="white").pack(anchor="w", padx=10, pady=10)


        tk.Button(root, text="Back", command=admin_menu,
                  bg="gray", fg="white").pack(pady=5)

   
    def reports_panel():
        clear_frame()
        tk.Label(root, text="REPORTS & ANALYTICS",
                 font=("Arial Rounded MT Bold", 20),
                 fg="pink", bg="white").pack(pady=20)

        report_frame = tk.Frame(root, bg="white")
        report_frame.pack(pady=10)

        total_customers = len([u for u in users.values() if u.get("role") == "Customer"])
        tk.Label(report_frame, text=f"👥 Total Customers: {total_customers}", font=("Arial", 14), bg="white").pack(anchor="w")

        total_reservations = len(reservations)
        tk.Label(report_frame, text=f"Total Reservations: {total_reservations}", font=("Arial", 14), bg="white").pack(anchor="w")

        completed_reservations = len([r for r in reservations if r.get("status") == "Completed"])
        tk.Label(report_frame, text=f"Completed Reservations: {completed_reservations}", font=("Arial", 14), bg="white").pack(anchor="w")

        if reservations:
            service_count = {}
            for r in reservations:
                service_name = r.get("service")
                service_count[service_name] = service_count.get(service_name, 0) + 1

            if service_count:
                most_popular = max(service_count, key=service_count.get)
                tk.Label(report_frame, text=f"🔥 Most Popular Service: {most_popular}", font=("Arial", 14), bg="white").pack(anchor="w", pady=10)
            else:
                 tk.Label(report_frame, text="No service data yet.", font=("Arial", 12), fg="gray", bg="white").pack(anchor="w", pady=10)

            staff_count = {}
            for r in reservations:
                staff_name = r.get("staff")
                staff_count[staff_name] = staff_count.get(staff_name, 0) + 1

            if staff_count:
                most_active_staff = max(staff_count, key=staff_count.get)
                tk.Label(report_frame, text=f"Most Active Staff: {most_active_staff}", font=("Arial", 14), bg="white").pack(anchor="w")
            else:
                tk.Label(report_frame, text="No staff activity recorded.", font=("Arial", 12), fg="gray", bg="white").pack(anchor="w")

        else:
            tk.Label(report_frame, text="No data yet to generate reports.", font=("Arial", 12), fg="gray", bg="white").pack(anchor="w", pady=10)


        tk.Button(root, text="Back", command=admin_menu,
                  bg="gray", fg="white", font=("Arial", 12, "bold")).pack(pady=20)


    def view_staff_ratings_panel():
        clear_frame()
        tk.Label(root, text="STAFF RATINGS & COMMENTS", font=("Arial Rounded MT Bold", 24),
                 fg="pink", bg="white").pack(pady=20)

        canvas = tk.Canvas(root, bg="white", highlightthickness=0)
        v_scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        v_scrollbar.pack(side="right", fill="y")

        staff_names = list({r["staff"] for r in reservations if "staff" in r})

        if not staff_names:
            tk.Label(scroll_frame, text="No staff found in reservations.", font=("Arial", 14),
                     fg="gray", bg="white").pack(pady=10)
        else:
            for staff_name in staff_names:
                tk.Label(scroll_frame, text=f"👤 {staff_name}", font=("Arial Rounded MT Bold", 16),
                         fg="pink", bg="white").pack(anchor="w", padx=10, pady=10)

                staff_ratings = [r for r in reservations if r.get("staff") == staff_name and "rating" in r]

                if not staff_ratings:
                    tk.Label(scroll_frame, text="   No ratings yet.", font=("Arial", 12),
                             fg="gray", bg="white").pack(anchor="w", padx=30, pady=5)
                else:
                    for r in staff_ratings:
                        comment_text = r.get("comment", "No comment")
                        tk.Label(scroll_frame,
                                 text=f"   ⭐ {r['rating']} | Customer: {r['customer']} | Service: {r['service']}\n     Comment: {comment_text}",
                                 font=("Arial", 12), fg="black", bg="white", justify="left").pack(anchor="w", padx=30, pady=5)

        tk.Button(root, text="Back", bg="gray", fg="white", font=("Arial", 12, "bold"),
                  command=admin_menu).pack(pady=20)

    tk.Button(root, text="View All Users", command=view_users_panel, **btn).pack(pady=5)
    
    tk.Button(root, text="Manage Registrations (Users)", command=manage_registration, **btn).pack(pady=5)
    
    tk.Button(root, text="Change Staff Role", command=change_staff_role_panel, **btn).pack(pady=5)
    tk.Button(root, text="View All Reservations", command=view_reservations_panel, **btn).pack(pady=5)
    tk.Button(root, text="Manage Services", command=manage_services_panel, **btn).pack(pady=5)
    tk.Button(root, text="Staff Schedule", command=staff_schedule_panel, **btn).pack(pady=5)
    tk.Button(root, text="Reports & Analytics", command=reports_panel, **btn).pack(pady=5)
    tk.Button(root, text="View Staff Ratings", command=view_staff_ratings_panel, **btn).pack(pady=5)
    tk.Button(root, text="Logout", command=main_menu, **btn).pack(pady=15)
    
# STAFF MENU

def view_staff_profile(username):
    clear_frame()
    staff_data = users.get(username, {}) 
    
    tk.Label(root, text="STAFF PROFILE INFORMATION",
             font=("Arial Rounded MT Bold", 26), fg="pink", bg="white").pack(pady=20)
    
    details_frame = tk.Frame(root, bg="white", padx=10, pady=10)
    details_frame.pack(pady=10)

    display_fields = {
        "Name": "name",
        "Role": "role",
        "Email": "email",
        "Contact No.": "contact",
        "Specialty Category": "category" 
    }
    
    row = 0
    tk.Label(details_frame, text="Username:", font=("Arial", 14, "bold"), bg="white").grid(row=row, column=0, sticky="w", padx=10, pady=2)
    tk.Label(details_frame, text=username, font=("Arial", 14), bg="white").grid(row=row, column=1, sticky="w", pady=2)
    row += 1
    
    for label, key in display_fields.items():
        value = staff_data.get(key, 'N/A')
        tk.Label(details_frame, text=f"{label}:", font=("Arial", 14, "bold"), bg="white").grid(row=row, column=0, sticky="w", padx=10, pady=2)
        tk.Label(details_frame, text=value, font=("Arial", 14), bg="white").grid(row=row, column=1, sticky="w", pady=2)
        row += 1
    
    staff_services = get_staff_services_from_db(username)
    if staff_services:
        tk.Label(root, text="ASSIGNED SERVICES",
                 font=("Arial Rounded MT Bold", 18), fg="#FF69B4", bg="white").pack(pady=10)
        
        services_frame = tk.Frame(root, bg="white")
        services_frame.pack(padx=20, pady=5, fill="x")

        columns = ("Category", "Service Name", "Price (₱)", "Duration")
        service_tree = ttk.Treeview(services_frame, columns=columns, show="headings")
        
        for col in columns:
            service_tree.heading(col, text=col)
            service_tree.column(col, width=150, anchor="center")
        
        for svc in staff_services:
            service_tree.insert("", "end", values=(
                svc["category"],
                svc["service_name"],
                f"₱ {svc['price']:,.2f}",
                f"{svc['duration_minutes']} mins"
            ))

        service_tree.pack(fill="x", expand=True)

    tk.Button(root, text="Back", command=lambda: staff_menu(username), 
              bg="pink", fg="black", font=("Arial", 16, "bold")).pack(pady=30)



def staff_menu(username):
    clear_frame()
    
    tk.Label(root, text=f"STAFF MENU ({username})", font=("Arial Rounded MT Bold", 26),
             fg="pink", bg="white").pack(pady=20)

    btn_style = {"bg": "pink", "fg": "black",
                 "font": ("Arial", 16, "bold"),
                 "width": 25, "height": 1, "bd": 0}

    def view_assigned():
        clear_frame()
        tk.Label(root, text="MY ASSIGNED RESERVATIONS",
                 font=("Arial Rounded MT Bold", 24), fg="pink", bg="white").pack(pady=15)

        frame_container = tk.Frame(root, bg="white")
        frame_container.pack(fill="both", expand=True, padx=20, pady=10)

        canvas = tk.Canvas(frame_container, bg="white")
        scrollbar_y = tk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
        scrollbar_x = tk.Scrollbar(frame_container, orient="horizontal", command=canvas.xview)

        scrollable_frame = tk.Frame(canvas, bg="white")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        own = [r for r in reservations if r["staff"] == username]

        if not own:
            tk.Label(scrollable_frame, text="No assigned reservations.",
                     font=("Arial", 16), fg="gray", bg="white").pack(pady=20)
        else:
            header = tk.Label(scrollable_frame,
                              text=f"{'Customer':<20}{'Service':<30}{'Date':<15}{'Status':<15}",
                              font=("Arial", 14, "bold"), bg="pink", fg="white", anchor="w", justify="left")
            header.pack(fill="x", pady=5, padx=5)
            
            for r in own:
                customer = r.get("customer", "Unknown")
                service = r.get("service", "Unknown")
                date = r.get("date", "N/A")
                status = r.get("status", "Pending")
                row_text = f"{customer:<20}{service:<30}{date:<15}{status:<15}"
                tk.Label(scrollable_frame, text=row_text, font=("Arial", 13),
                          bg="white", fg="black", anchor="w", justify="left").pack(fill="x", padx=5, pady=2)

        tk.Button(root, text="Back", font=("Arial", 16, "bold"),
                  bg="pink", fg="black", width=10,
                  command=lambda: staff_menu(username)).pack(pady=10)

    def open_update_gui():
        global own, own_indices, listbox, update_win

        own = []
        own_indices = []
        for i, r in enumerate(reservations):
            if r["staff"] == username:
                own.append(r)
                own_indices.append(i)
        
        if not own:
            messagebox.showinfo("Info", "No reservations assigned.")
            return

        update_win = tk.Toplevel(root)
        update_win.title("Update Reservation Status")
        update_win.geometry("850x550")
        update_win.config(bg="white")

        tk.Label(update_win, text="Select Reservation to Update",
                 font=("Arial Rounded MT Bold", 18), bg="white", fg="pink").pack(pady=10)

        frame = tk.Frame(update_win, bg="white")
        frame.pack(pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(frame, font=("Arial", 13), width=100, height=15, yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        for i, r in enumerate(own):
            customer = r.get("customer", "Unknown")
            service = r.get("service", "Unknown")
            date = r.get("date", "N/A")
            status = r.get("status", "Pending")
            listbox.insert(tk.END, f"{i+1}. {customer} | {service} | {date} | STATUS: {status}")

        alert_label = tk.Label(update_win, text="", font=("Arial", 12, "italic"), bg="white", fg="red")
        alert_label.pack(pady=5)

        def update_reservation_status(new_status, is_completion=False):
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("Select", "Please select a reservation first.")
                return

            idx = sel[0]
            true_index = own_indices[idx]
            res = reservations[true_index]

            current_status = res.get("status", "Pending")

            if current_status == "Completed" and new_status in ["Cancelled", "On-Going", "No-Show (Cancelled)"]:
                messagebox.showerror("Error", "Completed reservations cannot be changed to Cancelled, On-Going, or No-Show.")
                return
            if current_status == "No-Show (Cancelled)" and new_status in ["On-Going", "Completed"]:
                messagebox.showerror("Error", "No-Show reservations cannot be changed to On-Going or Completed.")
                return
            if current_status == "Cancelled" and new_status in ["On-Going", "Completed"]:
                messagebox.showerror("Error", "Cancelled reservations cannot be changed to On-Going or Completed.")
                return

            res_id = res.get("id")
            print("DEBUG Reservation:", res)
            if not res_id:
                messagebox.showerror("Error", "Reservation ID not found!")
                return
               
            update_reservation_status_db(res_id, new_status)
            load_data_from_db()

            messagebox.showinfo("Updated", f"Reservation marked as {new_status}!")
            update_win.destroy()
            open_update_gui()  

        btn_frame = tk.Frame(update_win, bg="white")
        btn_frame.pack(pady=15)

        btn_complete = tk.Button(btn_frame, text="Complete", command=lambda: update_reservation_status("Completed", True),
                                 font=("Arial", 14, "bold"), bg="lightgreen", fg="black", width=12)
        btn_complete.grid(row=0, column=0, padx=5, pady=5)

        btn_cancel = tk.Button(btn_frame, text="Cancel", command=lambda: update_reservation_status("Cancelled"),
                               font=("Arial", 14, "bold"), bg="red", fg="white", width=12)
        btn_cancel.grid(row=0, column=1, padx=5, pady=5)

        btn_no_show = tk.Button(btn_frame, text="No-Show", command=lambda: update_reservation_status("No-Show (Cancelled)"),
                                font=("Arial", 14, "bold"), bg="orange", fg="black", width=12)
        btn_no_show.grid(row=0, column=2, padx=5, pady=5)

        btn_ongoing = tk.Button(btn_frame, text="On-Going", command=lambda: update_reservation_status("On-Going"),
                                font=("Arial", 14, "bold"), bg="skyblue", fg="black", width=12)
        btn_ongoing.grid(row=0, column=3, padx=5, pady=5)

        listbox.bind("<<ListboxSelect>>", lambda e: None)  



    def add_schedule(username, date, start, end):
        if username not in staff_schedules:
            staff_schedules[username] = []
        
        for sched in staff_schedules[username]:
            if sched["date"] == date:
                sched["start"] = start
                sched["end"] = end
                found = True
                break
        
        
        staff_schedules[username].append({"date": date, "start": start, "end": end})

        for res in reservations:
            if res["staff"] == username and res["date"] == date and res["status"] == "Pending":
                res["status"] = "Confirmed"

    def staff_view_ratings_panel(root, username):
        load_data_from_db() 
        clear_frame() 
            
        tk.Label(root, text=f"Ratings for {username}", font=("Arial Rounded MT Bold", 24), fg="pink", bg="white").pack(pady=20)

        canvas = tk.Canvas(root, bg="white")
        scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw" )
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
            
        own = [r for r in reservations if r["staff"] == username and r.get("rating") is not None]
            
        if not own:
            tk.Label(scroll_frame, text="Wala pang ratings.", font=("Arial", 14), fg="gray", bg="white").pack(pady=10)
        else:
            for rv in own:            
                tk.Label(scroll_frame,                       
                          text=f"Customer: {rv['customer']} | Service: {rv['service']}",
                          font=("Arial", 14, "bold"), bg="white").pack(anchor="w", padx=20, pady=10)
                
                rating_desc = {5: "Excellent", 4: "Very Good", 3: "Average", 2: "Poor", 1: "Very Poor"}.get(rv.get('rating'), 'N/A')
                
                tk.Label(scroll_frame,
                          text=f"Rating: {rv.get('rating', 'No rating')} Stars ({rating_desc})",
                          font=("Arial", 13), bg="white", fg="black").pack(anchor="w", padx=40)

                tk.Label(scroll_frame,
                          text=f"Comment: {rv.get('comment', 'No comment')}",
                          font=("Arial", 12), bg="white", fg="gray20").pack(anchor="w", padx=40)
            

        tk.Button(root, text="Back", font=("Arial", 14, "bold"),
                  bg="pink", fg="black", command=lambda: staff_menu(username)).pack(pady=15) 

    def manage_schedule():
        
        sched_win = tk.Toplevel(root)
        sched_win.title("Manage Schedule")
        sched_win.geometry("400x400")
        sched_win.config(bg="white")

        tk.Label(sched_win, text="Set Your Schedule", font=("Arial", 16, "bold")).pack(pady=10)

        today = dt.date.today()
        dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(8)]

        tk.Label(sched_win, text="Date:", font=("Arial", 12)).pack()
        date_entry = ttk.Combobox(sched_win, values=dates, font=("Arial", 12), state="readonly")
        date_entry.set(dates[0])
        date_entry.pack(pady=5)

        times = []
        for hour in range(7, 22):
            times.append(f"{hour:02d}:00")
            times.append(f"{hour:02d}:30")

        tk.Label(sched_win, text="Start Time:", font=("Arial", 12)).pack()
        start_entry = ttk.Combobox(sched_win, values=times, font=("Arial", 12), state="readonly")
        start_entry.set("Select start time")
        start_entry.pack(pady=5)

        tk.Label(sched_win, text="End Time:", font=("Arial", 12)).pack()
        end_entry = ttk.Combobox(sched_win, values=times, font=("Arial", 12), state="readonly")
        end_entry.set("Select end time")
        end_entry.pack(pady=5)

        def save_schedule():
            date = date_entry.get().strip()
            start = start_entry.get().strip()
            end = end_entry.get().strip()

            if not date or not start or not end or start == "Select start time" or end == "Select end time":
                messagebox.showerror("Error", "Please complete all fields.")
                return

            try:
                start_time = datetime.datetime.strptime(start, "%H:%M").time()
                end_time = datetime.datetime.strptime(end, "%H:%M").time()
                if start_time >= end_time:
                    messagebox.showerror("Error", "End time must be later than start time.")
                    return
            except:
                messagebox.showerror("Error", "Invalid time format.")
                return

            add_schedule(username, date, start, end)
            messagebox.showinfo("Saved", "Schedule added/updated successfully!")
            sched_win.destroy()

        tk.Button(sched_win, text="Save", bg="pink", font=("Arial", 14, "bold"),
                  command=save_schedule).pack(pady=15)

    def view_schedule():
        clear_frame()
        tk.Label(root, text="YOUR SCHEDULE", font=("Arial Rounded MT Bold", 24), fg="pink", bg="white").pack(pady=20)

        canvas = tk.Canvas(root, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=40)
        scrollbar.pack(side="right", fill="y")

        schedules = staff_schedules.get(username, [])
        if not schedules:
            tk.Label(scroll_frame, text="No schedules set yet.", font=("Arial", 14), fg="gray", bg="white").pack(pady=10)
        else:
            for s in schedules:
                tk.Label(scroll_frame, text=f"{s['date']} | {s['start']} - {s['end']}",
                          font=("Arial", 14), fg="black", bg="white").pack(anchor="w", padx=20, pady=2)

        tk.Button(root, text="Back", font=("Arial", 14, "bold"),
                  bg="pink", fg="black", command=lambda: staff_menu(username)).pack(pady=20)
        
    tk.Button(root, text="View My Profile", command=lambda: view_staff_profile(username), **btn_style).pack(pady=10) 
    tk.Button(root, text="View Assigned Reservations", command=view_assigned, **btn_style).pack(pady=10)
    tk.Button(root, text="Update Reservation Status", command=open_update_gui, **btn_style).pack(pady=10)
    tk.Button(root, text="Manage Schedule", command=manage_schedule, **btn_style).pack(pady=10)
    tk.Button(root, text="View Schedule", command=view_schedule, **btn_style).pack(pady=10)
    tk.Button(root, text="View Ratings", command=lambda: staff_view_ratings_panel(root, username), **btn_style).pack(pady=10)
    tk.Button(root, text="Logout", command=main_menu, **btn_style).pack(pady=20)




def view_customer_profile(username):
    clear_frame()
    
    customer_data = users.get(username, {}) 
    
    tk.Label(root, text="MY PROFILE INFORMATION",
             font=("Arial Rounded MT Bold", 26), fg="pink", bg="white").pack(pady=20)
    
    details_frame = tk.Frame(root, bg="white", padx=10, pady=10)
    details_frame.pack(pady=10)
    
    display_fields = {
        "Name": "name",
        "Role": "role",
        "Email": "email",
        "Contact No.": "contact"
    }
    
    row = 0
    
    tk.Label(details_frame, text="Username:", font=("Arial", 14, "bold"), bg="white").grid(row=row, column=0, sticky="w", padx=10, pady=2)
    tk.Label(details_frame, text=username, font=("Arial", 14), bg="white").grid(row=row, column=1, sticky="w", pady=2)
    row += 1
    
    for label, key in display_fields.items():
        value = customer_data.get(key, 'N/A')
             
        tk.Label(details_frame, text=f"{label}:", font=("Arial", 14, "bold"), bg="white").grid(row=row, column=0, sticky="w", padx=10, pady=2)
        tk.Label(details_frame, text=value, font=("Arial", 14), bg="white").grid(row=row, column=1, sticky="w", pady=2)
        row += 1
        
    tk.Button(root, text="Back", command=lambda: customer_menu(username),
              bg="pink", fg="black", font=("Arial", 16, "bold")).pack(pady=30)

def customer_menu(username):
    clear_frame()

    try:
        
        bg_image = Image.open(r"C:\Users\nhel\Desktop\Salon Image\page.jpg").resize((800, 600))
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(root, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg_photo
    except Exception:
        root.config(bg="white")

    title = tk.Label(root,
                      text=f"CUSTOMER MENU ({username})",
                      font=("Arial Rounded MT Bold", 26),
                      fg="pink",
                      bg="#fcd6e0")
    title.place(relx=0.5, rely=0.08, anchor="center")

    btn_style = {
        "bg": "#ffb6c1",
        "fg": "black",
        "font": ("Arial", 16, "bold"),
        "width": 25,
        "height": 1,
        "bd": 0,
        "activebackground": "#ffc0cb",
    }
    
    tk.Button(root, text="View My Profile", command=lambda: view_customer_profile(username), **btn_style).place(relx=0.5, rely=0.20, anchor="center")
    tk.Button(root, text="View Services", command=lambda: view_services(username), **btn_style).place(relx=0.5, rely=0.28, anchor="center")
    tk.Button(root, text="View Staff", command=lambda: view_staff(username), **btn_style).place(relx=0.5, rely=0.36, anchor="center")
    tk.Button(root, text="Reserve a Service", command=lambda: reserve_service(username), **btn_style).place(relx=0.5, rely=0.44, anchor="center")
    tk.Button(root, text="Booking Panel (Alternative)", command=lambda: booking_panel(username), **btn_style).place(relx=0.5, rely=0.52, anchor="center")
    tk.Button(root, text="View My Reservations", command=lambda: view_reservations_customer(username), **btn_style).place(relx=0.5, rely=0.60, anchor="center")
    tk.Button(root, text="View Reservation History", command=lambda: view_reservation_history(username), **btn_style).place(relx=0.5, rely=0.68, anchor="center")
    tk.Button(root, text="Rate a Staff", command=lambda: customer_rate_staff_select_panel(root, username), **btn_style).place(relx=0.5, rely=0.76, anchor="center")    
    tk.Button(root, text="Logout", command=main_menu, 
              bg="red", fg="white", font=("Arial", 16, "bold"), 
              width=25, height=1, bd=0).place(relx=0.5, rely=0.88, anchor="center")



def get_service_duration(service_category, service_name):
    """Parses the duration (which is an integer in your services dict) and returns duration in minutes."""
    try:
        
        duration = services[service_category][service_name]['duration']
        
        if isinstance(duration, int):
            return duration
        
        return 30
    except Exception:
        
        return 30


def is_within_schedule(staff, date, time_obj, service_duration_minutes):
    """
    Check if selected time slot is within staff's schedule, 
    does not conflict with the lunch break (12:00 PM - 1:00 PM), 
    and is not already booked.
    """

    if staff not in staff_schedules or not staff_schedules[staff]:
        return False, f"Staff {staff} has no schedule defined for this date."

    chosen_start_dt = datetime.datetime.combine(date, time_obj)
    chosen_end_dt = chosen_start_dt + datetime.timedelta(minutes=service_duration_minutes)

    break_start = datetime.datetime.combine(date, datetime.time(12, 0))
    break_end = datetime.datetime.combine(date, datetime.time(13, 0))
    if max(chosen_start_dt, break_start) < min(chosen_end_dt, break_end):
        return False, "Booking overlaps with the staff break (12:00 PM - 1:00 PM)."

    is_in_schedule = False
    for sched in staff_schedules[staff]:
        sched_start_dt = datetime.datetime.strptime(f"{sched['date']} {sched['start']}", "%Y-%m-%d %H:%M")
        sched_end_dt = datetime.datetime.strptime(f"{sched['date']} {sched['end']}", "%Y-%m-%d %H:%M")
        if sched_start_dt <= chosen_start_dt and chosen_end_dt <= sched_end_dt:
            is_in_schedule = True
            break
    if not is_in_schedule:
        return False, "Requested time slot is outside staff working hours."

    for r in reservations:
        if r['staff'] == staff and r['date'] == date:
            res_time = r['time']

            if isinstance(res_time, datetime.timedelta):
                res_time = (datetime.datetime.min + res_time).time()

            res_start_dt = datetime.datetime.combine(date, res_time)
            res_end_dt = res_start_dt + datetime.timedelta(minutes=r['duration'])
            if max(chosen_start_dt, res_start_dt) < min(chosen_end_dt, res_end_dt):
                return False, f"Staff is already booked at {r['time']}."

    return True, "Staff is available."



def view_services(username):
    clear_frame()

    try:
        # 
        bg_image = Image.open(r"C:\Users\nhel\Desktop\Salon Image\pp.jpg").resize((800, 600))
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(root, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg_photo 
    except Exception:
        root.config(bg="white")

    tk.Label(root, text="AVAILABLE SERVICES",
             font=("Arial Rounded MT Bold", 22),
             fg="pink", bg="#fcd6e0").pack(pady=10)

    canvas = tk.Canvas(root, bg="white", highlightthickness=0)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="white")

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=40)
    scrollbar.pack(side="right", fill="y")

    for category, items in services.items():
        tk.Label(scroll_frame, text=f"🌸 {category}",
                 font=("Arial Rounded MT Bold", 16),
                 fg="#ff69b4", bg="white").pack(anchor="w", pady=(5, 0))

        for svc_name, svc in items.items():
            tk.Label(scroll_frame, text=f"- {svc_name} (₱{svc['price']}) - {svc['description']} ({svc['duration']})",
                      font=("Arial", 12), fg="black", bg="white").pack(anchor="w", padx=20)

    tk.Button(root, text="Back", command=lambda: customer_menu(username),
              bg="pink", fg="black", font=("Arial", 14, "bold")).pack(pady=10)


def view_staff(username):
    clear_frame()
    
    try:
        # 
        bg_image = Image.open(r"C:\Users\nhel\Desktop\Salon Image\pp.jpg").resize((800, 600))
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(root, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg_photo
    except Exception:
        root.config(bg="white")

    tk.Label(root, text="OUR STAFF",
             font=("Arial Rounded MT Bold", 20),
             fg="pink", bg="#fcd6e0").pack(pady=10)

    canvas = tk.Canvas(root, bg="white", highlightthickness=0)
    v_scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="white")

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=v_scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
    v_scrollbar.pack(side="right", fill="y")

    any_staff = False
    for u, d in users.items():
        if d["role"] == "Staff":
            any_staff = True
            
            category = d.get("category", "N/A")
            raw_specialties = d.get("specialty", [])
            
            if isinstance(raw_specialties, list):
                specialties = ", ".join(raw_specialties)
            else:
                specialties = str(raw_specialties)

            schedule = staff_schedules.get(u, []) 

            tk.Label(scroll_frame, text=f"{d.get('name', u)} ({u}) | Category: {category}",
                      font=("Arial", 12, "bold"), fg="black", bg="white").pack(anchor="w", padx=20, pady=(5,0))

            if schedule:
                tk.Label(scroll_frame, text="Working Schedules:", font=("Arial", 10, "underline"), fg="black", bg="white").pack(anchor="w", padx=40)
                for s in schedule:
                    tk.Label(scroll_frame, text=f"• {s.get('date', 'N/A')}: {s['start']} - {s['end']}",
                              font=("Arial", 10), fg="gray", bg="white").pack(anchor="w", padx=50)
            else:
                 tk.Label(scroll_frame, text="No schedule set.", font=("Arial", 10), fg="gray", bg="white").pack(anchor="w", padx=40)

            spec_frame = tk.Frame(scroll_frame, bg="white")
            spec_frame.pack(anchor="w", padx=40, pady=(0,5))
            tk.Label(spec_frame, text=f"Specialties: {specialties}",
                      font=("Arial", 10), fg="black", bg="white").pack(anchor="w")
            tk.Frame(scroll_frame, height=1, bg="#ffe4e1").pack(fill="x", padx=20, pady=5)

    if not any_staff:
        tk.Label(scroll_frame, text="No staff available.", font=("Arial", 12), fg="gray", bg="white").pack(pady=20)

    tk.Button(root, text="Back", command=lambda: customer_menu(username),
              bg="pink", fg="black", font=("Arial", 14, "bold")).pack(pady=10)


def booking_panel(username):
    clear_frame()
    tk.Label(root, text="BOOKING PANEL (Standard)",
             font=("Arial Rounded MT Bold", 26), fg="pink", bg="white").pack(pady=20)

    panel = tk.Frame(root, bg="white")
    panel.pack(pady=10)

    tk.Label(panel, text="Select Service:", font=("Arial", 14, "bold"), bg="white").grid(row=0, column=0, sticky="w", pady=5)
    service_names = [f"{cat} - {svc_name} - ₱{svc['price']}" 
                     for cat, items in services.items() 
                     for svc_name, svc in items.items()]
    service_box = ttk.Combobox(panel, values=service_names, state="readonly", width=60)
    service_box.grid(row=0, column=1, pady=5)

    tk.Label(panel, text="Select Staff:", font=("Arial", 14, "bold"), bg="white").grid(row=1, column=0, sticky="w", pady=5)
    staff_box = ttk.Combobox(panel, values=[], state="readonly", width=40) 
    staff_box.grid(row=1, column=1, pady=5)

    tk.Label(panel, text="Select Date:", font=("Arial", 14, "bold"), bg="white").grid(row=2, column=0, sticky="w", pady=5)
    today = datetime.date.today()
    date_options = [(today + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    date_box = ttk.Combobox(panel, values=date_options, state="readonly", width=40)
    date_box.grid(row=2, column=1, pady=5)

    tk.Label(panel, text="Select Time:", font=("Arial", 14, "bold"), bg="white").grid(row=3, column=0, sticky="w", pady=5)
    time_options = [f"{h:02d}:{m:02d}" for h in range(7, 22) for m in (0, 30)]
    time_box = ttk.Combobox(panel, values=time_options, state="readonly", width=20)
    time_box.grid(row=3, column=1, pady=5)

    def update_staff(event=None):
        selected_service = service_box.get()
        if not selected_service:
            staff_box['values'] = []
            staff_box.set('')
            return

        parts = selected_service.split(" - ")
        svc_category = parts[0]
        svc_name_only = parts[1]

        available_staff = []
        for u, d in users.items():
            if d.get("role") == "Staff":
                if d.get("category") == svc_category or svc_name_only in d.get("specialty", []):
                    available_staff.append(u)

        staff_box['values'] = available_staff
        staff_box.set('')
        time_box.set('')  
        update_available_times()

    service_box.bind("<<ComboboxSelected>>", update_staff)

    def update_available_times(event=None):
        selected_staff = staff_box.get()
        selected_date = date_box.get()
        if not (selected_staff and selected_date):
            time_box['values'] = time_options
            time_box.set('')
            return

        available_times = [t for t in time_options if not any(
            r["staff"] == selected_staff and r["date"] == selected_date and r["time"] == t and r["status"] not in ("Cancelled","Completed")
            for r in reservations
        )]
        time_box['values'] = available_times
        time_box.set('')
    
    staff_box.bind("<<ComboboxSelected>>", update_available_times)
    date_box.bind("<<ComboboxSelected>>", update_available_times)

    def confirm_booking():
        selected_service = service_box.get()
        selected_staff = staff_box.get()
        selected_date = date_box.get()
        selected_time = time_box.get()

        if not (selected_service and selected_staff and selected_date and selected_time):
            messagebox.showerror("Error", "Please complete all fields.")
            return

        if is_within_schedule(selected_staff, selected_date, selected_time):
            status = "Pending"
        else:
            status = "Pending - Staff Unavailable"
            messagebox.showwarning("Warning", f"{selected_staff} is not scheduled at this time. Booking status is set to '{status}'.")

        reservations.append({
            "customer": username,
            "service": selected_service,
            "staff": selected_staff,
            "date": selected_date,
            "time": selected_time, 
            "status": status
        })
        messagebox.showinfo("Success", f"Booking confirmed for {selected_staff} on {selected_date} at {selected_time}. Status: {status}")
        customer_menu(username)

    tk.Button(root, text="Confirm Booking", font=("Arial", 14, "bold"), bg="pink", fg="black",
              command=confirm_booking).pack(pady=20)
    tk.Button(root, text="Back", font=("Arial", 14, "bold"),
              bg="gray", fg="white", command=lambda: customer_menu(username)).pack(pady=5)

    
def complete_booking(staff, reservation):
    res_date = reservation["date"]

    if not any(s["date"] == res_date for s in staff_schedules.get(staff, [])):
        messagebox.showerror("Error", f"You have no schedule on {res_date}. You cannot complete this booking.")
        return

    reservation["status"] = "Completed"
    messagebox.showinfo("Success", "Booking marked as completed!")


    
def reserve_service(username):
    clear_frame()
    tk.Label(root, text="RESERVE A SERVICE (WITH PAYMENT)",
             font=("Arial Rounded MT Bold", 26), fg="pink", bg="white").pack(pady=20)

    panel = tk.Frame(root, bg="white")
    panel.pack(pady=10)

    tk.Label(panel, text="Select Service:", font=("Arial", 14, "bold"), bg="white").grid(row=0, column=0, sticky="w", pady=5)

    def get_all_services():
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT category, service_name, price FROM staff_specialties")
            result = cursor.fetchall()
            conn.close()
            return [f"{row[0]} - {row[1]} - ₱{row[2]}" for row in result]
        except Exception as e:
            print("Error fetching services:", e)
            return []

    service_names = get_all_services()
    service_box = ttk.Combobox(panel, values=service_names, state="readonly", width=50)
    service_box.grid(row=0, column=1, pady=5)

    tk.Label(panel, text="Price:", font=("Arial", 14, "bold"), bg="white").grid(row=0, column=2, sticky="w", padx=10)
    price_label = tk.Label(panel, text="₱0", font=("Arial", 14), bg="white", fg="green")
    price_label.grid(row=0, column=3, sticky="w")

    tk.Label(panel, text="Select Staff:", font=("Arial", 14, "bold"), bg="white").grid(row=1, column=0, sticky="w", pady=5)
    staff_box = ttk.Combobox(panel, values=[], state="readonly", width=40)
    staff_box.grid(row=1, column=1, pady=5)

    tk.Label(panel, text="Select Date:", font=("Arial", 14, "bold"), bg="white").grid(row=2, column=0, sticky="w", pady=5)
    today = datetime.date.today()
    date_options = [(today + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    date_box = ttk.Combobox(panel, values=date_options, state="readonly", width=40)
    date_box.grid(row=2, column=1, pady=5)

    tk.Label(panel, text="Select Time:", font=("Arial", 14, "bold"), bg="white").grid(row=3, column=0, sticky="w", pady=5)
    time_options = [f"{h:02d}:{m:02d}" for h in range(7, 22) for m in (0, 30)]
    time_box = ttk.Combobox(panel, values=time_options, state="readonly", width=20)
    time_box.grid(row=3, column=1, pady=5)

    def update_staff_and_price(event):
        selected_service = service_box.get()
        if not selected_service:
            staff_box['values'] = []
            staff_box.set('')
            price_label.config(text="₱0")
            return

        parts = selected_service.split(" - ")
        svc_category = parts[0]
        svc_name_only = parts[1]
        price = parts[2] if len(parts) >= 3 else "₱0"
        price_label.config(text=price)

        staff_ids = get_staff_for_service(svc_category, svc_name_only)
        staff_box['values'] = staff_ids
        staff_box.set('')
        if staff_ids:
            staff_box.current(0)

    service_box.bind("<<ComboboxSelected>>", update_staff_and_price)

    def confirm_reservation_inner():
        selected_service = service_box.get()
        selected_staff = staff_box.get()
        selected_date_str = date_box.get()
        selected_time_str = time_box.get()

        if not (selected_service and selected_staff and selected_date_str and selected_time_str):
            messagebox.showerror("Error", "Please complete all fields.")
            return

        try:
            selected_date = datetime.datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format.")
            return

        try:
            selected_time = datetime.datetime.strptime(selected_time_str, "%H:%M").time()
        except ValueError:
            messagebox.showerror("Error", "Invalid time format.")
            return

        parts = selected_service.split(" - ")
        svc_category = parts[0]
        svc_name_only = parts[1]

        service_duration_minutes = services.get(svc_category, {}).get(svc_name_only, {}).get("duration", 60)

        is_available, reason = is_within_schedule(selected_staff, selected_date, selected_time, service_duration_minutes)
        if not is_available:
            messagebox.showerror("Error", reason)
            return

        reservations.append({
            "customer": username,
            "service": selected_service,
            "staff": selected_staff,
            "date": selected_date,
            "time": selected_time,
            "duration": service_duration_minutes,
            "payment_method": "Cash",
            "status": "Pending"
        })

        success = insert_reservation_to_db(
            customer=username,
            staff=selected_staff,
            service=selected_service,
            date=selected_date,
            time=selected_time,
            duration=service_duration_minutes
        )

        if success:
            messagebox.showinfo("Success", "Reservation confirmed and saved!")
            pay_for_service(username, selected_service)
        else:
            messagebox.showerror("Error", "Failed to save reservation to database.")

    tk.Button(root, text="Confirm Reservation", font=("Arial", 14, "bold"), bg="pink", fg="black",
              command=confirm_reservation_inner).pack(pady=20)
    tk.Button(root, text="Back", font=("Arial", 14, "bold"), bg="gray", fg="white",
              command=lambda: customer_menu(username)).pack(pady=5)


def pay_for_service(username, selected_service):
    cat, svc_name, price_str = selected_service.split(" - ")
    
    try:
        price = float(price_str.replace("₱", "").replace(",", "").strip())
    except ValueError:
        price = 0.0

    pay_window = tk.Toplevel(root)
    pay_window.title("Payment")
    pay_window.geometry("400x250")
    pay_window.config(bg="white")

    tk.Label(pay_window, text=f"Payment for {svc_name}", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
    tk.Label(pay_window, text=f"Amount to Pay: ₱{price:.2f}", font=("Arial", 14), bg="white").pack(pady=5)
    tk.Label(pay_window, text="Payment Method: Cash", font=("Arial", 12), bg="white").pack(pady=5)

    tk.Label(pay_window, text="Amount:", font=("Arial", 12), bg="white").pack(pady=5)
    amount_entry = tk.Entry(pay_window, font=("Arial", 12))
    amount_entry.pack(pady=5)
    amount_entry.insert(0, f"{price:.2f}")
    amount_entry.config(state="readonly")
    
    def confirm_payment():
        global customer_balance
        customer_balance[username] = customer_balance.get(username, 0) + price
        messagebox.showinfo("Success", f"Payment of ₱{price:.2f} via Cash successful!")
        pay_window.destroy()
        customer_menu(username)

    tk.Button(pay_window, text="Pay Now", font=("Arial", 12, "bold"), bg="pink", fg="black",
              command=confirm_payment).pack(pady=20)



def cancel_reservation_object(username, reservation):
    confirm = messagebox.askyesno("Confirm", f"Cancel reservation for {reservation['service']} on {reservation['date']}?")
    
    if confirm:
        
        try:
            reservations.remove(reservation)
            messagebox.showinfo("Cancelled", "Your reservation has been cancelled.")
            
            view_reservations_customer(username)
        except ValueError:
            
             messagebox.showerror("Error", "Could not find reservation to cancel.")
            


def reschedule_reservation(username, selected_res):
    
    RESCHEDULE_ALLOWED_STATUSES = ("Pending", "Pending - Staff Unavailable", "Awaiting Payment")
    
    if selected_res.get("status") not in RESCHEDULE_ALLOWED_STATUSES:
        messagebox.showerror("Error", f"Only reservations with status {', '.join(RESCHEDULE_ALLOWED_STATUSES)} can be rescheduled.")
        return

    res_win = tk.Toplevel(root)
    res_win.title("Reschedule Reservation")
    res_win.geometry("400x350")
    res_win.config(bg="white")

    tk.Label(res_win, text="Select New Date:", font=("Arial", 14, "bold"), bg="white").pack(pady=5)
    
    today = dt.date.today()
    date_options = [(today + dt.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    date_box = ttk.Combobox(res_win, values=date_options, font=("Arial", 12), width=30, state="readonly")
    date_box.set(selected_res["date"])
    date_box.pack(pady=5)

    tk.Label(res_win, text="Select New Time:", font=("Arial", 14, "bold"), bg="white").pack(pady=5)
    
    time_options = []
    
    for h in range(9, 18):
        for m in (0, 30):
            time_str_24hr = f"{h:02d}:{m:02d}"
            
            if time_str_24hr == "12:00" or time_str_24hr == "12:30":
                continue 
            
            time_str_12hr = dt.datetime.strptime(time_str_24hr, "%H:%M").strftime("%I:%M %p").lstrip('0')
            time_options.append(time_str_12hr)
            
    time_box = ttk.Combobox(res_win, values=time_options, font=("Arial", 12), width=30, state="readonly")
    
    try:
        current_time_str_24hr = selected_res.get("time").split()[0] 
        current_time_str = dt.datetime.strptime(current_time_str_24hr, "%H:%M").strftime("%I:%M %p").lstrip('0')
    except (ValueError, TypeError, AttributeError):
        current_time_str = "10:00 AM"
    
    time_box.set(current_time_str)
    time_box.pack(pady=5)

    def confirm_reschedule():
        new_date = date_box.get()
        new_time_12hr = time_box.get() 
        
        if not new_date or not new_time_12hr:
            messagebox.showerror("Error", "Please select a new date and time.")
            return
            
        
        try:
            time_obj = dt.datetime.strptime(new_time_12hr, "%I:%M %p")
            new_time_24hr = time_obj.strftime("%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid time format.")
            return
            
       
        service_duration_minutes = selected_res.get("duration", 60)
        
        if "12:00" in new_time_24hr or "12:30" in new_time_24hr:
             messagebox.showerror("Error", "Booking is not allowed. The selected time is within the staff break time (12:00 PM - 1:00 PM).")
             return
             
        
        is_available, reason = is_within_schedule(selected_res['staff'], new_date, new_time_24hr, service_duration_minutes)

        if not is_available:
            messagebox.showerror("Error", reason)
            return
        
        selected_res["date"] = new_date

        selected_res["time"] = new_time_24hr 
        
        if selected_res["status"] == "Pending - Staff Unavailable":
             selected_res["status"] = "Pending"
             
        messagebox.showinfo("Success", f"Reservation rescheduled to {new_date} at {new_time_12hr}. Status: {selected_res['status']}")
        res_win.destroy()
        view_reservations_customer(username) 
        
    tk.Button(res_win, text="Confirm", bg="pink", fg="black", font=("Arial", 12, "bold"),
              command=confirm_reschedule).pack(pady=10)
    tk.Button(res_win, text="Cancel", bg="gray", fg="white", font=("Arial", 12, "bold"),
              command=res_win.destroy).pack()
    

def view_reservations_customer(username):
    clear_frame()
    tk.Label(root, text="YOUR ACTIVE RESERVATIONS", 
             font=("Arial Rounded MT Bold", 26), fg="pink", bg="white").pack(pady=20)
    
    ACTIVE_STATUSES = ("Pending", "Confirmed (Paid)", "Pending - Staff Unavailable", "Awaiting Payment", "Confirmed")
    
    customer_reservations = [r for r in reservations if r["customer"] == username and r.get("status") in ACTIVE_STATUSES]

    if not customer_reservations:
        tk.Label(root, text="You have no active reservations.", bg="white", font=("Arial", 14)).pack(pady=20)
    else:
        
        canvas = tk.Canvas(root, bg="white", highlightthickness=0)
        v_scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        canvas.pack(side="top", fill="both", expand=True, padx=20, pady=10)
        v_scrollbar.pack(side="right", fill="y")
        
        headers = ["Service", "Staff", "Date @ Time", "Status", "Actions"]
        widths = [20, 15, 20, 25, 30] 
        
        header_frame = tk.Frame(scroll_frame, bg="lightgray")
        header_frame.pack(fill="x", padx=10, pady=(5, 0))
        for col, header in enumerate(headers):
             tk.Label(header_frame, text=header, font=("Arial", 10, "bold"), width=widths[col], bg="lightgray").pack(side="left", padx=2, pady=2)
        
        
        for i, res in enumerate(customer_reservations):
            row_frame = tk.Frame(scroll_frame, bg="white", bd=1, relief="groove")
            row_frame.pack(fill="x", padx=10, pady=2)
            
            svc_name_only = res['service'].split(" - ")[1]
            tk.Label(row_frame, text=svc_name_only, width=widths[0], anchor="w", bg="white").pack(side="left", padx=2)
            tk.Label(row_frame, text=res['staff'], width=widths[1], bg="white").pack(side="left", padx=2)
            tk.Label(row_frame, text=f"{res['date']} @ {res.get('time', 'N/A')}", width=widths[2], bg="white").pack(side="left", padx=2)
            
            status_text = res['status']
            if "Pending" in status_text:
                color = "blue"
            elif "Confirmed" in status_text:
                color = "green"
            else:
                color = "gray"
                
            tk.Label(row_frame, text=status_text, width=widths[3], bg="white", fg=color).pack(side="left", padx=2)
            
            action_frame = tk.Frame(row_frame, bg="white")
            action_frame.pack(side="left", fill="y")
            
            current_status = res.get("status", "N/A")
            
            if current_status in ("Pending", "Pending - Staff Unavailable", "Awaiting Payment"):
                
                tk.Button(
                    action_frame, 
                    text="Change Time", 
                    font=("Arial", 8), 
                    bg="#ffcccb", 
                    command=lambda r=res: reschedule_reservation(username, r)
                ).pack(side="left", padx=2)

                tk.Button(
                    action_frame, 
                    text="Cancel", 
                    font=("Arial", 8), 
                    bg="red", 
                    fg="white", 
                    command=lambda r=res: cancel_reservation_object(username, r)
                ).pack(side="left", padx=2)
            
            elif current_status in ("Confirmed (Paid)", "Confirmed"):
                 tk.Label(action_frame, text="Confirmed", font=("Arial", 10), fg="green", bg="white").pack(side="left", padx=5)

    tk.Button(root, text="Back to Menu", command=lambda: customer_menu(username), 
             bg="pink", fg="black", font=("Arial", 14, "bold")).pack(pady=10)
    
    
def view_reservation_history(username):
    clear_frame()
    tk.Label(root, text="RESERVATION HISTORY",
             font=("Arial Rounded MT Bold", 26),
             fg="pink", bg="white").pack(pady=20)

    my_past = [r for r in reservations if r["customer"] == username and r["status"] in ("Completed", "Cancelled")]

    if my_past:
        for r in my_past:
            color = "green" if r["status"] == "Completed" else "red"
            tk.Label(root, text=f"{r['service']} | {r['staff']} | {r['date']} | {r['status']}",
                     font=("Arial", 14), fg=color, bg="white").pack(anchor="w", padx=60)
    else:
        tk.Label(root, text="No past reservations found.",
                 font=("Arial", 16), fg="gray", bg="white").pack()

    tk.Button(root, text="Back", command=lambda: customer_menu(username),
              bg="pink", fg="black", font=("Arial", 16, "bold")).pack(pady=30)

    
def view_reservation_history(username):
    clear_frame()
    tk.Label(root, text="RESERVATION HISTORY",
             font=("Arial Rounded MT Bold", 26),
             fg="pink", bg="white").pack(pady=20)

    my_past = [r for r in reservations if r["customer"] == username and r["status"] in ("Completed", "Cancelled")]

    if my_past:
        for r in my_past:
            color = "green" if r["status"] == "Completed" else "red"
            tk.Label(root, text=f"{r['service']} | {r['staff']} | {r['date']} | {r['status']}",
                     font=("Arial", 14), fg=color, bg="white").pack(anchor="w", padx=60)
    else:
        tk.Label(root, text="No past reservations found.",
                 font=("Arial", 16), fg="gray", bg="white").pack()

    tk.Button(root, text="Back", command=lambda: customer_menu(username),
              bg="pink", fg="black", font=("Arial", 16, "bold")).pack(pady=30)

def customer_rate_staff_panel(root, username, reservation):
    clear_frame()

    tk.Label(root, text="Give a Rating", font=("Arial Rounded MT Bold", 24), fg="pink").pack(pady=20)

    tk.Label(root, text=f"Staff: {reservation['staff']}", font=("Arial", 16)).pack()
    tk.Label(root, text=f"Service: {reservation['service'].split(' - ')[1]}", font=("Arial", 14)).pack(pady=5)

    tk.Label(root, text="Star Rating", font=("Arial", 13)).pack(pady=10)
    
    rating_var = tk.StringVar()
    rating_var.set("5 - Perfect") 
    rating_options = ["1 - Pangit", "2 - Kulang", "3 - Okay", "4 - Maganda", "5 - Perfect"]
    rating_combo = ttk.Combobox(root, values=rating_options, state="readonly", textvariable=rating_var, font=("Arial", 14))
    rating_combo.pack()

    tk.Label(root, text="Comment / Feedback", font=("Arial", 13)).pack(pady=10)
    comment_entry = tk.Text(root, height=4, width=40)
    comment_entry.pack()

    def submit_rating():
        if reservation.get("rating"):
            messagebox.showwarning("Already Rated", "You have already rated this service.")
            return

        try:
            rating_num = int(rating_var.get().split(' - ')[0])
            if not (1 <= rating_num <= 5):
                 raise ValueError
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Please select a valid rating.")
            return

        comment_val = comment_entry.get("1.0", "end").strip()

        reservation["rating"] = rating_num
        reservation["comment"] = comment_val

        res_id = reservation.get("id")
        if res_id:
            success = update_reservation_rating_db(res_id, rating_num, comment_val)
            if success:
                messagebox.showinfo("Success", "Rating submitted and saved to database!")
                load_data_from_db() 
            else:
                messagebox.showerror("Error", "Failed to save rating to database.")
        else:
             messagebox.showerror("Error", "Reservation ID not found!")

        customer_rate_staff_select_panel(root, username)   

    tk.Button(root, text="Submit", bg="pink", fg="black", font=("Arial", 14),
              command=submit_rating).pack(pady=15)

    tk.Button(root, text="Back", bg="pink", fg="black", font=("Arial", 12),
              command=lambda: customer_rate_staff_select_panel(root, username)).pack(pady=5)


def customer_rate_staff_select_panel(root, username):
    clear_frame()

    tk.Label(root, text="Rate a Staff", font=("Arial Rounded MT Bold", 24), fg="pink").pack(pady=20)

    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    completed = [r for r in reservations if r["customer"] == username and r.get("status", "") == "Completed" and not r.get("rating")]

    if not completed:
        tk.Label(scroll_frame, text="Wala ka pang completed services to rate.", font=("Arial", 14)).pack(pady=10, padx=20)
    else:
        for r in completed:
            frame = tk.Frame(scroll_frame, bd=2, relief="groove", padx=10, pady=10)
            frame.pack(fill="x", padx=20, pady=10)

            tk.Label(frame, text=f"Service: {r['service'].split(' - ')[1]}", font=("Arial", 14, "bold")).pack(anchor="w")
            tk.Label(frame, text=f"Staff: {r['staff']}", font=("Arial", 12)).pack(anchor="w")

            tk.Button(
                frame,
                text="Rate This",
                bg="pink",
                fg="black",
                command=lambda res=r: customer_rate_staff_panel(root, username, res)
            ).pack(anchor="e", pady=5)

    tk.Button(root, text="Back", bg="pink", fg="black",
              command=lambda: customer_menu(username)).pack(pady=10)


def view_reservations_customer(username):
    clear_frame()
    tk.Label(root, text="YOUR ACTIVE RESERVATIONS", 
             font=("Arial Rounded MT Bold", 26), fg="pink", bg="white").pack(pady=20)
    
    ACTIVE_STATUSES = ("Pending", "Confirmed (Paid)", "Pending - Staff Unavailable", "Awaiting Payment")
    
    customer_reservations = [r for r in reservations if r["customer"] == username and r["status"] in ACTIVE_STATUSES]

    if not customer_reservations:
        tk.Label(root, text="You have no active reservations.", bg="white", font=("Arial", 14)).pack(pady=20)
    else:
        
        canvas = tk.Canvas(root, bg="white", highlightthickness=0)
        v_scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        canvas.pack(side="top", fill="both", expand=True, padx=20, pady=10)
        v_scrollbar.pack(side="right", fill="y")
        
        headers = ["Service", "Staff", "Date @ Time", "Status", "Actions"]
        widths = [20, 15, 20, 25, 30] 
        
        header_frame = tk.Frame(scroll_frame, bg="lightgray")
        header_frame.pack(fill="x", padx=10, pady=(5, 0))
        for col, header in enumerate(headers):
             tk.Label(header_frame, text=header, font=("Arial", 10, "bold"), width=widths[col], bg="lightgray").pack(side="left", padx=2, pady=2)
        
        
        for i, res in enumerate(customer_reservations):
            row_frame = tk.Frame(scroll_frame, bg="white", bd=1, relief="groove")
            row_frame.pack(fill="x", padx=10, pady=2)
            
            svc_name_only = res['service'].split(" - ")[1]
            tk.Label(row_frame, text=svc_name_only, width=widths[0], anchor="w", bg="white").pack(side="left", padx=2)
            tk.Label(row_frame, text=res['staff'], width=widths[1], bg="white").pack(side="left", padx=2)
            tk.Label(row_frame, text=f"{res['date']} @ {res.get('time', 'N/A')}", width=widths[2], bg="white").pack(side="left", padx=2)
            
            status_text = res['status']
            if "Pending" in status_text:
                color = "blue"
            elif "Confirmed" in status_text:
                color = "green"
            else:
                color = "gray"
                
            tk.Label(row_frame, text=status_text, width=widths[3], bg="white", fg=color).pack(side="left", padx=2)
            
            action_frame = tk.Frame(row_frame, bg="white")
            action_frame.pack(side="left", fill="y")
            
            if res['status'] in ("Pending", "Pending - Staff Unavailable", "Confirmed (Paid)", "Awaiting Payment"):
                
                 tk.Button(action_frame, text="Change Time", bg="yellow", font=("Arial", 8),
                           command=lambda r=res: reschedule_reservation(username, r)).pack(side="left", padx=2)
                 
                 tk.Button(action_frame, text="Cancel", bg="#ffb6c1", fg="black", font=("Arial", 8),
                           command=lambda r=res: cancel_reservation_object(username, r)).pack(side="left", padx=2)
            else:
                 tk.Label(action_frame, text="N/A", font=("Arial", 8), bg="white").pack(side="left", padx=2)


    tk.Button(root, text="Back to Menu", font=("Arial", 14, "bold"), bg="gray", fg="white", command=lambda: customer_menu(username)).pack(pady=20)


main_menu()
root.mainloop()


