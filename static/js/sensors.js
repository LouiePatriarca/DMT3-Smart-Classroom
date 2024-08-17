async function fetchSensorData() {
    const response = await fetch('/sensor_data');
    const data = await response.json();

    document.getElementById('sensor1_temp').innerText = data[1].temperature;
    document.getElementById('sensor1_humidity').innerText = data[1].humidity;

    document.getElementById('sensor2_temp').innerText = data[2].temperature;
    document.getElementById('sensor2_humidity').innerText = data[2].humidity;

    document.getElementById('sensor3_temp').innerText = data[3].temperature;
    document.getElementById('sensor3_humidity').innerText = data[3].humidity;

    document.getElementById('sensor4_temp').innerText = data[4].temperature;
    document.getElementById('sensor4_humidity').innerText = data[4].humidity;
}

setInterval(fetchSensorData, 2000); // Fetch data every 2 seconds
