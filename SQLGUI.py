import tkinter as tk
from tkinter import ttk
import sqlite3
from sqlite3 import Error
import platform

from Tools.scripts.make_ctype import values


class SQLBuilderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Builder")

        # GUI elements
        self.database_var = tk.StringVar()
        self.connection_status = tk.StringVar(value="Disconnected")
        self.connection_label = tk.Label(root, text="Connection Status:")
        self.connection_label.grid(row=0, column=0)
        self.connection_status_label = tk.Label(root, textvariable=self.connection_status)
        self.connection_status_label.grid(row=0, column=1)
        self.status_indicator = tk.Label(root, width=10, height=10, bg="red")
        self.status_indicator.grid(row=0, column=2)

        # Database selection
        self.database_label = ttk.Label(root, text="Database:")
        self.database_label.grid(row=1, column=0)
        self.database_combo = ttk.Combobox(root, textvariable=self.database_var, values=["local", "custom path"])
        self.database_combo.grid(row=1, column=1)

        # Database Path
        self.database_path_label = ttk.Label(root, text="Database Path:")
        self.database_path_label.grid(row=2, column=0)
        self.database_path_entry = ttk.Entry(root)
        self.database_path_entry.grid(row=2, column=1)

        # Table selection
        self.table_label = ttk.Label(root, text="Table:")
        self.table_label.grid(row=3, column=0)
        self.table_entry = ttk.Entry(root, textvariable=tk.StringVar())
        self.table_entry.grid(row=3, column=1)

        # Column selection
        self.column_label = ttk.Label(root, text="Columns:")
        self.column_label.grid(row=4, column=0)
        self.column_entry = ttk.Entry(root, textvariable=tk.StringVar())
        self.column_entry.grid(row=4, column=1)

        # Where clause
        self.where_label = ttk.Label(root, text="Where:")
        self.where_label.grid(row=5, column=0)
        self.where_entry = ttk.Entry(root, textvariable=tk.StringVar())
        self.where_entry.grid(row=5, column=1)

        # Order By clause
        self.order_by_label = ttk.Label(root, text="Order By:")
        self.order_by_label.grid(row=6, column=0)
        self.order_by_entry = ttk.Entry(root, textvariable=tk.StringVar())
        self.order_by_entry.grid(row=6, column=1)

        # Group By clause
        self.group_by_label = ttk.Label(root, text="Group By:")
        self.group_by_label.grid(row=7, column=0)
        self.group_by_entry = ttk.Entry(root, textvariable=tk.StringVar())
        self.group_by_entry.grid(row=7, column=1)

        # SQL Type
        self.sql_type_label = ttk.Label(root, text="SQL Type:")
        self.sql_type_label.grid(row=8, column=0)
        self.sql_type_combo = ttk.Combobox(root, textvariable=tk.StringVar(), values=["SELECT", "UPDATE", "INSERT"])
        self.sql_type_combo.grid(row=8, column=1)

        # Execute button
        self.execute_button = ttk.Button(root, text="Execute", command=self.execute_sql)
        self.execute_button.grid(row=9, columnspan=2)

        # Data preview (GUI)
        self.data_preview_tree = ttk.Treeview(root)
        self.data_preview_tree.grid(row=10, column=0, columnspan=3)

        # Analyze local machine and display in preview
        self.display_system_info()

    def display_system_info(self):

        # Clear existing data preview
        for child in self.data_preview_tree.get_children():
            self.data_preview_tree.delete(child)
        system_info = f"Operating System: {platform.system()}\n" \
                      f"Machine Type: {platform.machine()}\n" \
                      f"Platform Version: {platform.version()}\n"

        self.data_preview_tree.insert("", "end", text="System Information", values=[system_info])

    def connect_to_database(self):
        database = self.database_var.get()
        if database == "local":
            database_path = "ESHBEL.db"  # Change this to your local database file path
        else:
            database_path = self.database_path_entry.get()
        try:
            self.conn = sqlite3.connect(database_path)
            self.cursor = self.conn.cursor()
            self.connection_status.set("Connected")
            self.status_indicator.config(bg="green")
        except Error as e:
            print(f"Error connecting to database: {e}")
            self.connection_status.set("Error")
            self.status_indicator.config(bg="red")

    def execute_sql(self):
        self.connect_to_database()
        if not self.conn:
            return

        table = self.table_entry.get()
        columns = self.column_entry.get()
        where_clause = self.where_entry.get()
        order_by = self.order_by_entry.get()
        group_by = self.group_by_entry.get()
        sql_type = self.sql_type_combo.get()

        if sql_type == "SELECT":
            sql = f"SELECT {columns} FROM {table}"
            if where_clause:
                sql += f" WHERE {where_clause}"
            if group_by:
                sql += f" GROUP BY {group_by}"
            if order_by:
                sql += f" ORDER BY {order_by}"
        elif sql_type == "UPDATE":
            sql = f"UPDATE {table} SET {columns}"
            if where_clause:
                sql += f" WHERE {where_clause}"
        elif sql_type == "INSERT":
            sql = f"INSERT INTO {table} ({columns}) VALUES ({values})"

        print("Executing SQL:", sql)
        try:
            self.cursor.execute(sql)
            if sql_type == "SELECT":
                self.display_results()
            self.conn.commit()
        except Error as e:
            print(f"Error executing SQL statement: {e}")

    def display_results(self):
        # Clear existing data preview
        for child in self.data_preview_tree.get_children():
            self.data_preview_tree.delete(child)

        # Get column names
        columns = [col[0] for col in self.cursor.description]
        self.data_preview_tree["columns"] = columns
        self.data_preview_tree.heading("#0", text="Row")
        for col in columns:
            self.data_preview_tree.heading(col, text=col)

        # Fetch and display data
        rows = self.cursor.fetchall()
        for i, row in enumerate(rows):
            self.data_preview_tree.insert("", "end", text=i+1, values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = SQLBuilderApp(root)
    root.mainloop()
