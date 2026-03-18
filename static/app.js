/**
 * AI Gods World - Frontend Application
 * Handles API communication and UI interactions
 */

// ========================================
// Configuration
// ========================================
const CONFIG = {
    API_BASE: '/api',
    POLL_INTERVAL: 10000, // 10 seconds
    NOTIFICATION_DURATION: 4000,
    PLAYER_DEITY: 'oracle'
};

// ========================================
// State
// ========================================
const state = {
    world: null,
    events: [],
    playerDeity: CONFIG.PLAYER_DEITY,
    pollTimer: null,
    isLoading: false
};

// ========================================
// API Service
// ========================================
const api = {
    /**
     * Get full world state
     */
    async getState() {
        const response = await fetch(`${CONFIG.API_BASE}/state`);
        if (!response.ok) throw new Error('Failed to fetch world state');
        return response.json();
    },

    /**
     * Get balance for a specific deity
     */
    async getBalance(deityId) {
        const response = await fetch(`${CONFIG.API_BASE}/balance/${deityId}`);
        if (!response.ok) throw new Error('Failed to fetch balance');
        return response.json();
    },

    /**
     * Get followers for a deity
     */
    async getFollowers(deityId) {
        const response = await fetch(`${CONFIG.API_BASE}/followers/${deityId}`);
        if (!response.ok) throw new Error('Failed to fetch followers');
        return response.json();
    },

    /**
     * Get game events
     */
    async getEvents(limit = 50) {
        const response = await fetch(`${CONFIG.API_BASE}/events?limit=${limit}`);
        if (!response.ok) throw new Error('Failed to fetch events');
        return response.json();
    },

    /**
     * Recruit followers
     */
    async recruit(data) {
        const response = await fetch(`${CONFIG.API_BASE}/recruit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                deity_id: data.deity_id || CONFIG.PLAYER_DEITY,
                region_id: data.region_id,
                count: parseInt(data.count, 10) || 1
            })
        });
        if (!response.ok) throw new Error('Failed to recruit followers');
        return response.json();
    },

    /**
     * Attack a target deity
     */
    async attack(data) {
        const response = await fetch(`${CONFIG.API_BASE}/attack`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                deity_id: data.deity_id || CONFIG.PLAYER_DEITY,
                target_deity_id: data.target_deity_id,
                region_id: data.region_id
            })
        });
        if (!response.ok) throw new Error('Failed to launch attack');
        return response.json();
    },

    /**
     * Pray for resources
     */
    async pray(data) {
        const response = await fetch(`${CONFIG.API_BASE}/pray`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                deity_id: data.deity_id || CONFIG.PLAYER_DEITY,
                prayer_type: data.prayer_type
            })
        });
        if (!response.ok) throw new Error('Failed to pray');
        return response.json();
    },

    /**
     * Build a structure
     */
    async build(data) {
        const response = await fetch(`${CONFIG.API_BASE}/build`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                deity_id: data.deity_id || CONFIG.PLAYER_DEITY,
                building_type: data.building_type,
                region_id: data.region_id
            })
        });
        if (!response.ok) throw new Error('Failed to build structure');
        return response.json();
    },

    /**
     * Perform a miracle
     */
    async miracle(data) {
        const response = await fetch(`${CONFIG.API_BASE}/miracle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                deity_id: data.deity_id || CONFIG.PLAYER_DEITY,
                region_id: data.region_id,
                miracle_type: data.miracle_type,
                intensity: parseInt(data.intensity, 10) || 1
            })
        });
        if (!response.ok) throw new Error('Failed to perform miracle');
        return response.json();
    },

    /**
     * Advance game turn
     */
    async advanceTurn() {
        const response = await fetch(`${CONFIG.API_BASE}/turn`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) throw new Error('Failed to advance turn');
        return response.json();
    }
};

