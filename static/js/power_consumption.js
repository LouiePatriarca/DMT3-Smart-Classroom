// Function to set the default date
function setDefaultDate() {
    const startDateElement = document.getElementById('start-date');
    const endDateElement = document.getElementById('end-date');

    if (!startDateElement || !endDateElement) {
        console.error('start-date or end-date element not found');
        return; // Exit the function if elements are not found
    }

    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);

    const formattedToday = today.toISOString().slice(0, 10);
    const formattedYesterday = yesterday.toISOString().slice(0, 10);

    startDateElement.value = formattedYesterday;
    endDateElement.value = formattedToday;

    updatePowerConsumptionData(formattedYesterday, formattedToday);
}

function updatePowerConsumptionData(startDate, endDate) {
    updatePlot('/power_consumption_data', 'power-consumption-plot', startDate, endDate);
}

// Set the default date and time when the page loads
window.onload = function() {
    setDefaultDate();

    document.getElementById('update-button').addEventListener('click', function() {
        let startDate = document.getElementById('start-date').value;
        let endDate = document.getElementById('end-date').value;
    
        if (!startDate) {
            startDate = new Date().toISOString().slice(0, 10);
            document.getElementById('start-date').value = startDate;
        }
        if (!endDate) {
            endDate = new Date().toISOString().slice(0, 10);
            document.getElementById('end-date').value = endDate;
        }
    
        updatePowerConsumptionData(startDate, endDate);
    });
};


function updatePlot(url, plotId, startDate, endDate) {
    fetch(`${url}?start_date=${startDate}&end_date=${endDate}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            const timestamps = data.map(record => new Date(record.timestamp));
            const power_consumption = data.map(record => record.consumption);
            const trace = {
                x: timestamps,
                y: power_consumption,
                mode: 'lines+markers',
                type: 'scatter'
            };

            const layout = {
                title: {
                    text: 'Power Consumption Data',
                    x: 0, // Align to the left (0 = left, 0.5 = center, 1 = right)
                    xanchor: 'left' // Anchor the title to the left
                },
                xaxis: {
                    title: 'Time'
                },
                yaxis: {
                    title: 'Power Consumption (kWh)'
                },
                margin: {
                    l: 50, r: 50, t: 50, b: 50
                }
            };

            Plotly.newPlot(plotId, [trace], layout);
        });
}
