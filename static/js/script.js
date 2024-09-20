let isPolling = localStorage.getItem('isPolling') === 'true' ? true : false;

window.addEventListener('DOMContentLoaded', () => {
    updateSensorStatus();
    // Update the button and UI based on the stored polling state
    if (isPolling) {
        document.getElementById('toggle-polling-btn').textContent = 'Stop';
        document.getElementById('toggle-polling-btn').classList.remove('btn-primary');
        document.getElementById('toggle-polling-btn').classList.add('btn-danger');
        fetch('/current_ac_temp', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('temperature-display').textContent = data + ' °C';
        });
    } else {
        document.getElementById('toggle-polling-btn').textContent = 'Start';
        document.getElementById('toggle-polling-btn').classList.remove('btn-danger');
        document.getElementById('toggle-polling-btn').classList.add('btn-primary');
    }
});

function adjustTemperature(direction, event) {
    event.stopPropagation(); // Prevent the card click event
    fetch('/adjust_temperature', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                adjustment: direction
            })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.temperature) {
                document.getElementById('temperature-display').textContent = '0 °C';
            } else {
                document.getElementById('temperature-display').textContent = data.temperature + ' °C';
            }
        });
}

function openTemperaturePlot() {
    window.location.href = '/temperature_plot'; // Redirect to the plot page
}

function openHumidityPlot() {
    window.location.href = '/humidity_plot'; // Redirect to the plot page
}

function openPowerConsumptionPlot() {
    window.location.href = '/power_consumption_plot'; // Redirect to the plot page
}

function togglePolling() {
    
    if (isPolling) {
        
        fetch('/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('toggle-polling-btn').textContent = 'Start';
                document.getElementById('toggle-polling-btn').classList.remove('btn-danger');
                document.getElementById('toggle-polling-btn').classList.add('btn-primary');
                document.getElementById('sensor1-status').textContent = 'Offline'
                document.getElementById('sensor2-status').textContent = 'Offline'
                document.getElementById('sensor3-status').textContent = 'Offline'
                document.getElementById('sensor4-status').textContent = 'Offline'
                document.getElementById('sensor5-status').textContent = 'Offline'
                document.getElementById('inside_temperature').innerText = '0 °C';
                document.getElementById('inside_humidity').innerText = '0 %';
                document.getElementById('outside_temperature').innerText = '0 °C';
                document.getElementById('outside_humidity').innerText = '0 %';
                document.getElementById('power-consumption-display').innerText = '0 kWh';
                document.getElementById('temperature-display').textContent = '0 °C';
            });
            isPolling = false;
            localStorage.setItem('isPolling', isPolling); // Store the state
    } else {
        fetch('/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('toggle-polling-btn').textContent = 'Stop';
                document.getElementById('toggle-polling-btn').classList.remove('btn-primary');
                document.getElementById('toggle-polling-btn').classList.add('btn-danger');
                
            });
            isPolling = true;
            localStorage.setItem('isPolling', isPolling); // Store the state
        fetch('/current_ac_temp', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('temperature-display').textContent = data + ' °C';
        });
    }
}
// Function to update sensor status
function updateSensorStatus() {
    if (isPolling){
        fetch('/devices_data', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            
            if (document.getElementById('inside_temperature')) {
                document.getElementById('inside_temperature').innerText = data.inside.temperature + ' °C';
            }
            if (document.getElementById('inside_humidity')) {
                document.getElementById('inside_humidity').innerText = data.inside.humidity + ' %';
            }
            if (document.getElementById('outside_temperature')) {
                document.getElementById('outside_temperature').innerText = data.outside.temperature + ' °C';
            }
            if (document.getElementById('outside_humidity')) {
                document.getElementById('outside_humidity').innerText = data.outside.humidity + ' %';
            }
            if (document.getElementById('power-consumption-display')) {
                document.getElementById('power-consumption-display').innerText = data.power_consumption + ' kWh';
            }
        });
       
        fetch('/sensor_status', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('sensor1-status').textContent = `${data.sensor1}`;
            document.getElementById('sensor2-status').textContent = `${data.sensor2}`;
            document.getElementById('sensor3-status').textContent = `${data.sensor3}`;
            document.getElementById('sensor4-status').textContent = `${data.sensor4}`;
            document.getElementById('sensor5-status').textContent = `${data.sensor5}`;
        });
    }
}

// Periodically update sensor status
setInterval(updateSensorStatus, 5000); 
