import pandas as pd
import io
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os
import json

from models import get_db_connection

def export_to_excel(enquiries):
    df = pd.DataFrame(enquiries)
    # Remove timestamps or format them properly
    if 'submitted_at' in df.columns:
        df['submitted_at'] = pd.to_datetime(df['submitted_at'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
        
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Enquiries')
        
    output.seek(0)
    return output

def import_from_excel(file_stream):
    try:
        df = pd.read_excel(file_stream, engine='openpyxl')
        return _sync_dataframe_to_db(df)
    except Exception as e:
        print("Error importing from excel:", e)
        return False, str(e)

def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Try getting from environment variable first
    gcp_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if gcp_json:
        try:
            creds_dict = json.loads(gcp_json)
            credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            return gspread.authorize(credentials)
        except json.JSONDecodeError:
            print("Error parsing GOOGLE_CREDENTIALS_JSON. Falling back to credentials.json file.")
            
    creds_file = 'credentials.json'
    if not os.path.exists(creds_file):
        raise FileNotFoundError("credentials.json not found and GOOGLE_CREDENTIALS_JSON is not set.")
    
    credentials = Credentials.from_service_account_file(creds_file, scopes=scopes)
    gc = gspread.authorize(credentials)
    return gc

def export_to_gsheets(enquiries, sheet_url_or_id):
    try:
        gc = get_gspread_client()
        # Open by url or id
        try:
            sh = gc.open_by_url(sheet_url_or_id)
        except:
            sh = gc.open_by_key(sheet_url_or_id)
            
        worksheet = sh.sheet1
        
        df = pd.DataFrame(enquiries)
        if 'submitted_at' in df.columns:
            df['submitted_at'] = df['submitted_at'].astype(str)
            
        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        return True, "Successfully exported to Google Sheets"
    except Exception as e:
        print("Error exporting to Google Sheets:", e)
        return False, str(e)

def import_from_gsheets(sheet_url_or_id):
    try:
        gc = get_gspread_client()
        try:
            sh = gc.open_by_url(sheet_url_or_id)
        except:
            sh = gc.open_by_key(sheet_url_or_id)
            
        worksheet = sh.sheet1
        all_values = worksheet.get_all_values()
        
        if not all_values:
            return False, "Sheet is empty"
            
        df = pd.DataFrame(all_values[1:], columns=all_values[0])
        return _sync_dataframe_to_db(df)
    except Exception as e:
        print("Error importing from Google Sheets:", e)
        return False, str(e)

def _sync_dataframe_to_db(df):
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
        
    synced_count = 0
    try:
        cur = conn.cursor()
        
        # Mapping column names flexibly
        col_map = {col.lower().strip(): col for col in df.columns}
        
        name_col = col_map.get('name')
        email_col = col_map.get('email')
        phone_col = col_map.get('phone number', col_map.get('phone'))
        details_col = col_map.get('project description', col_map.get('project_details', col_map.get('details')))
        start_col = col_map.get('project start timeline', col_map.get('start_date', col_map.get('start date')))
        hear_col = col_map.get('source', col_map.get('hear_about', col_map.get('how did you hear about us?')))
        
        if not all([name_col, email_col, phone_col]):
             return False, "Missing required columns: Name, Email, Phone/Phone Number"
             
        for index, row in df.iterrows():
            name = row[name_col] if pd.notna(row[name_col]) else ""
            email = row[email_col] if pd.notna(row[email_col]) else ""
            phone = str(row[phone_col]) if pd.notna(row[phone_col]) else ""
            details = row[details_col] if details_col and pd.notna(row[details_col]) else ""
            start_date = row[start_col] if start_col and pd.notna(row[start_col]) else ""
            hear_about = row[hear_col] if hear_col and pd.notna(row[hear_col]) else ""
            
            # Simple deduplication check based on email and project details
            cur.execute("SELECT id FROM enquiries WHERE email = %s AND name = %s AND phone = %s", (email, name, phone))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO enquiries (name, email, phone, project_details, start_date, hear_about) VALUES (%s, %s, %s, %s, %s, %s)",
                    (name, email, phone, details, start_date, hear_about)
                )
                synced_count += 1
                
        conn.commit()
        cur.close()
        conn.close()
        return True, f"Successfully synced {synced_count} new entries."
    except Exception as e:
        print("Sync Error:", e)
        return False, str(e)
