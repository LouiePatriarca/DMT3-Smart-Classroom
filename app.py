import datetime
import random
from flask import Flask, jsonify, render_template, request
from pymodbus.client import ModbusSerialClient as ModbusClient
from threading import Thread, Event
import time
import sqlite3

# Flask app setup
app = Flask(__name__)

# Modbus client setup
client = ModbusClient(method='rtu', port='COM3', baudrate=9600, timeout=1)
client.connect()

# Sensor data storage
sensor_data = {
    1: {'inside_temperature': None, 'inside_humidity': None},
    2: {'outside_temperature': None, 'outside_humidity': None},
}

power_consumption_data = {
    1: {'power_consumption': None}
}

ac_temperature = 0

sensor_status = {
    1: {'sensor1': 0},
    2: {'sensor2': 0},
    3: {'sensor3': 0},
    4: {'sensor4': 0},
    5: {'sensor5': 0},
}

def setup_database():
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

    # # Function to generate random temperatures and timestamps
    # def generate_dummy_data(start_date, end_date, num_records):
    #     data = []
    #     current_time = start_date
    #     time_delta = (end_date - start_date) / num_records

    #     for _ in range(num_records):
    #         temperature = round(random.uniform(10, 20), 1)  # Random temperature between 15.0 and 25.0
    #         data.append((current_time, temperature))
    #         current_time += time_delta

    #     return data

    # # Define start and end dates for the dummy data
    # start_date = datetime.datetime.now() - datetime.timedelta(days=30)  # 30 days ago
    # end_date = datetime.datetime.now()
    # num_records = 100  # Number of records to insert

    # # Generate dummy data
    # dummy_data = generate_dummy_data(start_date, end_date, num_records)

    # # Insert the dummy data into the table
    # cursor.executemany('''
    #     INSERT INTO power_consumption_records (timestamp, power_consumption)
    #     VALUES (?, ?)
    # ''', dummy_data)
    
    conn.commit()
    conn.close()

setup_database()

def record_inside_temperature(inside_temperature):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO inside_temperature_records (temperature) VALUES (?)', (inside_temperature,))
    conn.commit()
    conn.close()

def record_inside_humidity(inside_humidity):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO inside_humidity_records (humidity) VALUES (?)', (inside_humidity,))
    conn.commit()
    conn.close()

def record_outside_temperature(outside_temperature):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO outside_temperature_records (temperature) VALUES (?)', (outside_temperature,))
    conn.commit()
    conn.close()

def record_outside_humidity(outside_humidity):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO outside_humidity_records (humidity) VALUES (?)', (outside_humidity,))
    conn.commit()
    conn.close()

def record_power_consumption(power_consumption):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO power_consumption_records (power_consumption) VALUES (?)', (power_consumption,))
    conn.commit()
    conn.close()
# Event to control the background thread
stop_event = Event()
start_event = Event()
def poll_sensors():
    while not stop_event.is_set():
        if start_event.is_set():
            inside_humidity = 0
            inside_temperature = 0
            for sensor_id in range(1, 4):
                try:
                    result = client.read_holding_registers(0, 2, slave=sensor_id)
                    if not result.isError():
                        inside_humidity += result.registers[0]
                        inside_temperature += result.registers[1]
                        if sensor_id == 1:
                            sensor_status[1] = "Online"
                        if sensor_id == 2:
                            sensor_status[2] = "Online"
                        if sensor_id == 3:
                            sensor_status[3] = "Online"
                    else:
                        print(f"Error reading sensor {sensor_id}")
                        if sensor_id == 1:
                            sensor_status[1] = "Offline"
                        if sensor_id == 2:
                            sensor_status[2] = "Offline"
                        if sensor_id == 3:
                            sensor_status[3] = "Offline"
                except Exception as e:
                    print(f"Exception reading sensor {sensor_id}: {e}")

            average_inside_humidity = "{:.2f}".format(inside_humidity / 3)
            average_inside_temperature = "{:.2f}".format(inside_temperature / 3)
            
            record_inside_humidity(average_inside_humidity)
            record_inside_temperature(average_inside_temperature)
            
            sensor_data[1]['inside_humidity'] = average_inside_humidity
            sensor_data[1]['inside_temperature'] = average_inside_temperature
            
            outside_humidity = 0
            outside_temperature = 0
            result1 = client.read_holding_registers(0, 2, slave=4)
            if not result1.isError():
                sensor_data[2]['outside_humidity'] = "{:.2f}".format(result1.registers[0])
                sensor_data[2]['outside_temperature'] = "{:.2f}".format(result1.registers[1])
                outside_humidity = result1.registers[0]
                outside_temperature = result1.registers[1]
                sensor_status[4] = "On"
            else:
                print(f"Error reading sensor {sensor_id}")
                sensor_status[4] = "Off"

            record_outside_humidity(outside_humidity)
            record_outside_temperature(outside_temperature)
            time.sleep(10)

def poll_consumption(): 
    while not stop_event.is_set():
        if start_event.is_set():
            result1 = client.read_holding_registers(29, 2, slave=1)
            if not result1.isError():
                power_consumption_data[1]['power_consumption'] = ((result1.registers[0] << 16) | result1.registers[1]) /100
                record_power_consumption(result1.registers[0])
                sensor_status[5] = "Online"
            else:
                sensor_status[5] = "Offline"
                print(f"Error reading device")
            time.sleep(10)
