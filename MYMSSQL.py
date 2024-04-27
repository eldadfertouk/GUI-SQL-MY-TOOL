import pyodbc

# Define the connection parameters
server = 'ELDAD-LAP-HP\ESHBEL'  # Provide the server name
database = 'demo'  # Provide the database name
username = 'tabula'  # Provide your username
password = 'AAAaaa111'  # Provide your password

# Create a connection string
connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + \
                    ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password

# Establish a connection
try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    # Example query
    cursor.execute("SELECT @@version;")
    row = cursor.fetchone()
    print('Microsoft SQL Server version:', row[0])

    # Close cursor and connection
    cursor.close()
    conn.close()

except pyodbc.Error as e:
    print("Error connecting to SQL Server:", e)
