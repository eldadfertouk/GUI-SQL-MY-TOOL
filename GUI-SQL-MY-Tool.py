import pyodbc
import tkinter as tk
from tkinter import messagebox
import pandas as pd

# Function to execute SQL statement
def execute_sql():
    """
    Execute SQL statement and display results.
    """
    # Check if connection is established
    if conn is None:
        messagebox.showerror("Error", "Connection to database is not established!")
        return

    # Get SQL statement components from entry widgets
    operation = operation_var.get()
    tables = [table_entry.get()] + [table.get() for table in additional_tables if table.get()]
    columns = columns_entry.get().split(',')
    join_type = join_type_var.get()
    join_conditions = join_conditions_entry.get()
    where_clause = where_entry.get()
    order_by_clause = order_by_entry.get()
    group_by_clause = group_by_entry.get()

    # Construct SQL statement
    sql_statement = f"{operation} {', '.join(columns)} FROM {tables[0]}"

    for i in range(1, len(tables)):
        sql_statement += f" {join_type} {tables[i]} ON {join_conditions}"

    if where_clause:
        sql_statement += f" WHERE {where_clause}"
    if order_by_clause:
        sql_statement += f" ORDER BY {order_by_clause}"
    if group_by_clause:
        sql_statement += f" GROUP BY {group_by_clause}"

    sql_statement += ";"

    # Display SQL statement preview with abort option
    preview_sql = messagebox.askyesno("SQL Preview", f"SQL Statement Preview:\n\n{sql_statement}\n\nDo you want to proceed?")
    if not preview_sql:
        return

    # Execute SQL statement
    try:
        cursor = conn.cursor()
        cursor.execute(sql_statement)

        # Fetch results if any
        rows = cursor.fetchall()
        result_text.delete("1.0", tk.END)
        for row in rows:
            result_text.insert(tk.END, str(row) + '\n')

        # Save results to Excel file
        if save_to_excel_var.get() == 1:
            df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
            df.to_excel("sql_result.xlsx", index=False)
            messagebox.showinfo("Save Successful", "Result saved to 'sql_result.xlsx'")

        cursor.close()
        conn.commit()
    except pyodbc.Error as e:
        messagebox.showerror("Error", f"Error executing SQL statement:\n{e}")

# Function to clear SQL statement
def clear_sql():
    """
    Clear all SQL statement entry fields.
    """
    columns_entry.delete(0, tk.END)
    where_entry.delete(0, tk.END)
    order_by_entry.delete(0, tk.END)
    group_by_entry.delete(0, tk.END)

# Function to establish connection
def connect_to_db():
    """
    Establish connection to the database using provided credentials.
    """
    global conn
    server = server_entry.get()
    database = database_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    # Create a connection string
    connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + \
                        ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password

    # Establish a connection
    try:
        conn = pyodbc.connect(connection_string)
        status_label.config(text="Connected to database", fg="green")

        # Save connection data as default
        save_connection_data(server, database, username, password)
    except pyodbc.Error as e:
        messagebox.showerror("Error", f"Error connecting to SQL Server:\n{e}")
        status_label.config(text="Connection failed", fg="red")

# Function to save connection data as default
def save_connection_data(server, database, username, password):
    """
    Save connection data as default for future use.
    """
    with open("default_connection.txt", "w") as file:
        file.write(f"{server}\n{database}\n{username}\n{password}")

# Function to load default connection data
def load_default_connection():
    """
    Load default connection data from file, if available.
    """
    try:
        with open("default_connection.txt", "r") as file:
            server, database, username, password = file.readlines()
            server_entry.insert(tk.END, server.strip())
            database_entry.insert(tk.END, database.strip())
            username_entry.insert(tk.END, username.strip())
            password_entry.insert(tk.END, password.strip())
    except FileNotFoundError:
        pass

# Create main window
root = tk.Tk()
root.title("SQL Server Management GUI")

# Connection variables
conn = None

# GUI components
server_label = tk.Label(root, text="Server:")
server_label.grid(row=0, column=0, sticky=tk.W)
server_entry = tk.Entry(root)
server_entry.grid(row=0, column=1)

database_label = tk.Label(root, text="Database:")
database_label.grid(row=1, column=0, sticky=tk.W)
database_entry = tk.Entry(root)
database_entry.grid(row=1, column=1)

username_label = tk.Label(root, text="Username:")
username_label.grid(row=2, column=0, sticky=tk.W)
username_entry = tk.Entry(root)
username_entry.grid(row=2, column=1)

