// Main Application Script
document.addEventListener('DOMContentLoaded', function() {
    // Initialize modules
    Chat.init();
    Dashboard.init();
    
    // Event Listeners
    document.getElementById('sendButton').addEventListener('click', Chat.sendMessage);
    
    document.getElementById('userInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            Chat.sendMessage();
        }
    });
    
    // Navigation
    const navLinks = document.querySelectorAll('.nav-links li');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            link.classList.add('active');
            
            const tab = link.getAttribute('data-tab');
            this.handleNavigation(tab);
        });
    });
    
    // Clear chat button
    document.querySelector('.chat-actions button:first-child').addEventListener('click', Chat.clearChat);
    
    // Escalate button
    document.querySelector('.chat-actions button:last-child').addEventListener('click', () => {
        Chat.addMessage("I'd like to speak with a human agent", 'user');
        Chat.processUserMessage("I want to talk to a human agent");
    });
});

function handleNavigation(tab) {
    const dashboard = document.getElementById('dashboard');
    const chatHeader = document.querySelector('.chat-header');
    const chatArea = document.querySelector('.chat-area');
    const inputArea = document.querySelector('.input-area');
    
    if (tab === 'dashboard') {
        dashboard.classList.add('active');
        chatHeader.style.display = 'none';
        chatArea.style.display = 'none';
        inputArea.style.display = 'none';
        Dashboard.renderChart();
    } else {
        dashboard.classList.remove('active');
        chatHeader.style.display = 'flex';
        chatArea.style.display = 'flex';
        inputArea.style.display = 'flex';
    }
}