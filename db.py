# database.py
import mysql.connector
from mysql.connector import Error
from config import Config

def create_connection():
    """Create a database connection"""
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        print("Connection to MySQL DB successful")
        return connection
    except Error as e:
        print(f"The error '{e}' occurred")
        return None

def init_db():
    """Initialize the database with required tables"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        # Create journal_entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                entry_text TEXT NOT NULL,
                sentiment_label VARCHAR(50),
                sentiment_score FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized successfully")