import datetime
from flask import Flask, jsonify, render_template, request
from pymodbus.client import ModbusSerialClient as ModbusClient
from threading import Thread, Event
import time
import sqlite3

# Flask app setup
app = Flask(__name__)

# Modbus client setup
client = ModbusClient(method='rtu', port='COM2', baudrate=9600, timeout=1)
client.connect()

# Sensor data storage
sensor_data = {
    1: {'inside_temperature': None, 'humidity': None},
    2: {'outside_temperature': None, 'humidity': None},
    3: {'inside_temperature': None, 'humidity': None},
    4: {'inside_temperature': None, 'humidity': None}
}

ac_temperature = 0

def setup_database():
    conn = sqlite3.connect('temperature_data.db')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS temperature_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL
    )
    ''')
    
    conn.commit()
    conn.close()

setup_database()

def record_temperature(temp):
    conn = sqlite3.connect('temperature_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO temperature_records (temperature) VALUES (?)', (temp,))
    conn.commit()
    conn.close()

# Event to stop the background thread
stop_event = Event()

def poll_sensors():
    while not stop_event.is_set():
        for sensor_id in range(1, 5):  # Assuming 4 sensors
            try:
                result = client.read_holding_registers(0, 2, slave=sensor_id)
                if not result.isError():
                    sensor_data[sensor_id]['humidity'] = result.registers[0]
                    if result.registers[1] == 0:
                        sensor_data[sensor_id]['inside_temperature'] = 0
                    else:
                        sensor_data[sensor_id]['inside_temperature'] = result.registers[1]
                        record_temperature(result.registers[1])
                else:
                    print(f"Error reading sensor {sensor_id}")
            except Exception as e:
                print(f"Exception reading sensor {sensor_id}: {e}")
        time.sleep(2)  # Poll every 2 seconds

# Start polling thread
polling_thread = Thread(target=poll_sensors)
polling_thread.start()

@app.route('/')
def dashboard():
    return render_template('dashboard.html', temperature=ac_temperature)

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/sensor_data', methods=['GET'])
def get_sensor_data():
    return jsonify(sensor_data)

@app.route('/stop', methods=['POST'])
def stop_polling():
    stop_event.set()
    polling_thread.join()
    return jsonify({'message': 'Polling stopped'}), 200

@app.route('/adjust_temperature', methods=['POST'])
def adjust_temperature():
    global ac_temperature
    adjustment = request.json.get('adjustment')
    if adjustment == 'up':
        ac_temperature += 1
    elif adjustment == 'down':
        ac_temperature -= 1
    return jsonify({'temperature': ac_temperature})

@app.route('/temperature_data', methods=['GET'])
def get_temperature_data():
    start_time = datetime.datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
    end_time = datetime.datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
    
    conn = sqlite3.connect('temperature_data.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT timestamp, temperature FROM temperature_records
    WHERE timestamp BETWEEN ? AND ?
    ''', (start_time, end_time))
    
    rows = cursor.fetchall()
    conn.close()
    
    data = [{'timestamp': row[0], 'temperature': row[1]} for row in rows]
    return jsonify(data)

@app.route('/temperature_plot')
def temperature_plot():
    return render_template('temperature_plot.html')

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0')
    except KeyboardInterrupt:
        stop_event.set()
        polling_thread.join()
        client.close()