polling_thread = Thread(target=poll_sensors)
polling_thread1 = Thread(target=poll_consumption)

@app.route('/sensor_status', methods=['GET'])
def get_sensor_status():
 return jsonify(sensor_status)

@app.route('/')
def dashboard():
    return render_template('dashboard.html', temperature=ac_temperature)

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/sensor_data', methods=['GET'])
def get_sensor_data():
    return jsonify(sensor_data)

@app.route('/power_consumption_device_data', methods=['GET'])
def get_power_consumption_device_data():
    return jsonify(power_consumption_data)

@app.route('/adjust_temperature', methods=['POST'])
def adjust_temperature():
    global ac_temperature
    adjustment = request.json.get('adjustment')
    if adjustment == 'up':
        ac_temperature += 1
    elif adjustment == 'down':
        ac_temperature -= 1

    print(ac_temperature)
    return jsonify({'temperature': ac_temperature})

@app.route('/inside_humidity_data', methods=['GET'])
def get_inside_humidity_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    end_time = end_time.replace(hour=23, minute=59, second=59)  # Set the end time to the end of the day
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT timestamp, humidity FROM inside_humidity_records
    WHERE timestamp BETWEEN ? AND ?
    ''', (start_time, end_time))
    
    rows = cursor.fetchall()
    conn.close()

    filtered_data = []
    for row in rows:
        timestamp = datetime.datetime.fromisoformat(row[0])
        if 7 <= timestamp.hour <= 18:
            filtered_data.append({'timestamp': row[0], 'humidity': row[1]})
  
    print(filtered_data)
    return jsonify(filtered_data)

@app.route('/start', methods=['POST'])
def start_polling():
    start_event.set()
    if not polling_thread.is_alive():
        polling_thread.start()
    if not polling_thread1.is_alive():
        polling_thread1.start()
    return jsonify({'message': 'Polling started'}), 200

@app.route('/stop', methods=['POST'])
def stop_polling():
    start_event.clear()
    stop_event.set()
    polling_thread.join()
    polling_thread1.join()
    return jsonify({'message': 'Polling stopped'}), 200

@app.route('/outside_humidity_data', methods=['GET'])
def get_outside_humidity_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    end_time = end_time.replace(hour=23, minute=59, second=59)  # Set the end time to the end of the day

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT timestamp, humidity FROM outside_humidity_records
    WHERE timestamp BETWEEN ? AND ?
    ''', (start_time, end_time))
    
    rows = cursor.fetchall()
    conn.close()
    
    filtered_data = []
    for row in rows:
        timestamp = datetime.datetime.fromisoformat(row[0])
        if 7 <= timestamp.hour <= 18:
            filtered_data.append({'timestamp': row[0], 'humidity': row[1]})
    
    print(filtered_data)
    return jsonify(filtered_data)

@app.route('/inside_temperature_data', methods=['GET'])
def get_inside_temperature_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    end_time = end_time.replace(hour=23, minute=59, second=59)  # Set the end time to the end of the day
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT timestamp, temperature FROM inside_temperature_records
    WHERE timestamp BETWEEN ? AND ?
    ''', (start_time, end_time))
    
    rows = cursor.fetchall()
    conn.close()
    
    filtered_data = []
    for row in rows:
        timestamp = datetime.datetime.fromisoformat(row[0])
        if 7 <= timestamp.hour <= 18:
            filtered_data.append({'timestamp': row[0], 'temperature': row[1]})
    
    print(filtered_data)
    return jsonify(filtered_data)

@app.route('/outside_temperature_data', methods=['GET'])
def get_outside_temperature_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    end_time = end_time.replace(hour=23, minute=59, second=59)  # Set the end time to the end of the day
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT timestamp, temperature FROM outside_temperature_records
    WHERE timestamp BETWEEN ? AND ?
    ''', (start_time, end_time))
    
    rows = cursor.fetchall()
    conn.close()
    
    filtered_data = []
    for row in rows:
        timestamp = datetime.datetime.fromisoformat(row[0])
        if 7 <= timestamp.hour <= 18:
            filtered_data.append({'timestamp': row[0], 'temperature': row[1]})
    
    print(filtered_data)
    return jsonify(filtered_data)

@app.route('/power_consumption_data', methods=['GET'])
def get_power_consumption_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    end_time = end_time.replace(hour=23, minute=59, second=59)  # Set the end time to the end of the day
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT timestamp, power_consumption FROM power_consumption_records
    WHERE timestamp BETWEEN ? AND ?
    ''', (start_time, end_time))
    
    rows = cursor.fetchall()
    conn.close()
    
    filtered_data = []
    for row in rows:
        timestamp = datetime.datetime.fromisoformat(row[0])
        if 7 <= timestamp.hour <= 18:
            filtered_data.append({'timestamp': row[0], 'power_consumption': row[1]})
    
    print(filtered_data)
    return jsonify(filtered_data)

@app.route('/temperature_plot')
def temperature_plot():
    return render_template('temperature_plot.html')

@app.route('/humidity_plot')
def humidity_plot():
    return render_template('humidity_plot.html')

@app.route('/power_consumption_plot')
def power_consumption_plot():
    return render_template('power_consumption_plot.html')

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0')
    except KeyboardInterrupt:
        stop_event.set()
        polling_thread.join()
        client.close()
