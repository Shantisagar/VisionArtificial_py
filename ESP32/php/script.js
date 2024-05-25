document.getElementById('forwardBtn').addEventListener('click', function() {
    fetch('http://esp32.local/ena_f')
        .then(response => {
            if (response.ok) {
                console.log('Motor set to forward');
            } else {
                console.error('Error setting motor to forward');
            }
        })
        .catch(error => console.error('Fetch error:', error));
});

document.getElementById('reverseBtn').addEventListener('click', function() {
    fetch('http://esp32.local/ena_r')
        .then(response => {
            if (response.ok) {
                console.log('Motor set to reverse');
            } else {
                console.error('Error setting motor to reverse');
            }
        })
        .catch(error => console.error('Fetch error:', error));
});
