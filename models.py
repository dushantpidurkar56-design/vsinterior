import psycopg2
from psycopg2.extras import RealDictCursor
import os
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if not DATABASE_URL:
        print("DATABASE_URL environment variable is not set. Please set it to your Supabase PostgreSQL URL in the .env file.")
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if conn is not None:
        try:
            cur = conn.cursor()
            
            # Enquiries table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS enquiries (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    project_details TEXT,
                    start_date TEXT,
                    hear_about TEXT,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Admins table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            cur.close()
        except Exception as e:
            print("DB Init Error:", e)
        finally:
            conn.close()

def create_admin(username, password):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            hashed_pw = generate_password_hash(password)
            cur.execute("INSERT INTO admins (username, password_hash) VALUES (%s, %s)", (username, hashed_pw))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print("Error creating admin:", e)
            return False
        finally:
            conn.close()
    return False

def verify_admin(username, password):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, password_hash FROM admins WHERE username = %s", (username,))
            admin = cur.fetchone()
            cur.close()
            if admin and check_password_hash(admin[1], password):
                return admin[0] # return admin id
        except Exception as e:
            print("Error verifying admin:", e)
        finally:
            conn.close()
    return None

def get_all_enquiries():
    conn = get_db_connection()
    enquiries = []
    if conn:
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT id, name, email, phone, project_details, start_date, hear_about, submitted_at FROM enquiries ORDER BY submitted_at DESC")
            for row in cur.fetchall():
                enquiries.append(dict(row))
            cur.close()
        except Exception as e:
            print("Error fetching enquiries:", e)
        finally:
            conn.close()
    return enquiries

def add_enquiry(name, email, phone, project_details, start_date, hear_about):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO enquiries (name, email, phone, project_details, start_date, hear_about) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, email, phone, project_details, start_date, hear_about)
            )
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print("DB Error:", e)
            return False
        finally:
            conn.close()
    return False
