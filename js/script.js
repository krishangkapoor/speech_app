const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'en-US';
recognition.interimResults = false; 
recognition.continuous = true; // Enable continuous recognition

// Variable to track if recording is in progress
let isRecording = false;

// Variable to store the complete transcription
let completeTranscription = '';

// Start recording when the button is clicked
document.getElementById('start-recording').addEventListener('click', () => {
    if (!isRecording) {
        recognition.start();
        isRecording = true;
        completeTranscription = ''; // Reset transcription when starting a new recording
        document.getElementById('transcription').innerText = '';
    }
});

// Handle the result event
recognition.addEventListener('result', event => {
    let interimTranscription = '';

    for (const result of event.results) {
        interimTranscription += result[0].transcript;
    }

    // Append only new transcriptions
    if (!completeTranscription.endsWith(interimTranscription)) {
        completeTranscription += interimTranscription.replace(completeTranscription, '');
    }

    document.getElementById('transcription').innerText = completeTranscription;
    document.getElementById('transcription-field').value = completeTranscription;
});

// Handle the end event
recognition.addEventListener('end', () => {
    isRecording = false; // Ensure recording state is reset when recognition ends
    recognition.stop();
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
