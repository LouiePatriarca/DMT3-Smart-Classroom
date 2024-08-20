async function fetchPowerConsumptionData() {
    try {
        const response = await fetch('/power_consumption_device_data');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        // console.log(data); // To check if data is correct

        // Update only the available elements
        if (document.getElementById('power-consumption-display')) {
            document.getElementById('power-consumption-display').innerText = data[1].power_consumption + ' kWh';
        }
    } catch (error) {
        console.error('Fetch error:', error);
    }
}

setInterval(fetchPowerConsumptionData, 2000); // Fetch data every 2 seconds
