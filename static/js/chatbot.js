function sendMessage() {
    const message = document.getElementById('user-message').value;
    
    // Display user message in chat
    const chatlogs = document.getElementById('chatlogs');
    chatlogs.innerHTML += `<div class="user-message">${message}</div>`;
    
    // Send message to Flask server via POST request
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `message=${message}`
    })
    .then(response => response.json())
    .then(data => {
        // Display chatbot's response
        chatlogs.innerHTML += `<div class="bot-response">${data.response}</div>`;
        document.getElementById('user-message').value = '';  // Clear input
    });
}
