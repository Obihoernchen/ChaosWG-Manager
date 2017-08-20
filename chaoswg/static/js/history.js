/* global $ */
/* global Chart */
var config = {
    type: 'scatter',
    data: {
        datasets: []
    },
    options: {
        animation: {
            duration: 3000
        },
        scales: {
            xAxes: [{
                type: 'time',
                scaleLabel: {
                    display: true,
                    labelString: 'Date'
                },
                time: {
                    unit: 'day',
                    displayFormats: {
                        day: 'DD.MM.YY'
                    }
                }
            }],
            yAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: 'Points'
                },
                ticks: {
                    beginAtZero: true
                }
            }]
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

$.getJSON('/json/history', function(result) {
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
                steppedLine: true
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