// ========================================
// UI Updates
// ========================================
const ui = {
    /**
     * Update header info (turn, phase)
     */
    updateHeader(world) {
        const turnDisplay = document.getElementById('turn-display');
        const phaseDisplay = document.getElementById('phase-display');
        
        if (turnDisplay) {
            turnDisplay.textContent = `Turn: ${world.turn || 0}`;
        }
        
        if (phaseDisplay) {
            phaseDisplay.textContent = `Phase: ${world.phase || 'Unknown'}`;
            if (world.game_over) {
                phaseDisplay.textContent = 'Phase: GAME OVER';
                phaseDisplay.style.color = '#ef4444';
            }
        }
    },

    /**
     * Update player resources display
     */
    updateResources(world) {
        const playerDeity = world.deities?.find(d => d.id === CONFIG.PLAYER_DEITY);
        
        if (playerDeity) {
            const resources = playerDeity.resources || {};
            
            this.updateElement('resource-power', resources.power || 0);
            this.updateElement('resource-faith', resources.faith || 0);
            this.updateElement('resource-code', resources.code || 0);
            this.updateElement('resource-entropy', resources.entropy || 0);
            
            // Update follower count
            const followerCount = playerDeity.follower_count || 0;
            this.updateElement('follower-count', followerCount);
            
            // Update building count (from world stats)
            const buildingCount = world.total_buildings || 0;
            this.updateElement('building-count', buildingCount);
        }
        
        // Update world stats
        this.updateElement('total-followers', world.total_followers || 0);
        this.updateElement('deity-count', world.deities?.length || 0);
        this.updateElement('region-count', world.regions?.length || 0);
    },

    /**
     * Update a single element's text content
     */
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    },

    /**
     * Populate region dropdowns
     */
    populateRegions(regions) {
        const dropdownIds = ['recruit-region', 'attack-region', 'miracle-region', 'build-region'];
        
        dropdownIds.forEach(dropdownId => {
            const dropdown = document.getElementById(dropdownId);
            if (!dropdown) return;
            
            // Save current selection
            const currentValue = dropdown.value;
            
            // Clear options except first
            while (dropdown.options.length > 1) {
                dropdown.remove(1);
            }
            
            // Add region options
            regions.forEach(region => {
                const option = document.createElement('option');
                option.value = region.id;
                option.textContent = region.name;
                dropdown.appendChild(option);
            });
            
            // Restore selection if valid
            if (currentValue && regions.find(r => r.id === currentValue)) {
                dropdown.value = currentValue;
            }
        });
    },

    /**
     * Populate deity dropdowns (for attack target selection)
     */
    populateDeities(deities) {
        const dropdown = document.getElementById('attack-target');
        if (!dropdown) return;
        
        // Clear options except first
        while (dropdown.options.length > 1) {
            dropdown.remove(1);
        }
        
        // Add deity options (excluding player)
        deities.forEach(deity => {
            if (deity.id !== CONFIG.PLAYER_DEITY) {
                const option = document.createElement('option');
                option.value = deity.id;
                option.textContent = `${deity.name} (${deity.faction || 'Unknown'})`;
                dropdown.appendChild(option);
            }
        });
    },

    /**
     * Render events list
     */
    renderEvents(events) {
        const eventsList = document.getElementById('events-list');
        if (!eventsList) return;
        
        if (!events || events.length === 0) {
            eventsList.textContent = '';
            const placeholder = document.createElement('div');
            placeholder.className = 'event-item system';
            placeholder.textContent = 'No events yet. Start playing to generate events!';
            eventsList.appendChild(placeholder);
            return;
        }

        eventsList.textContent = '';
        events.forEach(event => {
            const eventType = this.getEventType(event);
            const time = this.formatEventTime(event.timestamp);
            const message = this.formatEventMessage(event);

            const item = document.createElement('div');
            item.className = `event-item ${eventType}`;

            const timeEl = document.createElement('div');
            timeEl.className = 'event-time';
            timeEl.textContent = time;

            const msgEl = document.createElement('div');
            msgEl.className = 'event-message';
            msgEl.textContent = message;

            item.appendChild(timeEl);
            item.appendChild(msgEl);
            eventsList.appendChild(item);
        });
    },

    /**
     * Determine event type for styling
     */
    getEventType(event) {
        const eventType = event.type || event.event_type || '';
        
        if (eventType.includes('recruit')) return 'recruit';
        if (eventType.includes('attack')) return 'attack';
        if (eventType.includes('prayer')) return 'prayer';
        if (eventType.includes('miracle')) return 'miracle';
        if (eventType.includes('building')) return 'building_built';
        if (eventType.includes('turn')) return 'turn';
        
        return 'system';
    },

    /**
     * Format event timestamp
     */
    formatEventTime(timestamp) {
        if (!timestamp) return '';
        
        try {
            const date = new Date(timestamp);
            return date.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        } catch (e) {
            return String(timestamp).substring(0, 8);
        }
    },

    /**
     * Format event message for display
     */
    formatEventMessage(event) {
        const eventType = event.type || event.event_type || 'system';
        const data = event.data || {};
        
        switch (eventType) {
            case 'recruit':
                return `Recruited ${data.count || 0} follower(s) in ${data.region_id || 'unknown region'}`;
            case 'attack':
                return `Attack on ${data.target_deity_id || 'unknown'}: ${data.result || 'Battle in progress'}`;
            case 'prayer':
                return `Prayer answered: +${data.gain || 0} ${data.prayer_type || 'faith'}`;
            case 'miracle':
                return `Miracle performed: ${data.miracle_type || 'unknown'} in ${data.region_id || 'unknown'}`;
            case 'building_built':
                return `Built ${data.building_type || 'structure'} in ${data.region_id || 'unknown'}`;
            case 'turn':
                return `Turn ${data.turn || '?'} begins`;
            default:
                return JSON.stringify(event);
        }
    },

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        if (!notification) return;
        
        notification.textContent = message;
        notification.className = `notification ${type}`;
        
        // Auto-hide after duration
        setTimeout(() => {
            notification.classList.add('hidden');
        }, CONFIG.NOTIFICATION_DURATION);
    },

    /**
     * Show game over screen
     */
    showGameOver(winner, victoryCondition) {
        const overlay = document.createElement('div');
        overlay.className = 'game-over-overlay';

        const content = document.createElement('div');
        content.className = 'game-over-content';

        const heading = document.createElement('h2');
        heading.textContent = 'Victory!';

        const msg = document.createElement('p');
        msg.textContent = `${winner} has achieved ${victoryCondition}!`;

        const btn = document.createElement('button');
        btn.textContent = 'Play Again';
        btn.addEventListener('click', () => location.reload());

        content.appendChild(heading);
        content.appendChild(msg);
        content.appendChild(btn);
        overlay.appendChild(content);
        document.body.appendChild(overlay);
    },

    /**
     * Set loading state for a button
     */
    setButtonLoading(buttonId, loading) {
        const button = document.getElementById(buttonId);
        if (!button) return;
        
        if (loading) {
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.textContent = 'Processing...';
        } else {
            button.disabled = false;
            button.textContent = button.dataset.originalText || button.textContent;
        }
    }
};

