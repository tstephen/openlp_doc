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
        if (!window.location.hash || window.location.hash === '') {
            window.location.hash = '/0/0';
        }
        const clientIdInput = document.querySelector('.openlp-client-id');
        if (clientIdInput) clientIdInput.value = this.clientId;

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
                const slideIdInput = document.querySelector('.openlp-slide-id');
                const slideId = slideIdInput ? slideIdInput.value.trim() : undefined;
                this.setSlide(slideId);
            });
        }

        // Refresh status button
        const refreshBtn = document.querySelector('.openlp-refresh-status');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadServerStatus());
        }

        // Setup Reveal.js navigation controls after Reveal.js is ready
        this.setupRevealNavigation();
    }

    setupRevealNavigation() {
        // Wait for Reveal.js to be ready and controls to be created
        if (typeof Reveal !== 'undefined') {
            Reveal.on('ready', () => {
                console.log('Reveal.js is ready, setting up navigation controls');
                this.attachNavigationListeners();
            });
        } else {
            // Fallback: try again after a short delay if Reveal.js isn't loaded yet
            setTimeout(() => {
                if (typeof Reveal !== 'undefined') {
                    Reveal.on('ready', () => {
                        console.log('Reveal.js is ready (delayed), setting up navigation controls');
                        this.attachNavigationListeners();
                    });
                } else {
                    console.warn('Reveal.js not found, navigation controls will not be attached');
                }
            }, 1000);
        }
    }

    attachNavigationListeners() {
        // Standard slide controls
        const navUp = document.querySelector('.navigate-up');
        if (navUp) {
            navUp.addEventListener('click', () => this.navigateSlides('up'));
            console.log('Attached navigate-up listener');
        } else {
            console.warn('No navigate-up button found in the DOM.');
        }

        const navDown = document.querySelector('.navigate-down');
        if (navDown) {
            navDown.addEventListener('click', () => this.navigateSlides('down'));
            console.log('Attached navigate-down listener');
        } else {
            console.warn('No navigate-down button found in the DOM.');
        }

        const navLeft = document.querySelector('.navigate-left');
        if (navLeft) {
            navLeft.addEventListener('click', () => this.navigateSlides('left'));
            console.log('Attached navigate-left listener');
        } else {
            console.warn('No navigate-left button found in the DOM.');
        }

        const navRight = document.querySelector('.navigate-right');
        if (navRight) {
            navRight.addEventListener('click', () => this.navigateSlides('right'));
            console.log('Attached navigate-right listener');
        } else {
            console.warn('No navigate-right button found in the DOM.');
        }


    }

    async connect() {

        if (!this.clientId) {
            this.showMessage('Please enter a client ID', 'error');
            return;
        }

        try {
            const wsUrl = this.serverUrl.replace('http://', 'ws://').replace('https://', 'wss://');
            this.websocket = new WebSocket(`${wsUrl}/api/connect/${this.clientId}`);

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
            window.location.hash = slideId;
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

    async setSlide(slideId) {
        console.log(`Setting slide to: ${slideId}`);

        if (!slideId) {
            this.showMessage('Please enter a slide ID', 'error');
            return;
        }

        try {
            const response = await fetch(`${this.serverUrl}/api/set-slide`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ id: slideId })
            });

            if (response.ok) {
                const result = await response.json();
                this.showMessage(`Slide set to ${slideId} (${result.clients_notified} clients notified)`, 'success');
                const slideIdInput = document.querySelector('.openlp-slide-id');
                if (slideIdInput) {
                    slideIdInput.value = '';
                }
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
            const response = await fetch(`${this.serverUrl}/api/status`);
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

    navigateSlides(navDir) {
        // Get current hash or default to /0/0
        let hash = window.location.hash || '#/0/0';

        // Remove the # and split by /
        const parts = hash.substring(1).split('/');

        // Parse current numbers, default to 0 if invalid
        let firstNum = parseInt(parts[1]) || 0;
        let secondNum = parseInt(parts[2]) || 0;

        // Navigate based on direction
        switch (navDir) {
            case 'up':
                firstNum = Math.max(0, firstNum - 1); // Never go below 0
                break;
            case 'down':
                firstNum = firstNum + 1;
                break;
            case 'right':
                secondNum = secondNum + 1;
                break;
            case 'left':
                secondNum = Math.max(0, secondNum - 1); // Never go below 0
                break;
            default:
                console.warn(`Unknown navigation direction: ${navDir}`);
                return;
        }

        // Update the hash
        const newHash = `/${firstNum}/${secondNum}`;
        window.location.hash = newHash;

        // Also send the slide update to the server
        this.setSlide(newHash);

        console.log(`Navigated ${navDir}: ${newHash}`);
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
