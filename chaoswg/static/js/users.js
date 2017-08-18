$.getJSON('/json/users', function(result) {
    // prepare data
    var users = [];
    var points = [];
    result.forEach(function(user) {
        users.push(user.username);
        points.push(user.points);
    });

    var ctx = document.getElementById('userChart').getContext('2d');
    var chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: users,
            datasets: [{
                label: "Points",
                backgroundColor: 'rgba(51, 122, 183, 0.7)',
                borderColor: 'rgba(51, 122, 183, 1)',
                data: points
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
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    });
});