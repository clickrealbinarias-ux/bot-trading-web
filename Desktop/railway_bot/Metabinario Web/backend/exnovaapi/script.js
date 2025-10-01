// Metabinario - Bot de Copytrading JavaScript

// Global variables
let countdownInterval;
let isLoggedIn = false;
let currentUser = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeCountdown();
    initializeEventListeners();
    checkAuthStatus();
});

// Countdown functionality
function initializeCountdown() {
    // Set target date (example: 30 days from now)
    const targetDate = new Date();
    targetDate.setDate(targetDate.getDate() + 30);
    
    countdownInterval = setInterval(() => {
        updateCountdown(targetDate);
    }, 1000);
    
    // Initial update
    updateCountdown(targetDate);
}

function updateCountdown(targetDate) {
    const now = new Date().getTime();
    const distance = targetDate.getTime() - now;
    
    if (distance < 0) {
        clearInterval(countdownInterval);
        document.getElementById('days').innerHTML = '00';
        document.getElementById('hours').innerHTML = '00';
        document.getElementById('minutes').innerHTML = '00';
        document.getElementById('seconds').innerHTML = '00';
        return;
    }
    
    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);
    
    document.getElementById('days').innerHTML = days.toString().padStart(2, '0');
    document.getElementById('hours').innerHTML = hours.toString().padStart(2, '0');
    document.getElementById('minutes').innerHTML = minutes.toString().padStart(2, '0');
    document.getElementById('seconds').innerHTML = seconds.toString().padStart(2, '0');
}

