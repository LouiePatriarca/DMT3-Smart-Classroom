
async function fetchDevicesData() {
    if (isPolling) {
        try {
            const response = await fetch('/devices_data');
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            
            // Update only the available elements
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
        } catch (error) {
            console.error('Fetch error:', error);
        }
    }
}

setInterval(fetchDevicesData, 1000); // Fetch data every 2 seconds
