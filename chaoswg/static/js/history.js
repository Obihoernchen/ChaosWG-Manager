var username = $('#username').text()
$.getJSON('/json/user_history/' + username, function(result) {
    // prepare data
    var time = [];
    var points = [];
    var point_sum = 0;
    // reverse the order to be old --> new
    result.reverse()
    result.forEach(function(hist) {
        time.push(hist.time);
        point_sum += hist.points;
        points.push(point_sum);
    });
    var ctx = document.getElementById('historyChart').getContext('2d');
    var chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: time,
            datasets: [{
                label: "Points",
                backgroundColor: 'rgba(51, 122, 183, 0.7)',
                borderColor: 'rgba(51, 122, 183, 1)',
                borderWidth: 1,
                data: points,
                lineTension: 0
            }]
        },
        options: {
            animation: {
                duration: 3000
            },
            legend: {
                display: false
            },
            scales: {
                xAxes: [{
                    type: 'time',
                    time: {
                        unit: 'day'
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    });
});