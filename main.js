document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    
    // Configure Marked.js options safely
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    function appendUserMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message user-message';
        msgDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-user"></i></div>
            <div class="message-content">
                <p>${text}</p>
            </div>
        `;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function appendBotMessage(markdownText) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot-message';
        const htmlContent = marked.parse(markdownText);
        
        msgDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="message-content">
                ${htmlContent}
            </div>
        `;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator bot-message';
        indicator.id = 'typing-indicator';
        indicator.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        chatBox.appendChild(indicator);
        indicator.style.display = 'flex';
        chatBox.scrollTop = chatBox.scrollHeight;
        return indicator;
    }

    // Add listeners to suggestion chips
    const chips = document.querySelectorAll('.suggestion-chip');
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            userInput.value = chip.innerText;
            chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        });
    });

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const text = userInput.value.trim();
        if (!text) return;
        
        // Append user message
        appendUserMessage(text);
        userInput.value = '';
        
        // Show typing
        const typingIndicator = showTypingIndicator();
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: text })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            typingIndicator.remove();
            
            if (response.ok) {
                appendBotMessage(data.response);
            } else {
                appendBotMessage(`**Error:** ${data.error || 'Something went wrong.'}`);
            }
        } catch (err) {
            typingIndicator.remove();
            appendBotMessage(`**Error:** Failed to connect to server.`);
            console.error(err);
        }
    });
});
