// JavaScript code for accessing the webcam and displaying the feed

const videoElement = document.getElementById('webcam');

async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoElement.srcObject = stream;
    } catch (err) {
        console.error('Error accessing the webcam:', err);
    }
}

startWebcam();
