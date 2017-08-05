var username = $('#username').text()
$.getJSON('/json/user_history/' + username, function(result) {
    // prepare data
    var time = [];
    var points = [];
    var point_sum = 0;
    result.forEach(function(hist) {
        time.push(hist.time);
        point_sum += hist.points;
        points.push(point_sum);
    });

    var ctx = document.getElementById('userChart').getContext('2d');
    var chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: time,
            datasets: [{
                label: "Points",
                backgroundColor: 'rgba(51, 122, 183, 0.75)',
                borderColor: 'rgba(51, 122, 183, 1)',
                borderWidth: 1,
                fill: true,
                data: points,
            }]
        },
        options: {
            animation: {
                duration: 3000
            },
            legend: {
                display: false
            }
        }
    });
});