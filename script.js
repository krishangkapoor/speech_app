const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'en-US';
recognition.interimResults = false;

// Variable to track if recording is in progress
let isRecording = false;

// Start recording when the button is clicked
document.getElementById('start-recording').addEventListener('click', () => {
    if (!isRecording) {
        recognition.start();
        isRecording = true;
    }
});

// Handle the result event
recognition.addEventListener('result', event => {
    const transcript = event.results[0][0].transcript;
    document.getElementById('transcription').innerText = transcript;
    document.getElementById('transcription-field').value = transcript;
    isRecording = false; // Stop recording after a result is received
    recognition.stop();
});

// Handle the end event
recognition.addEventListener('end', () => {
    isRecording = false; // Ensure recording state is reset when recognition ends
});

// Handle errors
recognition.addEventListener('error', (event) => {
    console.error('Speech recognition error detected: ' + event.error);
    isRecording = false;
    recognition.stop();
});

// Form submission event
document.getElementById('transcription-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const userId = document.getElementById('user_id').value;
    const transcription = document.getElementById('transcription-field').value;

    const response = await fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: userId, transcription: transcription, language: recognition.lang })
    });

    const result = await response.json();
    document.getElementById('response').innerText = result.message || result.error;
});
