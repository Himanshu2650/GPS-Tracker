// let qrCount = 1;

// function showMessage(text, type = 'info') {
//     const msg = document.getElementById('message');
//     msg.className = `alert alert-${type}`;
//     msg.textContent = text;
//     msg.style.display = 'block';
//     setTimeout(() => msg.style.display = 'none', 4000);
// }

// async function getAccurateLocation(timeout = 10000) {
//     return new Promise((resolve, reject) => {
//         if (!navigator.geolocation) {
//             showMessage('GPS not supported.', 'warning');
//             return reject('GPS not supported');
//         }

//         const timer = setTimeout(() => {
//             showMessage('GPS timeout. Try again outdoors.', 'danger');
//             reject('Timeout');
//         }, timeout);

//         navigator.geolocation.getCurrentPosition(
//             async pos => {
//                 clearTimeout(timer);
//                 const lat = pos.coords.latitude;
//                 const lon = pos.coords.longitude;
//                 try {
//                     const response = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`, {
//                         headers: {
//                             'User-Agent': 'QR-WalkTracker-App/1.0'
//                         }
//                     });
//                     const data = await response.json();
//                     resolve({ coords: `${lat}, ${lon}`, address: data.display_name });
//                 } catch (e) {
//                     resolve({ coords: `${lat}, ${lon}`, address: `${lat}, ${lon}` });
//                 }
//             },
//             err => {
//                 clearTimeout(timer);
//                 console.error('GPS error:', err);
//                 showMessage('Unable to get GPS location.', 'danger');
//                 reject(err);
//             },
//             { enableHighAccuracy: true, timeout: timeout, maximumAge: 0 }
//         );
//     });
// }

// async function startWalk() {
//     const res = await fetch('/start', { method: 'POST' });
//     const data = await res.json();
//     if (res.ok && data.status === 'started') {
//         showMessage(`Walk started at: ${data.start_time}`, 'success');
//     } else {
//         showMessage(data.message || 'Failed to start walk.', 'danger');
//     }
// }

// async function scanQR() {
//     try {
//         const html5QrCode = new Html5Qrcode("reader");
//         document.getElementById("reader").style.display = "block";

//         await html5QrCode.start(
//             { facingMode: "environment" },
//             { fps: 10, qrbox: 250 },
//             async (decodedText) => {
//                 await html5QrCode.stop();
//                 document.getElementById("reader").style.display = "none";

//                 const { coords, address } = await getAccurateLocation();
//                 const scan_time = new Date().toLocaleString();

//                 const response = await fetch('/scan', {
//                     method: 'POST',
//                     headers: { 'Content-Type': 'application/json' },
//                     body: JSON.stringify({
//                         scan_time,
//                         gps: coords,
//                         address,
//                         qr_text: decodedText
//                     })
//                 });

//                 const result = await response.json();
//                 if (response.ok && result.status === 'success') {
//                     showMessage(`QR ${qrCount++} scanned.`, 'success');
//                 } else {
//                     showMessage('Failed to save scan.', 'danger');
//                 }
//             }
//         );
//     } catch (err) {
//         console.error('QR scan failed:', err);
//         showMessage('Error during QR scan.', 'danger');
//     }
// }

// async function submitWalk() {
//     const res = await fetch('/submit', { method: 'POST' });
//     const data = await res.json();
//     if (res.ok && data.status === 'submitted') {
//         showMessage('Walk submitted and emailed.', 'success');
//         qrCount = 1;
//     } else {
//         showMessage('Submission failed.', 'danger');
//     }
// }

let watchId = null;
let messageTimeout = null;
let hasStarted = false;

function showMessage(msg, type = "info", duration = 3000) {
    const messageDiv = document.getElementById('message');
    messageDiv.innerHTML = `<div class="alert alert-${type}">${msg}</div>`;

    if (messageTimeout) clearTimeout(messageTimeout);

    messageTimeout = setTimeout(() => {
        messageDiv.innerHTML = '';
    }, duration);
}

function startWalk() {
    if (!navigator.geolocation) {
        showMessage("❌ Geolocation is not supported by this browser.", "danger");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        function (position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            // Save the first position with start_walk
            fetch('/start_walk', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lat: lat, lon: lon })
            })
                .then(res => res.json())
                .then(data => {
                    console.log(data.message);
                    showMessage("✅ Walk started and tracking enabled.", "success");

                    // Now begin live tracking
                    watchId = navigator.geolocation.watchPosition(
                        savePosition,
                        errorCallback,
                        {
                            enableHighAccuracy: true,
                            maximumAge: 0,
                            timeout: 5000
                        }
                    );
                    hasStarted = true;
                })
                .catch(err => {
                    console.error("Failed to start walk:", err);
                    showMessage("❌ Failed to start walk!", "danger");
                });
        },
        errorCallback,
        { enableHighAccuracy: true }
    );
}

function savePosition(position) {
    if (!hasStarted) return;

    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    const timestamp = new Date().toLocaleString();

    fetch('/save_position', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lat: lat, lon: lon, timestamp: timestamp })
    })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.text();
        })
        .then(data => {
            console.log('✅ Position saved:', data);
        })
        .catch(error => {
            console.error('Saving position failed:', error);
            showMessage("❌ Failed to save location!", "danger");
        });
}

function errorCallback(error) {
    let message = '';
    switch (error.code) {
        case error.PERMISSION_DENIED:
            message = "User denied the request for Geolocation.";
            break;
        case error.POSITION_UNAVAILABLE:
            message = "Location information is unavailable.";
            break;
        case error.TIMEOUT:
            message = "The request to get user location timed out.";
            break;
        default:
            message = "An unknown error occurred.";
            break;
    }
    showMessage(`❌ ${message}`, "danger");
}

// function stopWalk() {
//     if (watchId !== null) {
//         navigator.geolocation.clearWatch(watchId);
//         watchId = null;
//         hasStarted = false;
//     }

//     fetch('/submit_walk', { method: 'POST' })
//         .then(response => {
//             if (!response.ok) throw new Error('Network response was not ok');
//             return response.text();
//         })
//         .then(data => {
//             showMessage("✅ Walk route map generated! Opening map...", "success");
            
//         })
//         .catch(error => {
//             console.error('Generating walk map failed:', error);
//             showMessage("❌ Failed to generate walk map.", "danger");
//         });

function stopWalk() {
    if (watchId !== null) {
        navigator.geolocation.clearWatch(watchId);
        watchId = null;
        hasStarted = false;
    }

    fetch('/submit_walk', { method: 'POST' })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.text();
        })
        .then(data => {
            // ✅ Message only — no map opened
            showMessage("✅ Walk route map generated and emailed successfully!", "success");
        })
        .catch(error => {
            console.error('Generating walk map failed:', error);
            showMessage("❌ Failed to generate walk map.", "danger");
        });
}