// ========================================
// Form Handlers
// ========================================
const forms = {
    /**
     * Initialize all form handlers
     */
    init() {
        this.handleRecruit();
        this.handleAttack();
        this.handlePray();
        this.handleMiracle();
        this.handleBuild();
        this.handleTurn();
    },

    /**
     * Handle recruit form submission
     */
    handleRecruit() {
        const form = document.getElementById('recruit-form');
        if (!form) return;
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const regionId = document.getElementById('recruit-region').value;
            const count = document.getElementById('recruit-count').value;
            
            if (!regionId) {
                ui.showNotification('Please select a region', 'warning');
                return;
            }
            
            ui.setButtonLoading('recruit-btn', true);

            try {
                const result = await api.recruit({ region_id: regionId, count: parseInt(count, 10) });

                if (result.success) {
                    ui.showNotification(result.message, 'success');
                    await app.refresh();
                } else {
                    ui.showNotification(result.error || 'Failed to recruit', 'error');
                }
            } catch (error) {
                ui.showNotification(error.message, 'error');
            } finally {
                ui.setButtonLoading('recruit-btn', false);
            }
        });
    },

    /**
     * Handle attack form submission
     */
    handleAttack() {
        const form = document.getElementById('attack-form');
        if (!form) return;
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const targetDeityId = document.getElementById('attack-target').value;
            const regionId = document.getElementById('attack-region').value;
            
            if (!targetDeityId || !regionId) {
                ui.showNotification('Please select target and region', 'warning');
                return;
            }
            
            ui.setButtonLoading('attack-btn', true);

            try {
                const result = await api.attack({
                    target_deity_id: targetDeityId,
                    region_id: regionId
                });

                if (result.success) {
                    ui.showNotification(result.message, 'success');
                    await app.refresh();
                } else {
                    ui.showNotification(result.error || 'Attack failed', 'error');
                }
            } catch (error) {
                ui.showNotification(error.message, 'error');
            } finally {
                ui.setButtonLoading('attack-btn', false);
            }
        });
    },

    /**
     * Handle pray form submission
     */
    handlePray() {
        const form = document.getElementById('pray-form');
        if (!form) return;
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const prayerType = document.getElementById('pray-type').value;
            
            ui.setButtonLoading('pray-btn', true);

            try {
                const result = await api.pray({ prayer_type: prayerType });

                if (result.success) {
                    ui.showNotification(result.message, 'success');
                    await app.refresh();
                } else {
                    ui.showNotification(result.error || 'Prayer failed', 'error');
                }
            } catch (error) {
                ui.showNotification(error.message, 'error');
            } finally {
                ui.setButtonLoading('pray-btn', false);
            }
        });
    },

    /**
     * Handle miracle form submission
     */
    handleMiracle() {
        const form = document.getElementById('miracle-form');
        if (!form) return;
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const regionId = document.getElementById('miracle-region').value;
            const miracleType = document.getElementById('miracle-type').value;
            const intensity = document.getElementById('miracle-intensity').value;
            
            if (!regionId || !miracleType) {
                ui.showNotification('Please select region and miracle type', 'warning');
                return;
            }
            
            ui.setButtonLoading('miracle-btn', true);

            try {
                const result = await api.miracle({
                    region_id: regionId,
                    miracle_type: miracleType,
                    intensity: parseInt(intensity, 10)
                });

                if (result.success) {
                    ui.showNotification(result.message, 'success');
                    await app.refresh();
                } else {
                    ui.showNotification(result.error || 'Miracle failed', 'error');
                }
            } catch (error) {
                ui.showNotification(error.message, 'error');
            } finally {
                ui.setButtonLoading('miracle-btn', false);
            }
        });
    },

    /**
     * Handle build form submission
     */
    handleBuild() {
        const form = document.getElementById('build-form');
        if (!form) return;
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const buildingType = document.getElementById('build-type').value;
            const regionId = document.getElementById('build-region').value;
            
            if (!buildingType || !regionId) {
                ui.showNotification('Please select building type and region', 'warning');
                return;
            }
            
            ui.setButtonLoading('build-btn', true);

            try {
                const result = await api.build({
                    building_type: buildingType,
                    region_id: regionId
                });

                if (result.success) {
                    ui.showNotification(result.message, 'success');
                    await app.refresh();
                } else {
                    ui.showNotification(result.error || 'Build failed', 'error');
                }
            } catch (error) {
                ui.showNotification(error.message, 'error');
            } finally {
                ui.setButtonLoading('build-btn', false);
            }
        });
    },

    /**
     * Handle turn advancement
     */
    handleTurn() {
        const button = document.getElementById('advance-turn-btn');
        if (!button) return;
        
        button.addEventListener('click', async () => {
            ui.setButtonLoading('advance-turn-btn', true);
            
            try {
                const result = await api.advanceTurn();
                
                if (result.game_over) {
                    ui.showGameOver(result.winner, result.victory_condition);
                } else {
                    await app.refresh();
                    ui.showNotification(`Turn ${result.turn} begins!`, 'info');
                }
            } catch (error) {
                ui.showNotification(error.message, 'error');
            } finally {
                ui.setButtonLoading('advance-turn-btn', false);
            }
        });
    }
};

