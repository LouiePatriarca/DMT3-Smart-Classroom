// Function to set the default date
function setDefaultDate() {
    const today = new Date();
    const yesterday = new Date(today); // Create a new date object for yesterday
    yesterday.setDate(today.getDate() - 1); // Subtract 1 day from today's date

    const formattedToday = today.toISOString().slice(0, 10); // Format today's date as 'YYYY-MM-DD'
    const formattedYesterday = yesterday.toISOString().slice(0, 10); // Format yesterday's date as 'YYYY-MM-DD'

    document.getElementById('start-date').value = formattedYesterday; // Set start-date to yesterday
    document.getElementById('end-date').value = formattedToday; // Set end-date to today

    updateHumidityData(formattedYesterday, formattedToday);
}

function updateHumidityData(startDate, endDate) {
    updatePlot('/inside_humidity_data', 'inside-humidity-plot', startDate, endDate);
    updatePlot('/outside_humidity_data', 'outside-humidity-plot', startDate, endDate);
}

// Set the default date and time when the page loads
window.onload = setDefaultDate;

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

    updateHumidityData(startDate, endDate);
});

function updatePlot(url, plotId, startDate, endDate) {
    fetch(`${url}?start_date=${startDate}&end_date=${endDate}`)
        .then(response => response.json())
        .then(data => {
            const timestamps = data.map(record => new Date(record.timestamp));
            const humidity = data.map(record => record.humidity);
            
            const trace = {
                x: timestamps,
                y: humidity,
                mode: 'lines+markers',
                type: 'scatter'
            };

            const layout = {
                title: {
                    text: 'Humidity Data',
                    x: 0, // Align to the left (0 = left, 0.5 = center, 1 = right)
                    xanchor: 'left' // Anchor the title to the left
                },
                xaxis: {
                    title: 'Time'
                },
                yaxis: {
                    title: 'Humidity (%)'
                },
                margin: {
                    l: 50, r: 10, t: 40, b: 40
                }
            };

            Plotly.newPlot(plotId, [trace], layout);
        });
}