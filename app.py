import time
from threading import Thread, Event
from flask import Flask, jsonify, render_template, request,send_file
from pymodbus.client import ModbusSerialClient as ModbusClient
from gpio import GPIOController
from database import Database
import socket
from io import StringIO
import csv

esp32_host = "192.168.0.102"  # Replace with your ESP32's IP address
esp8266_host = "192.168.0.103"  # Replace with your ESP8266's IP address
port = 8080  # The port on which ESP32/ESP8266 is listening

app = Flask(__name__)
gpio_controller = GPIOController()
database = Database()
polling_thread = None

sensor_slave_address = 4
sensor_holding_registers_address = 0
sensor_registers_quantity = 2

meter_slave_address = 5
meter_holding_registers_address = 29
meter_registers_quantity = 2

# Sensor data storage
devices_data = {
    'inside': {'temperature': 0, 'humidity': 0},
    'outside': {'temperature': 0, 'humidity': 0},
    'power_consumption' : 0
    }

# Sensor status
sensor_status = {
    f'sensor{i}': "Offline" for i in range(1, 6)
    }

def send_command_to_esp(host, message):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.sendall(message.encode())
    except Exception as e:
        print(f"Error: {e}")

# Modbus client setup
# client = ModbusClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600, timeout=1)
client = ModbusClient(method='rtu', port='COM4', baudrate=9600, timeout=1)

database.update_power_status(0)
message = "temperature:"+str(database.get_temperature())+",power_status:"+str(database.get_power_status())

send_command_to_esp(esp32_host, message)
send_command_to_esp(esp8266_host, message)
gpio_controller.turn_off_ac_units()
gpio_controller.turn_off_e_fans()
gpio_controller.turn_off_blower()
gpio_controller.turn_off_exhaust()

# Event to control the background thread
stop_event = Event()
start_event = Event()

# Function to poll sensors
def poll_sensors():
    while not stop_event.is_set():
        if start_event.is_set():
            poll_temperature_and_humidity_sensors()
            poll_power_consumption()
        time.sleep(10)

# Poll temperature and humidity sensors
def poll_temperature_and_humidity_sensors():
    try:
        inside_temp_sum, inside_humid_sum = 0, 0

        # Polling inside sensors (sensor 1 to 3)
        for sensor_id in range(1, 4):
            if client.connected:
                result = client.read_holding_registers(sensor_holding_registers_address, sensor_registers_quantity, slave=sensor_id)
                if not result.isError():
                    inside_humid_sum += result.registers[0]/10
                    inside_temp_sum += result.registers[1]/10
                    sensor_status[f'sensor{sensor_id}'] = "Online"
                else:
                    sensor_status[f'sensor{sensor_id}'] = "Offline"
            else:
                try:
                    client.connect()
                except Exception as e:
                    print(f"Error: {e}")    
          

        # Get averages and update data
        devices_data['inside']['temperature'] = "{:.2f}".format(inside_temp_sum / 3)
        devices_data['inside']['humidity'] = "{:.2f}".format(inside_humid_sum / 3)

        # Record data in the database
        database.record_data('inside_temperature_records', devices_data['inside']['temperature'])
        database.record_data('inside_humidity_records', devices_data['inside']['humidity'])

        # Polling outside sensor (sensor 4)
        if client.connected:
            result = client.read_holding_registers(sensor_holding_registers_address, sensor_registers_quantity, slave=sensor_slave_address)
        else:
            try:
                client.connect()
            except Exception as e:
                print(f"Error: {e}")    
       
        if not result.isError():
            devices_data['outside']['temperature'] =  "{:.2f}".format(result.registers[1]/10)
            devices_data['outside']['humidity'] =  "{:.2f}".format(result.registers[0]/10)
            sensor_status['sensor4'] = "Online"

            database.record_data('outside_temperature_records', devices_data['outside']['temperature'])
            database.record_data('outside_humidity_records', devices_data['outside']['humidity'])
        else:
            sensor_status['sensor4'] = "Offline"

    except Exception as e:
        print(f"Error polling temperature/humidity sensors: {e}")

# Poll power consumption
def poll_power_consumption():
    try:
        if client.connected:
            result = client.read_holding_registers(meter_holding_registers_address, meter_registers_quantity, slave=meter_slave_address)
            if not result.isError():
                power_value = ((result.registers[0] << 16) | result.registers[1]) / 100
                devices_data['power_consumption'] =  "{:.2f}".format(power_value)
                sensor_status['sensor5'] = "Online"
                database.record_data('power_consumption_records', devices_data['power_consumption'])
            else:
                sensor_status['sensor5'] = "Offline"
        else:
            try:
                client.connect()
            except Exception as e:
                print(f"Error: {e}")
    except Exception as e:
        print(f"Error polling power consumption: {e}")

# Control devices based on sensor data
def control_devices():
    gpio_controller.turn_on_ac_units()
    database.update_power_status(1)
    
    send_command_to_esp(esp8266_host, message)
    gpio_controller.turn_on_e_fans()
    Thread(target = gpio_controller.turn_on_timed_exhaust).start()
    Thread(target = gpio_controller.turn_on_timed_blower).start()
    Thread(target = check_temp_set_point).start()
    time.sleep(3)
    message = "temperature:"+str(database.get_temperature())+",power_status:"+str(database.get_power_status())
    send_command_to_esp(esp32_host, message)
    time.sleep(5)
    send_command_to_esp(esp8266_host, message)

