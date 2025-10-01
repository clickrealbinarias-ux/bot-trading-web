/**
 * Metabinario Web - API Client
 * Comunicación con el backend Flask
 */

class MetabinarioAPI {
    constructor() {
        this.baseURL = 'http://localhost:5004/api';
        this.token = localStorage.getItem('metabinario_token');
        this.socket = null;
        this.initSocket();
    }

    // ==================== CONFIGURACIÓN ====================

    initSocket() {
        // Inicializar WebSocket para notificaciones en tiempo real
        this.socket = io('http://localhost:5004');
        
        this.socket.on('connect', () => {
            console.log('🔌 Conectado al servidor WebSocket');
            this.joinUserRoom();
        });

        this.socket.on('disconnect', () => {
            console.log('❌ Desconectado del servidor WebSocket');
        });

        this.socket.on('notification', (data) => {
            this.handleNotification(data);
        });

        this.socket.on('copytrading_result', (data) => {
            this.handleCopytradingResult(data);
        });

        this.socket.on('new_operation', (data) => {
            this.handleNewOperation(data);
        });
    }

    joinUserRoom() {
        if (this.token) {
            this.socket.emit('join_room', { room: this.getCurrentUser() });
        }
    }

    // ==================== AUTENTICACIÓN ====================

    async login(email, password, role = 'follower') {
        try {
            const response = await fetch(`${this.baseURL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password, role })
            });

            const data = await response.json();
            
            if (data.success) {
                this.token = data.token;
                localStorage.setItem('metabinario_token', this.token);
                this.joinUserRoom();
                return data;
            } else {
                throw new Error(data.error || 'Error en el login');
            }
        } catch (error) {
            console.error('Error en login:', error);
            throw error;
        }
    }

    async register(username, password, email, role = 'follower') {
        try {
            const response = await fetch(`${this.baseURL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password, email, role })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error en registro:', error);
            throw error;
        }
    }

    async logout() {
        try {
            if (this.token) {
                await fetch(`${this.baseURL}/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.token}`,
                        'Content-Type': 'application/json',
                    }
                });
            }
            
