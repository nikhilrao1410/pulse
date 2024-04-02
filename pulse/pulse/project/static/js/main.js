document.addEventListener('DOMContentLoaded', function () {
    // Create a chart context
    var ctx = document.getElementById('pulseChart').getContext('2d');

    // Initialize the pulse rate chart
    var pulseChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Pulse Rate',
                data: [],
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                fill: false
            }]
        },
        options: {
            scales: {
                x: [{
                    type: 'linear',
                    position: 'bottom'
                }]
            }
        }
    });

    // Fetch pulse rate data and update the chart
    function updatePulseChart() {
        fetch('/get_pulse_rate_data')
            .then(response => response.json())
            .then(data => {
                // Update chart data
                pulseChart.data.labels = data.timestamps;
                pulseChart.data.datasets[0].data = data.pulseRates;
                pulseChart.update();
            })
            .catch(error => {
                console.error('Error fetching pulse rate data:', error);
            });
    }

    // Update pulse chart every second
    setInterval(updatePulseChart, 1000);

    // Fetch heart rate data and update the heart rate display
    function updateHeartRate() {
        fetch('/get_heart_rate')
            .then(response => response.json())
            .then(data => {
                document.getElementById('heart-rate').innerText = `Heart Rate: ${data.bpm.toFixed(2)} BPM`;
            })
            .catch(error => {
                console.error('Error fetching heart rate data:', error);
            });
    }

    // Update heart rate display every second
    setInterval(updateHeartRate, 1000);

    // Get the "Get Started" button element
    var getStartedButton = document.getElementById('getStartedButton');
    
    // Add an event listener to handle the button click
    getStartedButton.addEventListener('click', function(event) {
        // Prevent the default behavior of the button (e.g., form submission)
        event.preventDefault();
        
        // Redirect the user to the heartRate page
        window.location.href = '/heartRate';
    });

    // Function to change the background image of the container
    function changeBackgroundImage(imageUrl) {
        var container = document.querySelector('.container');
        container.style.backgroundImage = `url(${imageUrl})`;
    }

    // Call the function with the URL of the image you want to set as the background
    changeBackgroundImage("{ { url_for('static', filename='images/medic.png') } }");
});
