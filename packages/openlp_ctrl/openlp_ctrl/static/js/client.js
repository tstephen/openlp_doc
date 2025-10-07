/**
 * OpenLP Control - Client Interface JavaScript
 */

class OpenLPControlClient {
    constructor() {
        this.serverUrl = 'http://localhost:8000';
        this.websocket = null;
        this.clientId = `client-${Math.random().toString(36).substr(2, 9)}-${Date.now()}`;
        console.log(`Generated client ID: ${this.clientId}`);
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;

        this.initializeUI();
        this.connect();
    }

    initializeUI() {
        console.info('Initializing UI');
        document.querySelector('.openlp-client-id').value = this.clientId;

        this.setupEventListeners();
        this.loadServerStatus();
    }

    setupEventListeners() {
        // Connect button
        const connectBtn = document.querySelector('.openlp-connect-btn');
        if (connectBtn) {
            connectBtn.addEventListener('click', () => this.connect());
        }

        // Disconnect button
        const disconnectBtn = document.querySelector('.openlp-disconnect-btn');
        if (disconnectBtn) {
            disconnectBtn.addEventListener('click', () => this.disconnect());
        }

        // Set slide form
        const slideBtn = document.querySelector('.openlp-set-slide-btn');
        if (slideBtn) {
            slideBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.setSlide();
            });
        }

        // Refresh status button
        const refreshBtn = document.querySelector('.openlp-refresh-status');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadServerStatus());
        }
    }

    async connect() {

        if (!this.clientId) {
            this.showMessage('Please enter a client ID', 'error');
            return;
        }

        try {
            const wsUrl = this.serverUrl.replace('http://', 'ws://').replace('https://', 'wss://');
            this.websocket = new WebSocket(`${wsUrl}/connect/${this.clientId}`);

            this.websocket.onopen = () => {
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus();
                this.showMessage(`Connected to ${this.serverUrl} as ${this.clientId}`, 'success');
            };

            this.websocket.onmessage = (event) => {
                this.handleMessage(event.data);
            };

            this.websocket.onclose = () => {
                this.isConnected = false;
                this.updateConnectionStatus();
                this.showMessage('Connection closed', 'warning');
                this.attemptReconnect();
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.showMessage('Connection error', 'error');
            };

        } catch (error) {
            console.error('Failed to connect:', error);
            this.showMessage('Failed to connect to server', 'error');
        }
    }

    disconnect() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        this.isConnected = false;
        this.reconnectAttempts = this.maxReconnectAttempts; // Prevent auto-reconnect
        this.updateConnectionStatus();
        this.showMessage('Disconnected', 'info');
    }

    handleMessage(message) {
        console.log('Received message:', message);

        if (message.startsWith('slide_update:')) {
            const slideId = message.split(':', 2)[1];
            this.updateCurrentSlide(slideId);
            this.showMessage(`New slide: ${slideId}`, 'info');
        } else {
            try {
                const data = JSON.parse(message);
                if (data.type === 'heartbeat_response') {
                    console.log('Heartbeat acknowledged');
                }
            } catch (e) {
                console.log('Non-JSON message:', message);
            }
        }
    }

    async setSlide() {
        const slideIdInput = document.querySelector('.openlp-slide-id');
        const slideId = slideIdInput ? slideIdInput.value.trim() : undefined;
        console.log(`Setting slide to: ${slideId}`);

        if (!slideId) {
            this.showMessage('Please enter a slide ID', 'error');
            return;
        }

        try {
            const response = await fetch(`${this.serverUrl}/set-slide`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ id: slideId })
            });

            if (response.ok) {
                const result = await response.json();
                this.showMessage(`Slide set to ${slideId} (${result.clients_notified} clients notified)`, 'success');
                slideIdInput.value = '';
            } else {
                this.showMessage('Failed to set slide', 'error');
            }
        } catch (error) {
            console.error('Error setting slice:', error);
            this.showMessage('Error setting slide', 'error');
        }
    }

    async loadServerStatus() {
        try {
            const response = await fetch(`${this.serverUrl}/status`);
            if (response.ok) {
                this.showMessage('Server status refreshed', 'info');
                const status = await response.json();
                this.updateServerStatus(status);
            }
        } catch (error) {
            console.error('Failed to load server status:', error);
        }
    }

    updateConnectionStatus() {
        const statusElement = document.querySelector('.openlp-connection-status');
        const connectBtn = document.querySelector('.openlp-connect-btn');
        const disconnectBtn = document.querySelector('.openlp-disconnect-btn');

        if (statusElement) {
            statusElement.textContent = this.isConnected ? 'Connected' : 'Disconnected';
            statusElement.className = `status ${this.isConnected ? 'connected' : 'disconnected'}`;
        }

        if (connectBtn) connectBtn.disabled = this.isConnected;
        if (disconnectBtn) disconnectBtn.disabled = !this.isConnected;
    }

    updateCurrentSlide(slideId) {
        const slideElement = document.querySelector('.openlp-current-slide');
        if (slideElement) {
            slideElement.textContent = slideId;
        }

        const lastUpdateElement = document.querySelector('.openlp-last-update');
        if (lastUpdateElement) {
            lastUpdateElement.textContent = new Date().toLocaleTimeString();
        }
    }

    updateServerStatus(status) {
        const clientsElement = document.querySelector('.openlp-connected-clients');
        const countElement = document.querySelector('.openlp-client-count');

        if (clientsElement) {
            clientsElement.innerHTML = '';
            status.connected_clients.forEach(clientId => {
                const li = document.createElement('li');
                li.textContent = clientId;
                li.className = 'client-item';
                clientsElement.appendChild(li);
            });
        }

        if (countElement) {
            countElement.textContent = status.total_connections;
        }
    }

    showMessage(message, type = 'info') {
        const messageContainer = document.querySelector('.openlp-messages');
        if (!messageContainer) return;

        const messageElement = document.createElement('div');
        messageElement.className = `message message-${type}`;
        messageElement.textContent = message;

        messageContainer.appendChild(messageElement);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.parentNode.removeChild(messageElement);
            }
        }, 5000);
    }

    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            this.showMessage('Max reconnection attempts reached', 'error');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

        setTimeout(() => {
            if (!this.isConnected && this.clientId) {
                this.showMessage(`Reconnecting... (attempt ${this.reconnectAttempts})`, 'info');
                this.connect();
            }
        }, delay);
    }

    sendHeartbeat() {
        if (this.websocket && this.isConnected) {
            const heartbeat = {
                type: 'heartbeat',
                timestamp: Date.now()
            };
            this.websocket.send(JSON.stringify(heartbeat));
        }
    }
}

// Initialize the client when the page loads
window.addEventListener('DOMContentLoaded', () => {
    window.openlp = new OpenLPControlClient();

    // Send heartbeat every 30 seconds
    setInterval(() => {
        if (window.openlp) {
            window.openlp.sendHeartbeat();
        }
    }, 30000);
});
