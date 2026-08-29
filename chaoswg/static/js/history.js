/* global Chart */
var config = {
    type: 'scatter',
    data: {
        datasets: []
    },
    options: {
        // Chart.js v3+ renamed the v2 scatter option showLines to showLine
        showLine: true,
        animation: {
            duration: 3000
        },
        scales: {
            // v3+ uses named scale objects (x/y) instead of xAxes/yAxes arrays;
            // scaleLabel became title
            x: {
                type: 'time',
                title: {
                    display: true,
                    text: 'Date'
                },
                time: {
                    unit: 'day',
                    displayFormats: {
                        day: 'DD.MM.YY'
                    }
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Points'
                },
                beginAtZero: true
            }
        }
    }
};

// Chart colors: green, purple, red, orange, blue, yellow, grey
var chartColors = [
    'rgb(75, 192, 192)',
    'rgb(153, 102, 255)',
    'rgb(255, 99, 132)',
    'rgb(255, 159, 64)',
    'rgb(54, 162, 235)',
    'rgb(255, 205, 86)',
    'rgb(201, 203, 207)'
];

fetch('/json/history')
    .then(response => response.json())
    .then(function(result) {
        // prepare data
        var points = [];
        var point_sum = 0;
        for (var user in result) {
            if (result.hasOwnProperty(user)) {
                result[user].forEach(function(hist) {
                    point_sum += hist.points;
                    points.push({
                        x: hist.time,
                        y: point_sum
                    });
                });

                var color = chartColors[config.data.datasets.length % chartColors.length];

                var dataset = {
                    label: user,
                    borderColor: color,
                    backgroundColor: color,
                    data: points,
                    fill: false,
                    // v3+ renamed the v2 dataset option steppedLine to stepped
                    stepped: true
                };
                config.data.datasets.push(dataset);

                // reset for next iteration
                points = [];
                point_sum = 0;
            }
        }

        var ctx = document.getElementById('historyChart').getContext('2d');
        window.chart = new Chart(ctx, config);
    });
