/* global Chart */
var username = document.getElementById('username').textContent;
fetch('/json/history/' + username)
    .then(response => response.json())
    .then(function(result) {
        // A user who has not done any task yet: the JSON is an empty array,
        // result[0] is undefined and there is nothing to chart - show a hint
        // in place of the canvas instead.
        if (!result.length) {
            var canvas = document.getElementById('historyUserChart');
            var msg = document.createElement('p');
            msg.className = 'text-muted';
            msg.textContent = 'No tasks completed yet.';
            canvas.parentNode.replaceChild(msg, canvas);
            return;
        }
        // Chart.js v4 time scales want {x, y} data points (v2 could also use a
        // labels array). x is the HTTP-date string from the JSON endpoint;
        // chartjs-adapter-moment parses it with moment.
        var data = [];
        var point_sum = 0;
        // reverse the order to be old --> new
        result.reverse();
        // push initial value with 0 points
        data.push({x: result[0].time, y: 0});
        result.forEach(function(hist) {
            point_sum += hist.points;
            data.push({x: hist.time, y: point_sum});
        });
        var ctx = document.getElementById('historyUserChart').getContext('2d');
        window.chart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: "Points",
                    backgroundColor: 'rgba(51, 122, 183, 0.7)',
                    borderColor: 'rgba(51, 122, 183, 1)',
                    data: data,
                    // v3+ renamed the v2 dataset option steppedLine to stepped
                    stepped: true
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
                    // v3+ uses named scale objects (x/y) instead of xAxes/yAxes
                    // arrays; scaleLabel became title
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
        });
    });
