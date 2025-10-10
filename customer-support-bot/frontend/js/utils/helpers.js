// Utility functions
class Helpers {
    static getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    static detectIntent(message) {
        message = message.toLowerCase();
        
        for (const [intent, keywords] of Object.entries(INTENT_KEYWORDS)) {
            if (keywords.some(keyword => message.includes(keyword))) {
                return intent;
            }
        }
        return 'default';
    }

    static getRandomResponse(intent) {
        const responseArray = RESPONSES[intent] || RESPONSES.default;
        return responseArray[Math.floor(Math.random() * responseArray.length)];
    }

    static createQuickReplies(intent) {
        const quickRepliesDiv = document.createElement('div');
        quickRepliesDiv.classList.add('quick-replies');
        
        const replies = QUICK_REPLIES[intent] || 
            ["Order Status", "Return Request", "Technical Issue", "Billing Question"];
            
        replies.forEach(reply => {
            const quickReply = document.createElement('div');
            quickReply.classList.add('quick-reply');
            quickReply.textContent = reply;
            quickReply.addEventListener('click', () => {
                document.getElementById('userInput').value = reply;
                Chat.sendMessage();
            });
            quickRepliesDiv.appendChild(quickReply);
        });
        
        return quickRepliesDiv;
    }
}