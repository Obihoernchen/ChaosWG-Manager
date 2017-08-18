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
                time: {
                    unit: 'day',
                    displayFormats: {
                        day: 'DD.MM.YY'
                    }
                }
            }],
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        }
    }
};

$.getJSON('/json/history', function(result) {
    // prepare data
    var points = [];
    var point_sum = 0;
    for (var user in result) {
        // push initial value with 0 points
        points.push({x: result[user][0].time, y: 0});
        result[user].forEach(function(hist) {
            point_sum += hist.points;
            points.push({
                x: hist.time,
                y: point_sum
            });
        });

        var color = '#'+string_to_color(user);
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
    };

    var ctx = document.getElementById('historyChart').getContext('2d');
    var chart = new Chart(ctx, config);
});