// Event listeners
function initializeEventListeners() {
    // Login form
    const loginForm = document.querySelector('.login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Register form
    const registerForm = document.querySelector('.register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // Video placeholder click
    const videoPlaceholder = document.querySelector('.video-placeholder');
    if (videoPlaceholder) {
        videoPlaceholder.addEventListener('click', playDemoVideo);
    }
    
    // Smooth scrolling for navigation links
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
}

// Modal functions
function showLogin() {
    document.getElementById('loginModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function showRegister() {
    document.getElementById('registerModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Close modals when clicking outside
window.addEventListener('click', function(event) {
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    
    if (event.target === loginModal) {
        closeModal('loginModal');
    }
    if (event.target === registerModal) {
        closeModal('registerModal');
    }
});

// Authentication functions
function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const remember = document.querySelector('input[name="remember"]').checked;
    
    console.log('Login attempt:', email, password);
    
    // Show loading state
    const submitBtn = e.target.querySelector('.btn-login-submit');
    submitBtn.classList.add('loading');
    
    // Simulate API call
    setTimeout(() => {
        if (validateLogin(email, password)) {
            // Successful login
            currentUser = {
                email: email,
                name: email.split('@')[0],
                plan: 'profesional'
            };
            isLoggedIn = true;
            
            // Save to localStorage if remember is checked
            if (remember) {
                localStorage.setItem('metabinario_user', JSON.stringify(currentUser));
            }
            
            closeModal('loginModal');
            showSuccessMessage('¡Bienvenido a Metabinario!');
            updateUIForLoggedInUser();
        } else {
            // Login failed
            showErrorMessage('Credenciales incorrectas. Inténtalo de nuevo.');
            submitBtn.classList.remove('loading');
        }
    }, 1000); // Reduced timeout for faster response
}

function handleRegister(e) {
    e.preventDefault();
    
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const confirmPassword = document.getElementById('reg-confirm-password').value;
    const terms = document.querySelector('input[name="terms"]').checked;
    
    // Validation
    if (!validateRegistration(name, email, password, confirmPassword, terms)) {
        return;
    }
    
    // Show loading state
    const submitBtn = e.target.querySelector('.btn-register-submit');
    submitBtn.classList.add('loading');
    
    // Simulate API call
    setTimeout(() => {
        // Successful registration
        currentUser = {
            name: name,
            email: email,
            plan: 'basico'
        };
        isLoggedIn = true;
        
        // Save to localStorage
        localStorage.setItem('metabinario_user', JSON.stringify(currentUser));
        
        closeModal('registerModal');
        showSuccessMessage('¡Cuenta creada exitosamente! Bienvenido a Metabinario.');
        updateUIForLoggedInUser();
    }, 2000);
}

function validateLogin(email, password) {
    // Simple validation - in real app, this would be server-side
    const validUsers = [
        { email: 'demo@metabinario.com', password: 'demo123' },
        { email: 'test@metabinario.com', password: 'test123' }
    ];
    
    console.log('Validating login:', email, password);
    const isValid = validUsers.some(user => user.email === email && user.password === password);
    console.log('Login validation result:', isValid);
    
    return isValid;
}

function validateRegistration(name, email, password, confirmPassword, terms) {
    if (!name || name.length < 2) {
        showErrorMessage('El nombre debe tener al menos 2 caracteres.');
        return false;
    }
    
    if (!isValidEmail(email)) {
        showErrorMessage('Por favor, introduce un email válido.');
        return false;
    }
    
    if (password.length < 6) {
        showErrorMessage('La contraseña debe tener al menos 6 caracteres.');
        return false;
    }
    
    if (password !== confirmPassword) {
        showErrorMessage('Las contraseñas no coinciden.');
        return false;
    }
    
    if (!terms) {
        showErrorMessage('Debes aceptar los términos y condiciones.');
        return false;
    }
    
    return true;
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function checkAuthStatus() {
    const savedUser = localStorage.getItem('metabinario_user');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        isLoggedIn = true;
        updateUIForLoggedInUser();
    }
}

function updateUIForLoggedInUser() {
    // Update navigation
    const navButtons = document.querySelector('.nav-buttons');
    if (navButtons && currentUser) {
        navButtons.innerHTML = `
            <div class="user-info">
                <span>Hola, ${currentUser.name}</span>
                <button class="btn-logout" onclick="logout()">Cerrar Sesión</button>
            </div>
        `;
    }
    
    // Show copytrading dashboard
    if (isLoggedIn) {
        showCopytradingDashboard();
        initializeCopytradingData();
    }
}

function showCopytradingDashboard() {
    // Hide main sections
    document.querySelector('.hero').style.display = 'none';
    document.querySelector('.copytrading-section').style.display = 'none';
    document.querySelector('.features-section').style.display = 'none';
    document.querySelector('.pricing-section').style.display = 'none';
    
    // Show copytrading dashboard
    document.getElementById('copytrading-dashboard').style.display = 'block';
    
    // Scroll to top
    window.scrollTo(0, 0);
}

function logout() {
    isLoggedIn = false;
    currentUser = null;
    localStorage.removeItem('metabinario_user');
    
    // Reset navigation
    const navButtons = document.querySelector('.nav-buttons');
    if (navButtons) {
        navButtons.innerHTML = `
            <button class="btn-login" onclick="showLogin()">Iniciar Sesión</button>
            <button class="btn-register" onclick="showRegister()">Registrarse</button>
        `;
    }
    
    // Hide copytrading dashboard and show main sections
    document.getElementById('copytrading-dashboard').style.display = 'none';
    document.querySelector('.hero').style.display = 'flex';
    document.querySelector('.copytrading-section').style.display = 'block';
    document.querySelector('.features-section').style.display = 'block';
    document.querySelector('.pricing-section').style.display = 'block';
    
    // Stop bot if running
    if (copytradingBot && copytradingBot.isRunning) {
        copytradingBot.stop();
    }
    
    showSuccessMessage('Sesión cerrada exitosamente.');
}

// Plan selection
function selectPlan(plan) {
    if (!isLoggedIn) {
        showRegister();
        return;
    }
    
    // Update user plan
    if (currentUser) {
        currentUser.plan = plan;
        localStorage.setItem('metabinario_user', JSON.stringify(currentUser));
    }
    
    showSuccessMessage(`Plan ${plan.charAt(0).toUpperCase() + plan.slice(1)} seleccionado exitosamente.`);
}

// Video functionality
function playDemoVideo() {
    // In a real implementation, this would load an actual video
    showSuccessMessage('Reproduciendo video de demostración...');
    
    // Simulate video loading
    const videoPlaceholder = document.querySelector('.video-placeholder');
    if (videoPlaceholder) {
        videoPlaceholder.innerHTML = `
            <div class="video-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Cargando video...</p>
            </div>
        `;
        
        setTimeout(() => {
            videoPlaceholder.innerHTML = `
                <i class="fas fa-play-circle"></i>
                <p>Video de demostración</p>
            `;
        }, 3000);
    }
}

// Message functions
function showSuccessMessage(message) {
    showMessage(message, 'success');
}

function showErrorMessage(message) {
    showMessage(message, 'error');
}

function showMessage(message, type) {
    // Remove existing messages
    const existingMessage = document.querySelector('.message-toast');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-toast ${type}`;
    messageDiv.innerHTML = `
        <div class="message-content">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#00d4ff' : '#ff6b6b'};
        color: ${type === 'success' ? '#000' : '#fff'};
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
        z-index: 3000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;
    
    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        .message-content {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(messageDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => {
                messageDiv.remove();
            }, 300);
        }
    }, 5000);
}

// Copytrading Bot Functions
class CopytradingBot {
    constructor() {
        this.isRunning = false;
        this.traders = [];
        this.positions = [];
        this.balance = 10000; // Starting balance
        this.settings = {
            maxRisk: 0.02, // 2% max risk per trade
            maxTrades: 10,
            stopLoss: 0.02, // 2% stop loss
            takeProfit: 0.04 // 4% take profit
        };
    }
    
    start() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        this.showBotStatus('Bot iniciado correctamente');
        this.simulateTrading();
    }
    
    stop() {
        this.isRunning = false;
        this.showBotStatus('Bot detenido');
    }
    
    simulateTrading() {
        if (!this.isRunning) return;
        
        // Simulate random trading activity
        const shouldTrade = Math.random() > 0.7; // 30% chance of trading
        
        if (shouldTrade) {
            this.executeTrade();
        }
        
        // Continue simulation
        setTimeout(() => this.simulateTrading(), 5000 + Math.random() * 10000);
    }
    
    executeTrade() {
        const symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD'];
        const symbol = symbols[Math.floor(Math.random() * symbols.length)];
        const type = Math.random() > 0.5 ? 'BUY' : 'SELL';
        const amount = this.calculatePositionSize();
        const price = this.getCurrentPrice(symbol);
        
        const trade = {
            id: Date.now(),
            symbol: symbol,
            type: type,
            amount: amount,
            price: price,
            timestamp: new Date(),
            status: 'OPEN'
        };
        
        this.positions.push(trade);
        this.updateDashboard();
        this.showBotStatus(`Nueva operación: ${type} ${symbol} - $${amount}`);
    }
    
    calculatePositionSize() {
        const riskAmount = this.balance * this.settings.maxRisk;
        return Math.floor(riskAmount / 100); // Simplified calculation
    }
    
    getCurrentPrice(symbol) {
        // Simulate price data
        const basePrice = {
            'EURUSD': 1.0850,
            'GBPUSD': 1.2650,
            'USDJPY': 150.00,
            'AUDUSD': 0.6550,
            'USDCAD': 1.3650
        };
        
        const variation = (Math.random() - 0.5) * 0.01; // ±0.5% variation
        return basePrice[symbol] * (1 + variation);
    }
    
    updateDashboard() {
        // Update dashboard with current positions and balance
        const dashboard = document.getElementById('tradingDashboard');
        if (dashboard) {
            dashboard.innerHTML = this.generateDashboardHTML();
        }
    }
    
    generateDashboardHTML() {
        const openPositions = this.positions.filter(p => p.status === 'OPEN');
        const totalValue = this.balance + this.calculateUnrealizedPnL();
        
        return `
            <div class="dashboard-stats">
                <div class="stat-card">
                    <h3>Balance Total</h3>
                    <p class="stat-value">$${totalValue.toFixed(2)}</p>
                </div>
                <div class="stat-card">
                    <h3>Posiciones Abiertas</h3>
                    <p class="stat-value">${openPositions.length}</p>
                </div>
                <div class="stat-card">
                    <h3>P&L del Día</h3>
                    <p class="stat-value ${this.calculateDailyPnL() >= 0 ? 'positive' : 'negative'}">
                        ${this.calculateDailyPnL() >= 0 ? '+' : ''}$${this.calculateDailyPnL().toFixed(2)}
                    </p>
                </div>
            </div>
            <div class="positions-table">
                <h3>Posiciones Activas</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Símbolo</th>
                            <th>Tipo</th>
                            <th>Cantidad</th>
                            <th>Precio</th>
                            <th>P&L</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${openPositions.map(pos => `
                            <tr>
                                <td>${pos.symbol}</td>
                                <td class="${pos.type.toLowerCase()}">${pos.type}</td>
                                <td>$${pos.amount}</td>
                                <td>${pos.price.toFixed(4)}</td>
                                <td class="${this.calculatePositionPnL(pos) >= 0 ? 'positive' : 'negative'}">
                                    ${this.calculatePositionPnL(pos) >= 0 ? '+' : ''}$${this.calculatePositionPnL(pos).toFixed(2)}
                                </td>
                                <td>${pos.status}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
    
    calculateUnrealizedPnL() {
        return this.positions
            .filter(p => p.status === 'OPEN')
            .reduce((total, pos) => total + this.calculatePositionPnL(pos), 0);
    }
    
    calculatePositionPnL(position) {
        // Simplified P&L calculation
        const currentPrice = this.getCurrentPrice(position.symbol);
        const priceDiff = position.type === 'BUY' 
            ? currentPrice - position.price 
            : position.price - currentPrice;
        return priceDiff * position.amount * 100; // Simplified multiplier
    }
    
    calculateDailyPnL() {
        const today = new Date().toDateString();
        const todayPositions = this.positions.filter(p => 
            p.timestamp.toDateString() === today
        );
        return todayPositions.reduce((total, pos) => total + this.calculatePositionPnL(pos), 0);
    }
    
    showBotStatus(message) {
        console.log(`[Copytrading Bot] ${message}`);
        showSuccessMessage(message);
    }
}

// Initialize bot when page loads
let copytradingBot;

document.addEventListener('DOMContentLoaded', function() {
    copytradingBot = new CopytradingBot();
    
    // Add bot controls if user is logged in
    if (isLoggedIn) {
        addBotControls();
    }
});

function addBotControls() {
    const heroSection = document.querySelector('.hero');
    if (heroSection) {
        const botControls = document.createElement('div');
        botControls.className = 'bot-controls';
        botControls.innerHTML = `
            <div class="bot-control-panel">
                <h3>Panel de Control del Bot</h3>
                <div class="control-buttons">
                    <button class="btn-start" onclick="startBot()">Iniciar Bot</button>
                    <button class="btn-stop" onclick="stopBot()">Detener Bot</button>
                    <button class="btn-settings" onclick="showBotSettings()">Configuración</button>
                </div>
                <div id="tradingDashboard" class="trading-dashboard"></div>
            </div>
        `;
        
        // Add styles for bot controls
        const style = document.createElement('style');
        style.textContent = `
            .bot-controls {
                margin-top: 3rem;
                padding: 2rem;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .bot-control-panel h3 {
                color: #00d4ff;
                margin-bottom: 1.5rem;
                text-align: center;
            }
            .control-buttons {
                display: flex;
                gap: 1rem;
                justify-content: center;
                margin-bottom: 2rem;
            }
            .btn-start, .btn-stop, .btn-settings {
                padding: 0.75rem 1.5rem;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .btn-start {
                background: linear-gradient(135deg, #00d4ff, #0099cc);
                color: #000;
            }
            .btn-stop {
                background: linear-gradient(135deg, #ff6b6b, #ff5252);
                color: #fff;
            }
            .btn-settings {
                background: rgba(255, 255, 255, 0.1);
                color: #fff;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .btn-start:hover, .btn-stop:hover, .btn-settings:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }
            .trading-dashboard {
                margin-top: 2rem;
            }
            .dashboard-stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin-bottom: 2rem;
            }
            .stat-value {
                font-size: 1.5rem;
                font-weight: 700;
                color: #00d4ff;
            }
            .stat-value.positive {
                color: #4caf50;
            }
            .stat-value.negative {
                color: #f44336;
            }
            .positions-table {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 1rem;
                overflow-x: auto;
            }
            .positions-table table {
                width: 100%;
                border-collapse: collapse;
            }
            .positions-table th,
            .positions-table td {
                padding: 0.75rem;
                text-align: left;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            .positions-table th {
                color: #00d4ff;
                font-weight: 600;
            }
            .positions-table .buy {
                color: #4caf50;
            }
            .positions-table .sell {
                color: #f44336;
            }
        `;
        document.head.appendChild(style);
        
        heroSection.appendChild(botControls);
    }
}

// Bot control functions
function startBot() {
    if (copytradingBot) {
        copytradingBot.start();
    }
}

function stopBot() {
    if (copytradingBot) {
        copytradingBot.stop();
    }
}

function showBotSettings() {
    showSuccessMessage('Configuración del bot (próximamente)');
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

// Copytrading Dashboard Functions
function initializeCopytradingData() {
    // Initialize sample data
    initializeTraders();
    initializePositions();
    initializeHistory();
    updateTradingStats();
}

function initializeTraders() {
    const traders = [
        {
            id: 1,
            name: "TraderPro_01",
            status: "active",
            winRate: 87,
            totalTrades: 156,
            monthlyReturn: 12.5,
            isCopied: true
        },
        {
            id: 2,
            name: "FXMaster_2024",
            status: "active",
            winRate: 92,
            totalTrades: 89,
            monthlyReturn: 18.3,
            isCopied: true
        },
        {
            id: 3,
            name: "CryptoKing",
            status: "inactive",
            winRate: 78,
            totalTrades: 234,
            monthlyReturn: 8.7,
            isCopied: false
        }
    ];
    
    const tradersGrid = document.getElementById('tradersGrid');
    if (tradersGrid) {
        tradersGrid.innerHTML = traders.map(trader => `
            <div class="trader-card">
                <div class="trader-header">
                    <span class="trader-name">${trader.name}</span>
                    <span class="trader-status ${trader.status}">${trader.status === 'active' ? 'Activo' : 'Inactivo'}</span>
                </div>
                <div class="trader-stats">
                    <div class="trader-stat">
                        <div class="trader-stat-value">${trader.winRate}%</div>
                        <div class="trader-stat-label">Tasa de Éxito</div>
                    </div>
                    <div class="trader-stat">
                        <div class="trader-stat-value">${trader.monthlyReturn}%</div>
                        <div class="trader-stat-label">Retorno Mensual</div>
                    </div>
                </div>
                <div class="trader-actions">
                    ${trader.isCopied ? 
                        `<button class="btn-remove" onclick="removeTrader(${trader.id})">Remover</button>` :
                        `<button class="btn-copy" onclick="copyTrader(${trader.id})">Copiar</button>`
                    }
                </div>
            </div>
        `).join('');
    }
}

function initializePositions() {
    const positions = [
        {
            id: 1,
            symbol: "EURUSD",
            type: "BUY",
            volume: 1000,
            openPrice: 1.0850,
            currentPrice: 1.0875,
            pnl: 25.00,
            status: "OPEN"
        },
        {
            id: 2,
            symbol: "GBPUSD",
            type: "SELL",
            volume: 500,
            openPrice: 1.2650,
            currentPrice: 1.2620,
            pnl: 15.00,
            status: "OPEN"
        },
        {
            id: 3,
            symbol: "USDJPY",
            type: "BUY",
            volume: 800,
            openPrice: 150.00,
            currentPrice: 150.25,
            pnl: 2.00,
            status: "OPEN"
        }
    ];
    
    updatePositionsTable(positions);
}

function updatePositionsTable(positions) {
    const tbody = document.getElementById('positionsTableBody');
    if (tbody) {
        tbody.innerHTML = positions.map(pos => `
            <tr>
                <td>${pos.symbol}</td>
                <td class="${pos.type.toLowerCase()}">${pos.type}</td>
                <td>$${pos.volume.toLocaleString()}</td>
                <td>${pos.openPrice.toFixed(4)}</td>
                <td>${pos.currentPrice.toFixed(4)}</td>
                <td class="${pos.pnl >= 0 ? 'positive' : 'negative'}">
                    ${pos.pnl >= 0 ? '+' : ''}$${pos.pnl.toFixed(2)}
                </td>
                <td>${pos.status}</td>
                <td>
                    <button class="action-btn btn-close" onclick="closePosition(${pos.id})">
                        Cerrar
                    </button>
                </td>
            </tr>
        `).join('');
    }
}

function initializeHistory() {
    const history = [
        {
            date: new Date('2024-01-15 14:30:00'),
            symbol: "EURUSD",
            type: "BUY",
            volume: 1000,
            price: 1.0820,
            pnl: 45.00,
            trader: "TraderPro_01"
        },
        {
            date: new Date('2024-01-15 10:15:00'),
            symbol: "GBPUSD",
            type: "SELL",
            volume: 500,
            price: 1.2680,
            pnl: -12.50,
            trader: "FXMaster_2024"
        },
        {
            date: new Date('2024-01-14 16:45:00'),
            symbol: "USDJPY",
            type: "BUY",
            volume: 800,
            price: 149.50,
            pnl: 32.00,
            trader: "TraderPro_01"
        }
    ];
    
    updateHistoryTable(history);
}

function updateHistoryTable(history) {
    const tbody = document.getElementById('historyTableBody');
    if (tbody) {
        tbody.innerHTML = history.map(trade => `
            <tr>
                <td>${formatDate(trade.date)}</td>
                <td>${trade.symbol}</td>
                <td class="${trade.type.toLowerCase()}">${trade.type}</td>
                <td>$${trade.volume.toLocaleString()}</td>
                <td>${trade.price.toFixed(4)}</td>
                <td class="${trade.pnl >= 0 ? 'positive' : 'negative'}">
                    ${trade.pnl >= 0 ? '+' : ''}$${trade.pnl.toFixed(2)}
                </td>
                <td>${trade.trader}</td>
            </tr>
        `).join('');
    }
}

function updateTradingStats() {
    // Update trading statistics
    const stats = {
        totalBalance: 10250.00,
        dailyPnL: 250.00,
        tradesToday: 12,
        successRate: 85
    };
    
    document.getElementById('totalBalance').textContent = `$${stats.totalBalance.toLocaleString()}`;
    document.getElementById('dailyPnL').textContent = `+$${stats.dailyPnL.toFixed(2)}`;
    document.getElementById('tradesToday').textContent = stats.tradesToday;
    document.getElementById('successRate').textContent = `${stats.successRate}%`;
}

// Bot Control Functions
function startCopytradingBot() {
    if (copytradingBot) {
        copytradingBot.start();
        updateBotStatus(true);
        showSuccessMessage('Bot de copytrading iniciado correctamente');
    }
}

function stopCopytradingBot() {
    if (copytradingBot) {
        copytradingBot.stop();
        updateBotStatus(false);
        showSuccessMessage('Bot de copytrading detenido');
    }
}

function updateBotStatus(isRunning) {
    const statusDot = document.getElementById('botStatusDot');
    const statusText = document.getElementById('botStatusText');
    const startBtn = document.querySelector('.btn-start-bot');
    const stopBtn = document.querySelector('.btn-stop-bot');
    
    if (isRunning) {
        statusDot.classList.add('running');
        statusText.textContent = 'Bot Ejecutándose';
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        statusDot.classList.remove('running');
        statusText.textContent = 'Bot Detenido';
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
}

function openBotSettings() {
    document.getElementById('botSettingsModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function openTraderSelection() {
    document.getElementById('traderSelectionModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
    loadAvailableTraders();
}

function loadAvailableTraders() {
    const availableTraders = [
        {
            id: 4,
            name: "ScalpingMaster",
            performance: 15.2,
            trades: 45,
            winRate: 89
        },
        {
            id: 5,
            name: "SwingTrader_Pro",
            performance: 22.8,
            trades: 23,
            winRate: 91
        },
        {
            id: 6,
            name: "NewsTrader",
            performance: 8.5,
            trades: 67,
            winRate: 76
        }
    ];
    
    const container = document.getElementById('availableTraders');
    if (container) {
        container.innerHTML = availableTraders.map(trader => `
            <div class="available-trader">
                <div class="trader-info">
                    <h4>${trader.name}</h4>
                    <p>${trader.trades} operaciones • ${trader.winRate}% éxito</p>
                </div>
                <div class="trader-performance">
                    <div class="performance-value">+${trader.performance}%</div>
                    <div class="performance-label">Retorno</div>
                </div>
                <button class="btn-copy" onclick="addTrader(${trader.id})">Agregar</button>
            </div>
        `).join('');
    }
}

// Trader Management Functions
function copyTrader(traderId) {
    showSuccessMessage('Trader agregado para copiar');
    // Update UI to show trader as copied
    initializeTraders(); // Refresh the list
}

function removeTrader(traderId) {
    showSuccessMessage('Trader removido de la lista de copia');
    // Update UI to show trader as not copied
    initializeTraders(); // Refresh the list
}

function addTrader(traderId) {
    showSuccessMessage('Trader agregado exitosamente');
    closeModal('traderSelectionModal');
    initializeTraders(); // Refresh the list
}

function closePosition(positionId) {
    showSuccessMessage('Posición cerrada exitosamente');
    // Remove position from list
    initializePositions(); // Refresh the list
}

// Dashboard Section Navigation
function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.dashboard-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Remove active class from all tabs
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Activate corresponding tab
    const targetTab = document.querySelector(`[data-section="${sectionId}"]`);
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    // Initialize section-specific data if needed
    if (sectionId === 'traders') {
        initializeTraders();
    }
}

// Debug function for quick login
function quickLogin() {
    currentUser = {
        email: 'demo@metabinario.com',
        name: 'demo',
        plan: 'profesional'
    };
    isLoggedIn = true;
    localStorage.setItem('metabinario_user', JSON.stringify(currentUser));
    updateUIForLoggedInUser();
    showSuccessMessage('¡Login rápido exitoso!');
}

// Export functions for global access
window.showLogin = showLogin;
window.showRegister = showRegister;
window.closeModal = closeModal;
window.selectPlan = selectPlan;
window.logout = logout;
window.startBot = startBot;
window.stopBot = stopBot;
window.showBotSettings = showBotSettings;
window.startCopytradingBot = startCopytradingBot;
window.stopCopytradingBot = stopCopytradingBot;
window.openBotSettings = openBotSettings;
window.openTraderSelection = openTraderSelection;
window.copyTrader = copyTrader;
window.removeTrader = removeTrader;
window.addTrader = addTrader;
window.closePosition = closePosition;
window.quickLogin = quickLogin;
window.showSection = showSection;