            this.token = null;
            localStorage.removeItem('metabinario_token');
            this.socket.disconnect();
        } catch (error) {
            console.error('Error en logout:', error);
        }
    }

    // ==================== TRADER ====================

    async addTraderAccount(email, password, balanceMode = 'PRACTICE') {
        try {
            const response = await fetch(`${this.baseURL}/trader/add`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password, balance_mode: balanceMode })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error agregando trader:', error);
            throw error;
        }
    }

    async getTraderStatus() {
        try {
            const response = await fetch(`${this.baseURL}/trader/status`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                }
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error obteniendo estado del trader:', error);
            throw error;
        }
    }

    async startTraderMonitoring(amount = 10.0) {
        try {
            const response = await fetch(`${this.baseURL}/trader/start-monitoring`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ amount })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error iniciando monitoreo:', error);
            throw error;
        }
    }

    async stopTraderMonitoring() {
        try {
            const response = await fetch(`${this.baseURL}/trader/stop-monitoring`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                }
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error deteniendo monitoreo:', error);
            throw error;
        }
    }

    // ==================== SEGUIDORES ====================

    async addFollowerAccount(email, password, amount = 10.0, balanceMode = 'PRACTICE') {
        try {
            const response = await fetch(`${this.baseURL}/follower/add`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password, amount, balance_mode: balanceMode })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error agregando seguidor:', error);
            throw error;
        }
    }

    async updateFollowerAmount(email, amount) {
        try {
            const response = await fetch(`${this.baseURL}/follower/update-amount`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, amount: amount })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error actualizando importe del seguidor:', error);
            throw error;
        }
    }

    async getFollowers() {
        try {
            const response = await fetch(`${this.baseURL}/followers`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                }
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error obteniendo seguidores:', error);
            throw error;
        }
    }

    async removeFollower(email) {
        try {
            const response = await fetch(`${this.baseURL}/follower/remove`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error removiendo seguidor:', error);
            throw error;
        }
    }

    // ==================== COPYTRADING ====================

    async executeManualCopytrading(amount, active, direction, duration) {
        try {
            const response = await fetch(`${this.baseURL}/copytrading/manual`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ amount, active, direction, duration })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error en copytrading manual:', error);
            throw error;
        }
    }

    async startAutoCopytrading(amount = 10.0) {
        try {
            const response = await fetch(`${this.baseURL}/copytrading/auto/start`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ amount })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error iniciando copytrading automático:', error);
            throw error;
        }
    }

    async stopAutoCopytrading() {
        try {
            const response = await fetch(`${this.baseURL}/copytrading/auto/stop`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                }
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error deteniendo copytrading automático:', error);
            throw error;
        }
    }

    async getCopytradingStatus() {
        try {
            const response = await fetch(`${this.baseURL}/copytrading/status`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                }
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error obteniendo estado del copytrading:', error);
            throw error;
        }
    }

    // ==================== UTILIDADES ====================

    getCurrentUser() {
        // Obtener usuario actual del token (implementación simple)
        if (this.token) {
            try {
                const payload = JSON.parse(atob(this.token.split('.')[1]));
                return payload.user_id;
            } catch (error) {
                console.error('Error decodificando token:', error);
                return null;
            }
        }
        return null;
    }

    isAuthenticated() {
        return this.token !== null;
    }

    // ==================== MANEJADORES DE EVENTOS ====================

    handleNotification(data) {
        console.log('📢 Notificación recibida:', data);
        
        // Manejar diferentes tipos de notificaciones
        switch(data.type) {
            case 'trader_connected':
                this.showConnectionSuccess('Trader', data.data.email, 'conectado exitosamente');
                break;
            case 'trader_connection_failed':
                this.showConnectionError('Trader', data.data.email, data.data.error);
                break;
            case 'follower_connected':
                this.showConnectionSuccess('Seguidor', data.data.email, 'conectado exitosamente');
                break;
            case 'follower_connection_failed':
                this.showConnectionError('Seguidor', data.data.email, data.data.error);
                break;
            case 'new_operation':
                this.showNewOperation(data.data);
                break;
            case 'copytrading_result':
                this.showCopytradingResult(data.data);
                break;
            default:
                this.showNotification(data.type, data.data);
        }
    }

    handleCopytradingResult(data) {
        console.log('📊 Resultado de copytrading:', data);
        
        // Actualizar UI con resultado
        this.updateCopytradingResults(data);
    }

    handleNewOperation(data) {
        console.log('🔄 Nueva operación detectada:', data);
        
        // Actualizar UI con nueva operación
        this.updateNewOperation(data);
    }

    // ==================== UI HELPERS ====================

    showNotification(type, data) {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-type">${type.toUpperCase()}</span>
                <span class="notification-message">${JSON.stringify(data)}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Agregar al DOM
        document.body.appendChild(notification);
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    updateCopytradingResults(data) {
        // Actualizar estadísticas de trading
        const statsElement = document.getElementById('tradingStats');
        if (statsElement) {
            statsElement.innerHTML = `
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-content">
                        <div class="stat-value">${data.successful_operations}/${data.total_operations}</div>
                        <div class="stat-label">Operaciones Exitosas</div>
                    </div>
                </div>
            `;
        }
    }

    updateNewOperation(data) {
        // Agregar nueva operación a la tabla
        const operationsTable = document.getElementById('operationsTable');
        if (operationsTable) {
            const tbody = operationsTable.querySelector('tbody') || operationsTable;
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${data.active}</td>
                <td>${data.direction}</td>
                <td>$${data.amount}</td>
                <td>${data.duration}min</td>
                <td>${new Date().toLocaleTimeString()}</td>
                <td><span class="status-pending">Pendiente</span></td>
            `;
            tbody.insertBefore(row, tbody.firstChild);
        }
    }

    // ==================== NOTIFICACIONES ESPECÍFICAS ====================

    showConnectionSuccess(type, email, message) {
        this.showNotification('success', {
            title: `✅ ${type} Conectado`,
            message: `${email} ${message}`,
            type: 'success'
        });
    }

    showConnectionError(type, email, error) {
        this.showNotification('error', {
            title: `❌ Error de Conexión`,
            message: `${type} ${email}: ${error}`,
            type: 'error'
        });
    }

    showNewOperation(data) {
        this.showNotification('info', {
            title: '🔄 Nueva Operación Detectada',
            message: `${data.active} ${data.direction} - $${data.amount}`,
            type: 'info'
        });
        
        // Actualizar tabla de operaciones
        this.updateNewOperation(data);
    }

    showCopytradingResult(data) {
        this.showNotification('info', {
            title: '📊 Resultado de Copytrading',
            message: `${data.successful_operations}/${data.total_operations} operaciones exitosas`,
            type: 'info'
        });
        
        // Actualizar estadísticas
        this.updateCopytradingResults(data);
    }
}

// Instancia global de la API
window.metabinarioAPI = new MetabinarioAPI();
