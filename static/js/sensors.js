async function fetchSensorData() {
    try {
        const response = await fetch('/sensor_data');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        // console.log(data); // To check if data is correct

        // Update only the available elements
        if (document.getElementById('inside_temperature')) {
            document.getElementById('inside_temperature').innerText = 'Inside Temperature:  ' + data[1].inside_temperature + '°C';
        }
        if (document.getElementById('inside_humidity')) {
            document.getElementById('inside_humidity').innerText = 'Inside Humidity:    ' + data[1].inside_humidity + '%';
        }
        if (document.getElementById('outside_temperature')) {
            document.getElementById('outside_temperature').innerText = 'Outside Temperature:    ' + data[2].outside_temperature + '°C';
        }
        if (document.getElementById('outside_humidity')) {
            document.getElementById('outside_humidity').innerText = 'Outside Humidity:  ' + data[2].outside_humidity + '%';
        }
    } catch (error) {
        console.error('Fetch error:', error);
    }
}

setInterval(fetchSensorData, 2000); // Fetch data every 2 seconds