def check_temp_set_point():
    while True:
        try:
            if client.connected:
                result = client.read_holding_registers(sensor_holding_registers_address, sensor_registers_quantity, slave=1)
                if not result.isError() and not stop_event.is_set():
                    if float(result.registers[1]/10) == 24:
                        gpio_controller.turn_off_e_fans()
                    elif float(result.registers[1]/10) == 26:
                        gpio_controller.turn_on_e_fans()
                result2 = client.read_holding_registers(sensor_holding_registers_address, sensor_registers_quantity, slave=4)
                if not result2.isError() and not stop_event.is_set():
                    if float(result2.registers[1]/10) < 28:
                        gpio_controller.turn_on_timed_blower()
                time.sleep(10)
            else:
                try:
                    client.connect()
                except Exception as e:
                    print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

# Manage polling threads
def start_polling_threads():
    global polling_thread
    if polling_thread == None:
        polling_thread = Thread(target=poll_sensors)
        polling_thread.start()

def stop_polling_threads():
    global polling_thread
    stop_event.set()
    if polling_thread is not None and polling_thread.is_alive():  # Check if thread is alive before joining
        polling_thread.join()
    polling_thread = None  # Reset the thread after stopping

# Threads for polling
polling_thread = Thread(target=poll_sensors)

# Flask routes
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/power_consumption_plot')
def power_consumption_plot():
    return render_template('power_consumption_plot.html')

@app.route('/temperature_plot')
def temperature_plot():
    return render_template('temperature_plot.html')

@app.route('/humidity_plot')
def humidity_plot():
    return render_template('humidity_plot.html')

@app.route('/start', methods=['POST'])
def start_polling():
    try:
        client.connect()
    except Exception as e:
        print(f"Error: {e}")
    stop_event.clear()
    start_event.set()
    start_polling_threads()
    Thread(target=control_devices).start()
    return jsonify({'message': 'Polling and control started'}), 200
    

@app.route('/stop', methods=['POST'])
def stop_polling():
    if client.connected:
        client.close()
    start_event.clear()
    stop_polling_threads()
    
    database.update_power_status(0)
    message = "temperature:"+str(database.get_temperature())+",power_status:"+str(database.get_power_status())
    print(message)
    send_command_to_esp(esp32_host, message)
    send_command_to_esp(esp8266_host, message)
    time.sleep(8)
    send_command_to_esp(esp8266_host, message)
    gpio_controller.turn_off_ac_units()
    gpio_controller.turn_off_e_fans()
    gpio_controller.turn_off_blower()
    gpio_controller.turn_off_exhaust()
    return jsonify({'message': 'Polling stopped'}), 200

@app.route('/sensor_status', methods=['GET'])
def get_sensor_status():
    return jsonify(sensor_status)

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/devices_data', methods=['GET'])
def get_devices_data():
    return jsonify(devices_data)

@app.route('/current_ac_temp', methods=['GET'])
def get_current_ac_temp():
    return jsonify(database.get_temperature())

@app.route('/adjust_temperature', methods=['POST'])
def adjust_temperature():
    print(database.get_temperature())
    ac_temperature = database.get_temperature()
    adjustment = request.json.get('adjustment')
    if adjustment == 'up':
        if(ac_temperature != 25):
            ac_temperature += 1
            database.update_temperature(ac_temperature)
            message = "temperature:"+str(database.get_temperature())+",power_status:"+str(database.get_power_status())
            send_command_to_esp(esp32_host, message)
            send_command_to_esp(esp8266_host, message)
    elif adjustment == 'down':
        if(ac_temperature != 19):
            ac_temperature -= 1
            database.update_temperature(ac_temperature)
            message = "temperature:"+str(database.get_temperature())+",power_status:"+str(database.get_power_status())
            send_command_to_esp(esp32_host, message)
            send_command_to_esp(esp8266_host, message)
    return jsonify({'temperature': ac_temperature})

@app.route('/inside_humidity_data', methods=['GET'])
def get_inside_humidity_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    return jsonify(database.fetch_filtered_data('inside_humidity_records', start_date, end_date))

@app.route('/outside_humidity_data', methods=['GET'])
def get_outside_humidity_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    return jsonify(database.fetch_filtered_data('outside_humidity_records', start_date, end_date))

@app.route('/inside_temperature_data', methods=['GET'])
def get_inside_temperature_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    return jsonify(database.fetch_filtered_data('inside_temperature_records', start_date, end_date))

@app.route('/outside_temperature_data', methods=['GET'])
def get_outside_temperature_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    return jsonify(database.fetch_filtered_data('outside_temperature_records', start_date, end_date))

@app.route('/power_consumption_data', methods=['GET'])
def get_power_consumption_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    return jsonify(database.fetch_filtered_data('power_consumption_records', start_date, end_date))

if __name__ == '__main__':
    app.run(debug=True)
