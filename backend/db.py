# backend/db.py
import psycopg2
from backend.settings import DB_CONFIG

def get_connection():

# Establish a new connection to the PostgreSQL database using configuration from settings.
# psycopg2.connection: A live database connection.

    return psycopg2.connect(**DB_CONFIG)

def initialize_db():

# Initialize the database by creating the 'receipts' table if it does not exist.

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS receipts (
                    id SERIAL PRIMARY KEY,
                    vendor TEXT,
                    date DATE,
                    amount FLOAT,
                    category TEXT,
                    currency VARCHAR(5) DEFAULT 'INR'
                );
            """)
            conn.commit()

def insert_receipt(data: dict) -> int:

# Insert a new receipt entry into the database.

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO receipts (vendor, date, amount, category, currency)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (
        data["vendor"],
        data["date"], 
        data["amount"], 
        data["category"], 
        data.get("currency", "INR")
    ))
    receipt_id = cur.fetchone()[0]
    conn.commit()
    return receipt_id