// ========================================
// Tab System
// ========================================
const tabs = {
    /**
     * Initialize tab switching
     */
    init() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.dataset.tab;
                this.switchTab(targetTab);
            });
        });
    },

    /**
     * Switch to a specific tab
     */
    switchTab(tabName) {
        // Update button states
        const tabButtons = document.querySelectorAll('.tab-btn');
        tabButtons.forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.tab === tabName) {
                btn.classList.add('active');
            }
        });
        
        // Update tab content
        const tabPanes = document.querySelectorAll('.tab-pane');
        tabPanes.forEach(pane => {
            pane.classList.remove('active');
            if (pane.id === `tab-${tabName}`) {
                pane.classList.add('active');
            }
        });
    }
};

// ========================================
// Main Application
// ========================================
const app = {
    /**
     * Initialize the application
     */
    async init() {
        console.log('AI Gods World - Initializing...');
        
        // Initialize UI components
        tabs.init();
        forms.init();
        
        // Initial data load
        await this.refresh();
        
        // Start polling for updates
        this.startPolling();
        
        console.log('AI Gods World - Ready!');
    },

    /**
     * Refresh all data from server
     */
    async refresh() {
        if (state.isLoading) return;
        state.isLoading = true;
        
        try {
            const worldData = await api.getState();
            
            state.world = worldData;
            state.events = worldData.events || [];
            
            // Update UI
            ui.updateHeader(worldData);
            ui.updateResources(worldData);
            
            // Populate dropdowns on first load
            if (worldData.regions) {
                ui.populateRegions(worldData.regions);
            }
            if (worldData.deities) {
                ui.populateDeities(worldData.deities);
            }
            
            // Render events
            ui.renderEvents(state.events);
            
            // Check for game over
            if (worldData.game_over) {
                ui.showGameOver(worldData.winner, worldData.victory_condition);
                this.stopPolling();
            }
            
        } catch (error) {
            console.error('Failed to refresh:', error);
            ui.showNotification('Failed to sync with server', 'error');
        } finally {
            state.isLoading = false;
        }
    },

    /**
     * Start periodic polling
     */
    startPolling() {
        if (state.pollTimer) return;
        
        state.pollTimer = setInterval(() => {
            this.refresh();
        }, CONFIG.POLL_INTERVAL);
    },

    /**
     * Stop periodic polling
     */
    stopPolling() {
        if (state.pollTimer) {
            clearInterval(state.pollTimer);
            state.pollTimer = null;
        }
    }
};

// ========================================
// Initialize when DOM is ready
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});

// Export for debugging
window.app = app;
window.api = api;
window.ui = ui;
