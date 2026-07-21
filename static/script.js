// Chat functionality
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const suggestionsContainer = document.getElementById('suggestions');

// API endpoint (adjust based on deployment)
const API_URL = window.location.origin + '/api/chat';

// Example suggestions
const exampleQueries = [
    "Schedule a meeting tomorrow at 2pm",
    "What can you help me with?",
    "Create a task to review proposal",
    "Show my calendar for today",
    "Check in a visitor"
];

// Add message to chat
function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const sender = isUser ? 'You' : 'Tammy';
    contentDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show suggestions
function showSuggestions(suggestions) {
    suggestionsContainer.innerHTML = '';

    if (suggestions && suggestions.length > 0) {
        suggestions.forEach(suggestion => {
            const chip = document.createElement('div');
            chip.className = 'suggestion-chip';
            chip.textContent = suggestion;
            chip.onclick = () => {
                chatInput.value = suggestion;
                chatInput.focus();
            };
            suggestionsContainer.appendChild(chip);
        });
    }
}

// Send message
async function sendMessage() {
    const message = chatInput.value.trim();

    if (!message) return;

    // Disable input while processing
    chatInput.disabled = true;
    sendButton.disabled = true;

    // Add user message
    addMessage(message, true);
    chatInput.value = '';
    showLoading();

    try {
        // Call API
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error('API request failed');
        }

        const data = await response.json();

        // Add assistant response
        hideLoading();
        addMessage(data.response, false);

        // Show suggestions
        if (data.suggestions) {
            showSuggestions(data.suggestions);
        }

        // Show intent and confidence (for demo purposes)
        if (data.intent && data.intent !== 'unknown') {
            console.log('Intent:', data.intent, 'Confidence:', data.confidence);
        }

    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        addMessage(
            "I'm having trouble connecting to the server. Please make sure the API is running. " +
            "You can start it with: <code>python -m uvicorn app.main:app --reload</code>",
            false
        );
    } finally {
        // Re-enable input
        chatInput.disabled = false;
        sendButton.disabled = false;
        chatInput.focus();
    }
}

// Event listeners
sendButton.addEventListener('click', sendMessage);

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Show initial suggestions
showSuggestions(exampleQueries);

// Code copy functionality
function copyCode(button) {
    const codeBlock = button.closest('.code-block').querySelector('code');
    const text = codeBlock.textContent;

    navigator.clipboard.writeText(text).then(() => {
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        button.style.background = '#10b981';

        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading animation
function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant';
    loadingDiv.id = 'loading';
    loadingDiv.innerHTML = `
        <div class="message-content">
            <strong>Tammy:</strong> <span class="typing-indicator">●●●</span>
        </div>
    `;
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.remove();
    }
}

console.log('Tammy Chat Interface Loaded');
console.log('API Endpoint:', API_URL);
