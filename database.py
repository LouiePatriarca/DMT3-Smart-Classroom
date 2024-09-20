import datetime
import sqlite3

class Database:
    def __init__(self):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inside_temperature_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inside_humidity_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            humidity REAL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS outside_temperature_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS outside_humidity_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            humidity REAL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS power_consumption_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            power_consumption REAL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS temperature_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL
        )
        ''')

        conn.commit()
        conn.close()
    
    def get_temperature(self):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT temperature FROM temperature_settings')
        
        rows = cursor.fetchall()
        conn.close()
        return rows[0][0]

    def get_power_status(self):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT power_status FROM power_settings')
        
        rows = cursor.fetchall()
        conn.close()
        return rows[0][0]   

    def record_data(self, table, value):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute(f'INSERT INTO {table} (timestamp, {table.split("_")[1]}) VALUES (CURRENT_TIMESTAMP, ?)', (value,))
        conn.commit()
        conn.close()

    def update_temperature(self, value):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute(f'UPDATE temperature_settings SET temperature=?', (str(value),))
        conn.commit()
        conn.close()
        
    def update_power_status(self, value):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute(f'UPDATE power_settings SET power_status=?', (value,))
        conn.commit()
        conn.close()

    def fetch_filtered_data(self, table, start_date, end_date):
        start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)

        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT timestamp, {table.split("_")[1]} FROM {table} WHERE timestamp BETWEEN ? AND ?', (start_time, end_time))
        
        rows = cursor.fetchall()
        conn.close()

        filtered_data = [{'timestamp': row[0], table.split("_")[1]: row[1]} for row in rows if 7 <= datetime.datetime.fromisoformat(row[0]).hour <= 18]
        return filtered_data
    
    
