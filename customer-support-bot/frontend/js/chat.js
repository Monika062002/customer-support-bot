// Chat Management Module
class Chat {
    static init() {
        this.addMessage("Hello! I'm your AI customer support assistant. How can I help you today?", "bot", true);
    }

    static addMessage(text, sender, showQuickReplies = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        
        if (sender === 'user') {
            messageDiv.classList.add('user-message');
        } else {
            messageDiv.classList.add('bot-message');
        }
        
        messageDiv.innerHTML = text;
        
        // Add timestamp
        const timeDiv = document.createElement('div');
        timeDiv.classList.add('message-time');
        timeDiv.textContent = Helpers.getCurrentTime();
        messageDiv.appendChild(timeDiv);
        
        // Add quick replies for bot messages if needed
        if (sender === 'bot' && showQuickReplies) {
            const nlpResult = NLPProcessor.processMessage(text);
            const quickRepliesDiv = Helpers.createQuickReplies(nlpResult.intent);
            messageDiv.appendChild(quickRepliesDiv);
        }
        
        document.getElementById('chatArea').appendChild(messageDiv);
        document.getElementById('chatArea').scrollTop = document.getElementById('chatArea').scrollHeight;
    }

    static showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('typing-indicator');
        typingDiv.id = 'typingIndicator';
        
        const typingDots = document.createElement('div');
        typingDots.classList.add('typing-dots');
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            typingDots.appendChild(dot);
        }
        
        typingDiv.appendChild(typingDots);
        document.getElementById('chatArea').appendChild(typingDiv);
        document.getElementById('chatArea').scrollTop = document.getElementById('chatArea').scrollHeight;
        
        return typingDiv;
    }

    static removeTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    static sendMessage() {
        const message = document.getElementById('userInput').value.trim();
        
        if (message) {
            this.addMessage(message, 'user');
            document.getElementById('userInput').value = '';
            
            this.processUserMessage(message);
        }
    }

    static processUserMessage(message) {
        const typingIndicator = this.showTypingIndicator();
        
        setTimeout(() => {
            this.removeTypingIndicator();
            
            const nlpResult = NLPProcessor.processMessage(message);
            this.addMessage(nlpResult.response, 'bot', true);
            
            // Handle escalation
            if (nlpResult.intent === 'escalation') {
                setTimeout(() => {
                    const typingIndicator2 = this.showTypingIndicator();
                    setTimeout(() => {
                        this.removeTypingIndicator();
                        this.addMessage("A support agent will be with you shortly. Thank you for your patience.", 'bot');
                    }, 1500);
                }, 1000);
            }
        }, 1500);
    }

    static clearChat() {
        if (confirm("Are you sure you want to clear the chat history?")) {
            document.getElementById('chatArea').innerHTML = '';
            this.init();
        }
    }
}