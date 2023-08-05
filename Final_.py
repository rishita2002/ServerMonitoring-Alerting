import subprocess
import time
import psycopg2
import pyttsx3


# Configure pyttsx3
engine = pyttsx3.init()


# Function to get PostgreSQL connection details from the user
def get_connection_details():
    #print("Please enter PostgreSQL connection details:")
    #host = input("Host: ")
    host='localhost'
    #port = input("Port: ")
    port=5432
    #database = input("Database: ")
    database='ping'
    #user = input("Username: ")
    user="postgres"
    #password = input("Password: ")
    password='postgres'
    return host, port, database, user, password

# Function to create the database if it doesn't exist
def create_database(host, port, database, user, password):
    try:
        # Connect to the default PostgreSQL server to check if the database exists
        conn_temp = psycopg2.connect(host=host, port=port, database="postgres", user=user, password=password)
        conn_temp.autocommit = True
        cursor_temp = conn_temp.cursor()

        # Check if the database exists
        cursor_temp.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
        database_exists = cursor_temp.fetchone()

        if not database_exists:
            # Create the database
            cursor_temp.execute(f"CREATE DATABASE {database}")
            print(f"Database '{database}' created successfully.")
        else:
            print(f"Database '{database}' already exists. Skipping creation.")

        cursor_temp.close()
        conn_temp.close()
        return database  # Return the created database name
    except Exception as e:
        print("Error:", e)

# Get PostgreSQL connection details from the user
host, port, database, user, password = get_connection_details()

# Create the database if it doesn't exist and get the database name
database = create_database(host, port, database, user, password)

# Establish the connection to PostgreSQL
conn = psycopg2.connect(host=host, port=port, database=database, user=user, password=password)
cursor = conn.cursor()

# Create the tables if they don't exist
create_table_query1 = '''
    CREATE TABLE IF NOT EXISTS ip_status (
        ip_address VARCHAR(15),
        message VARCHAR(255)
    );
'''
create_table_query2 = '''
    CREATE TABLE IF NOT EXISTS ip_list (
        ip_address VARCHAR(15) PRIMARY KEY
    );
'''
cursor.execute(create_table_query1)
cursor.execute(create_table_query2)
conn.commit()

# Function to add an IP address to the ip_list table
'''def add_ip_address(ip_address):
    cursor.execute("INSERT INTO ip_list (ip_address) VALUES (%s) ON CONFLICT DO NOTHING", (ip_address,))
    conn.commit()'''

# Function to add an IP address to the ip_list table
def add_ip_address(ip_address):
    cursor.execute("SELECT 1 FROM ip_list WHERE ip_address = %s", (ip_address,))
    if cursor.fetchone():
        print(f"IP address '{ip_address}' already exists in the database. It cannot be added again.")
    else:
        cursor.execute("INSERT INTO ip_list (ip_address) VALUES (%s) ON CONFLICT DO NOTHING", (ip_address,))
        conn.commit()
        print("IP Added successfully to the database!")

# Function to edit an existing IP address in the ip_list table
'''def edit_ip_address(old_ip_address, new_ip_address):
    cursor.execute("UPDATE ip_list SET ip_address = %s WHERE ip_address = %s", (new_ip_address, old_ip_address))
    conn.commit()'''
def edit_ip_address(old_ip_address, new_ip_address):
    cursor.execute("SELECT 1 FROM ip_list WHERE ip_address = %s", (old_ip_address,))
    if not cursor.fetchone():
        print(f"IP address '{old_ip_address}' does not exist in the database. It cannot be edited.")
    else:
        cursor.execute("SELECT 1 FROM ip_list WHERE ip_address = %s", (new_ip_address,))
        if cursor.fetchone():
            print(f"IP address '{new_ip_address}' already exists in the database. It cannot be used for replacement.")
        else:
            cursor.execute("UPDATE ip_list SET ip_address = %s WHERE ip_address = %s", (new_ip_address, old_ip_address))
            conn.commit()
            print("IP Edited successfully in the database!")

