# database/db_config.py
import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Use the root user for XAMPP MySQL
            password="",  # Default password for XAMPP MySQL is empty
            database="brgy_profiling_system"  # Your new database name
        )
        if connection.is_connected():
            print("Successfully connected to the database")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
