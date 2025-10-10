// Dashboard Management Module
class Dashboard {
    static init() {
        this.renderChart();
        this.setupEventListeners();
    }

    static renderChart() {
        const canvas = document.getElementById('queryChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        // Draw a simple bar chart
        const data = [45, 30, 15, 10]; // Order status, refunds, technical, billing
        const labels = ['Order Status', 'Refunds', 'Technical', 'Billing'];
        const colors = ['#4361ee', '#3a0ca3', '#4cc9f0', '#7209b7'];
        
        const barWidth = 50;
        const barSpacing = 30;
        const startX = 50;
        const startY = 150;
        const maxHeight = 100;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw bars
        for (let i = 0; i < data.length; i++) {
            const barHeight = (data[i] / 50) * maxHeight;
            const x = startX + i * (barWidth + barSpacing);
            const y = startY - barHeight;
            
            ctx.fillStyle = colors[i];
            ctx.fillRect(x, y, barWidth, barHeight);
            
            // Draw label
            ctx.fillStyle = '#333';
            ctx.font = '12px Arial';
            ctx.fillText(labels[i], x, startY + 20);
            
            // Draw value
            ctx.fillText(data[i] + '%', x + 10, y - 5);
        }
        
        // Draw axes
        ctx.beginPath();
        ctx.moveTo(30, 20);
        ctx.lineTo(30, startY);
        ctx.lineTo(400, startY);
        ctx.strokeStyle = '#ccc';
        ctx.stroke();
    }

    static setupEventListeners() {
        // Refresh chart on window resize
        window.addEventListener('resize', () => {
            this.renderChart();
        });
    }

    static updateStats(stats) {
        // Update statistics cards
        const statCards = document.querySelectorAll('.stat-info h3');
        if (statCards.length >= 4 && stats) {
            statCards[0].textContent = stats.totalConversations || '1,247';
            statCards[1].textContent = stats.resolutionRate || '89%';
            statCards[2].textContent = stats.escalations || '137';
            statCards[3].textContent = stats.satisfaction || '4.7/5';
        }
    }
}