password_label = tk.Label(root, text="Password:")
password_label.grid(row=3, column=0, sticky=tk.W)
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=3, column=1)

load_default_connection()

connect_button = tk.Button(root, text="Connect", command=connect_to_db)
connect_button.grid(row=4, column=0, columnspan=2)

status_label = tk.Label(root, text="Not connected", fg="red")
status_label.grid(row=5, column=0, columnspan=2)

instruction_label = tk.Label(root, text="Instructions:\n1. Enter server, database, username, and password.\n2. Click 'Connect' to establish a connection.\n3. Choose the SQL operation and specify table(s), column(s), and other options.\n4. Click 'Execute SQL' to execute the SQL statement.\n5. Use commas to separate multiple columns.")
instruction_label.grid(row=6, column=0, columnspan=2)

operation_label = tk.Label(root, text="Operation:")
operation_label.grid(row=7, column=0, sticky=tk.W)
operation_var = tk.StringVar(root)
operation_var.set("SELECT")  # Default operation
operation_menu = tk.OptionMenu(root, operation_var, "SELECT", "INSERT", "UPDATE", "DELETE")
operation_menu.grid(row=7, column=1)

table_label = tk.Label(root, text="Main Table:")
table_label.grid(row=8, column=0, sticky=tk.W)
table_entry = tk.Entry(root)
table_entry.grid(row=8, column=1)

additional_tables_label = tk.Label(root, text="Additional Tables (Max 3):")
additional_tables_label.grid(row=9, column=0, sticky=tk.W)

additional_tables = []
additional_tables.append(tk.Entry(root))
additional_tables[0].grid(row=9, column=1)

def add_table_entry():
    """
    Add additional table entry field dynamically.
    """
    if len(additional_tables) < 3:
        additional_tables.append(tk.Entry(root))
        additional_tables[-1].grid(row=len(additional_tables) + 8, column=1)
        add_table_button.grid(row=len(additional_tables) + 8, column=2)
    else:
        add_table_button.config(state=tk.DISABLED)

add_table_button = tk.Button(root, text="Add Table", command=lambda: add_table_entry())
add_table_button.grid(row=9, column=2)

columns_label = tk.Label(root, text="Columns:")
columns_label.grid(row=10, column=0, sticky=tk.W)
columns_entry = tk.Entry(root)
columns_entry.grid(row=10, column=1)

join_type_label = tk.Label(root, text="Join Type:")
join_type_label.grid(row=11, column=0, sticky=tk.W)
join_type_var = tk.StringVar(root)
join_type_var.set("INNER JOIN")  # Default join type
join_type_menu = tk.OptionMenu(root, join_type_var, "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN")
join_type_menu.grid(row=11, column=1)

join_conditions_label = tk.Label(root, text="Join Conditions:")
join_conditions_label.grid(row=12, column=0, sticky=tk.W)
join_conditions_entry = tk.Entry(root)
join_conditions_entry.grid(row=12, column=1)

where_label = tk.Label(root, text="WHERE Clause:")
where_label.grid(row=13, column=0, sticky=tk.W)
where_entry = tk.Entry(root)
where_entry.grid(row=13, column=1)

order_by_label = tk.Label(root, text="ORDER BY Clause:")
order_by_label.grid(row=14, column=0, sticky=tk.W)
order_by_entry = tk.Entry(root)
order_by_entry.grid(row=14, column=1)

group_by_label = tk.Label(root, text="GROUP BY Clause:")
group_by_label.grid(row=15, column=0, sticky=tk.W)
group_by_entry = tk.Entry(root)
group_by_entry.grid(row=15, column=1)

execute_button = tk.Button(root, text="Execute SQL", command=execute_sql)
execute_button.grid(row=16, column=0, columnspan=2)

save_to_excel_var = tk.IntVar()
save_to_excel_checkbox = tk.Checkbutton(root, text="Save to Excel", variable=save_to_excel_var)
save_to_excel_checkbox.grid(row=16, column=1, columnspan=2)

clear_button = tk.Button(root, text="Clear SQL", command=clear_sql)
clear_button.grid(row=16, column=2, columnspan=2)

result_label = tk.Label(root, text="SQL Results:")
result_label.grid(row=17, column=0, sticky=tk.W)
result_text = tk.Text(root, height=10, width=50)
result_text.grid(row=17, column=1, columnspan=2)

root.mainloop()