# Function to delete an IP address from the ip_list table
'''def delete_ip_address(ip_addresst):
    cursor.execute("DELETE FROM ip_list WHERE ip_address = %s", (ip_address,))
    conn.commit()'''

def delete_ip_address(ip_address):
    cursor.execute("SELECT 1 FROM ip_list WHERE ip_address = %s", (ip_address,))
    if cursor.fetchone():
        cursor.execute("DELETE FROM ip_list WHERE ip_address = %s", (ip_address,))
        conn.commit()
        print("IP Deleted successfully from the database!")
    else:
        print(f"IP address '{ip_address}' does not exist in the database. It cannot be deleted.")

# Function to show all IP addresses from the ip_list table
def show_ip_addresses():
    cursor.execute("SELECT * FROM ip_list")
    rows=cursor.fetchall()
    return rows


ping_enabled = True  # Variable to control the pinging

while True:

    # Display initial options
    print("Select an option:")
    print("1. Start/Continue pinging (To Stop Press Ctrl+C)")
    print("2. Access other options")
    print("3. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        # Pinging process in an infinite loop
        while True:

            if ping_enabled:
                # Navigate through the table
                select_query = "SELECT * FROM ip_list"
                cursor.execute(select_query)
                rows = cursor.fetchall()   # rows is the list of all ip's in the ip_list db
                #print(rows)

                for row in rows:
                    ip_address = row[0]
                    #message = row[1]
                    # Execute ping command
                    result = subprocess.run(["ping", "-n", "1", ip_address], capture_output=True)

                    # Check ping result
                    
                    if result.returncode == 0:  # Ping success
                        #message = f"IP {ip_address} is running"
                        #print(message)  # Display IP status
                        #message = f"{Fore.GREEN}IP {ip_address} is running{Style.RESET_ALL}"  # Display IP status in green
                        #print(message)\message = f"IP {ip_address} is running"  # Display IP status
                        message = f"IP {ip_address} is running"  # Display IP status
                        print("\033[92m" + message + "\033[0m")

                        #engine.say(message)  # Speak the alert message
                        #engine.runAndWait()  # Wait for the speech to complete

                    else:  # Ping failure
                        #message = f"IP {ip_address} timed out"
                        #print(message)  # Display IP status
                        #message = f"{Fore.RED}IP {ip_address} timed out{Style.RESET_ALL}"  # Display IP status in red
                        #print(message)
                        message = f"IP {ip_address} timed out"  # Display IP status
                        print("\033[91m" + message + "\033[0m")

                        
                        engine.say(message)  # Speak the alert message
                        engine.runAndWait()  # Wait for the speech to complete
                    

                    # Store message in the database
                    cursor.execute("INSERT INTO ip_status (ip_address, message) VALUES (%s, %s)", (ip_address, message))
                    conn.commit()

                    time.sleep(1)

    elif choice == "2":
            while True:

                # Ask for user input to continue, add, edit, delete, or exit
                print("Select an option:")
                print("1. Add IP address")
                print("2. Edit IP address")
                print("3. Delete IP address")
                print("4. Show all existing IP's")
                print("5. Exit")


                choice = input("Enter your choice: ")

        

                if choice == "1":
                    ip_address = input("Enter IP address to add: ")
                    add_ip_address(ip_address)
                    ping_enabled = False



                elif choice == "2":
                    old_ip_address = input("Enter IP address to edit: ")
                    new_ip_address = input("Enter new IP address: ")
                    edit_ip_address(old_ip_address, new_ip_address)
                    ping_enabled = False

                elif choice == "3":
                    ip_address = input("Enter IP address to delete: ")
                    delete_ip_address(ip_address)
                    ping_enabled = False

                elif choice=="4":
                    ips=show_ip_addresses()
                    print(len(ips),"IP's currently present in the database")
                    for ip in ips:
                        print(ip[0])
                    ping_enabled = False
                    
                elif choice == "5":
                    break

                else:
                    print("Invalid choice. Please try again.")


    elif choice == "3":
        break

    else:
        print("Invalid choice. Please try again.")

    ping_enabled=True



# Close the cursor and connection
cursor.close()
conn.close()
