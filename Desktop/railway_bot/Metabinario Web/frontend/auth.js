/**
 * Metabinario Web - Authentication Module
 * Manejo de autenticación con el backend
 */

// ==================== FUNCIONES DE AUTENTICACIÓN ====================

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    if (!email || !password) {
        showMessage('Por favor, completa todos los campos', 'error');
        return;
    }
    
    try {
        showMessage('Iniciando sesión...', 'info');
        
        // Obtener el rol seleccionado
        const selectedRole = localStorage.getItem('selectedRole') || 'follower';
        
        // Usar la API para hacer login con credenciales de ExNova
        const response = await metabinarioAPI.login(email, password, selectedRole);
        
        if (response.success) {
            currentUser = response.user;
            isLoggedIn = true;
            
            // Guardar en localStorage
            localStorage.setItem('metabinario_user', JSON.stringify(currentUser));
            
            updateUIForLoggedInUser();
            closeModal('loginModal');
            showMessage(`¡Bienvenido, ${currentUser.username}!`, 'success');
        } else {
            showMessage('Credenciales inválidas', 'error');
        }
    } catch (error) {
        console.error('Error en login:', error);
        showMessage('Error al iniciar sesión. Verifica tu conexión.', 'error');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('registerConfirmPassword').value;
    const terms = document.getElementById('registerTerms').checked;
    
    // Validación local
    if (!validateRegistration(name, email, password, confirmPassword, terms)) {
        return;
    }
    
    try {
        showMessage('Registrando usuario...', 'info');
        
        // Usar la API para registrar
        const response = await metabinarioAPI.register(name, password, email, 'follower');
        
        if (response.success) {
            showMessage('Usuario registrado exitosamente. Ahora puedes iniciar sesión.', 'success');
            closeModal('registerModal');
            
            // Limpiar formulario
            document.getElementById('registerForm').reset();
        } else {
            showMessage(response.error || 'Error al registrar usuario', 'error');
        }
    } catch (error) {
        console.error('Error en registro:', error);
        showMessage('Error al registrar usuario. Verifica tu conexión.', 'error');
    }
}

function validateRegistration(name, email, password, confirmPassword, terms) {
    if (!name || name.length < 2) {
        showMessage('El nombre debe tener al menos 2 caracteres.', 'error');
        return false;
    }
    
    if (!isValidEmail(email)) {
        showMessage('Por favor, introduce un email válido.', 'error');
        return false;
    }
    
    if (password.length < 6) {
        showMessage('La contraseña debe tener al menos 6 caracteres.', 'error');
        return false;
    }
    
    if (password !== confirmPassword) {
        showMessage('Las contraseñas no coinciden.', 'error');
        return false;
    }
    
    if (!terms) {
        showMessage('Debes aceptar los términos y condiciones.', 'error');
        return false;
    }
    
    return true;
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

async function logout() {
    try {
        // Usar la API para logout
        await metabinarioAPI.logout();
        
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
        
        // Hide copytrading dashboard
        document.getElementById('copytrading-dashboard').style.display = 'none';
        
        // Show main sections
        document.querySelector('.hero').style.display = 'block';
        document.querySelector('.copytrading-section').style.display = 'block';
        document.querySelector('.features-section').style.display = 'block';
        document.querySelector('.pricing-section').style.display = 'block';
        
        showMessage('Sesión cerrada exitosamente', 'success');
    } catch (error) {
        console.error('Error en logout:', error);
        showMessage('Error al cerrar sesión', 'error');
    }
}

function checkAuthStatus() {
    // Verificar si hay un usuario guardado
    const savedUser = localStorage.getItem('metabinario_user');
    if (savedUser) {
        try {
            currentUser = JSON.parse(savedUser);
            isLoggedIn = true;
            
            // Verificar si el token sigue siendo válido
            if (metabinarioAPI && metabinarioAPI.isAuthenticated()) {
                updateUIForLoggedInUser();
            } else {
                // Token expirado, limpiar datos
                localStorage.removeItem('metabinario_user');
                currentUser = null;
                isLoggedIn = false;
            }
        } catch (error) {
            console.error('Error cargando usuario guardado:', error);
            localStorage.removeItem('metabinario_user');
        }
    }
}

function updateUIForLoggedInUser() {
    // Update navigation
    const navButtons = document.querySelector('.nav-buttons');
    if (navButtons && currentUser) {
        navButtons.innerHTML = `
            <div class="user-info">
                <span>Hola, ${currentUser.username}</span>
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
    
    // Configure UI based on user role
    if (currentUser && currentUser.role === 'follower') {
        // Show follower controls
        document.getElementById('amountBtn').style.display = 'inline-block';
        document.getElementById('startFollowerBtn').style.display = 'inline-block';
        document.getElementById('stopFollowerBtn').style.display = 'none';
        document.getElementById('disconnectBtn').style.display = 'inline-block';
        
        // Check follower bot status
        if (typeof checkFollowerBotStatus === 'function') {
            checkFollowerBotStatus();
        }
    } else {
        // Hide follower controls for traders
        document.getElementById('amountBtn').style.display = 'none';
        document.getElementById('startFollowerBtn').style.display = 'none';
        document.getElementById('stopFollowerBtn').style.display = 'none';
        document.getElementById('disconnectBtn').style.display = 'none';
    }
    
    // Scroll to top
    window.scrollTo(0, 0);
}

// ==================== FUNCIONES DE MODAL ====================

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

// ==================== FUNCIÓN DE LOGIN RÁPIDO ====================

async function quickLogin() {
    try {
        // Usar credenciales de demo
        const response = await metabinarioAPI.login('demo_user', 'demo123');
        
        if (response.success) {
            currentUser = response.user;
            isLoggedIn = true;
            localStorage.setItem('metabinario_user', JSON.stringify(currentUser));
            updateUIForLoggedInUser();
            showMessage('¡Login rápido exitoso!', 'success');
        } else {
            showMessage('Error en login rápido', 'error');
        }
    } catch (error) {
        console.error('Error en login rápido:', error);
        showMessage('Error en login rápido. Verifica tu conexión.', 'error');
    }
}

// ==================== EXPORTAR FUNCIONES ====================

// Exportar funciones para acceso global
window.handleLogin = handleLogin;
window.handleRegister = handleRegister;
window.logout = logout;
window.showLogin = showLogin;
window.showRegister = showRegister;
window.closeModal = closeModal;
window.quickLogin = quickLogin;
