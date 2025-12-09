import mysql.connector
from tkinter import messagebox

class Database:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="salon_db"
            )
            self.cursor = self.conn.cursor(dictionary=True)
        except Exception as e:
            messagebox.showerror("Database Error", f"Cannot connect to MySQL.\n{e}")

    def add_appointment(self, name, contact, services, staff, start, status):
        sql = """
        INSERT INTO customers (name, contact, services, staff, start_time, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(sql, (name, contact, services, staff, start, status))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_customers(self):
        self.cursor.execute("SELECT * FROM customers ORDER BY start_time DESC")
        return self.cursor.fetchall()

    def update_status(self, ticket, status):
        sql = "UPDATE customers SET status=%s WHERE ticket=%s"
        self.cursor.execute(sql, (status, ticket))
        self.conn.commit()

    def add_waiting(self, name, contact, services, staff, requested_time):
        sql = """
        INSERT INTO waiting_list (name, contact, services, staff, requested_time)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.cursor.execute(sql, (name, contact, services, staff, requested_time))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_waiting_list(self):
        self.cursor.execute("SELECT * FROM waiting_list")
        return self.cursor.fetchall()

    def remove_waiting(self, ticket):
        sql = "DELETE FROM waiting_list WHERE ticket=%s"
        self.cursor.execute(sql, (ticket,))
        self.conn.commit()

    def get_history(self):
        self.cursor.execute("SELECT * FROM customers ORDER BY start_time DESC")
        return self.cursor.fetchall()

    def add_service(self, name, duration):
        sql = "INSERT INTO services (name, duration) VALUES (%s, %s)"
        self.cursor.execute(sql, (name, duration))
        self.conn.commit()

    def get_services(self):
        self.cursor.execute("SELECT * FROM services")
        return self.cursor.fetchall()

    def update_service(self, service_id, name, duration):
        sql = "UPDATE services SET name=%s, duration=%s WHERE id=%s"
        self.cursor.execute(sql, (name, duration, service_id))
        self.conn.commit()

    def delete_service(self, service_id):
        sql = "DELETE FROM services WHERE id=%s"
        self.cursor.execute(sql, (service_id,))
        self.conn.commit()

    def clear_statistics(self):
        self.cursor.execute("DELETE FROM statistics")
        self.conn.commit()

    def add_statistics(self, staff=None, service=None, count=0):
        self.cursor.execute(
            "INSERT INTO statistics (staff, service, count) VALUES (%s, %s, %s)",
            (staff, service, count)
        )
        self.conn.commit()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
