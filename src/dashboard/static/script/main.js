class Dashboard {
    constructor() {
        this.storage = new Storage();
        this.deviceManager = new Devices(this.storage);
        this.chartManager = new Charts(this.storage);
        this.sseClient = new SSEConnection();
        
        this.initialized = false;
        this.setupEventListeners();
    }

    async initialize() {
        if (this.initialized) return;

        try {
            console.log('Initializing Dust Collection App...');
            
            this.initializeActiveTab();
            this.restoreSimulationMode();
            this.initializeJsPlumb();
            
            this.chartManager.initializePieCharts();
            this.chartManager.initializeAirQualityCharts();
            
            this.sseClient.connect();
            
            this.initialized = true;
            console.log('Dust Collection App initialized successfully');
        } catch (error) {
            console.error('Failed to initialize app:', error);
            throw error;
        }
    }

    setupEventListeners() {
        this.sseClient.on('connected', () => {
            console.log('Connected to server');
        });

        this.sseClient.on('deviceUpdate', (data) => {
            console.log(data)
            this.handleDeviceUpdate(data);
        });

        this.sseClient.on('connection_established', (data) => {
            this.handleConnectionEstablished(data);
        });

        this.sseClient.on('simulation_mode_updated', (data) => {
            this.handleSimulationModeUpdate(data);
        });

        this.deviceManager.on('deviceUpdated', (data) => {
            if (data.metadata.durations) {
                this.chartManager.updateDeviceChart(data.dataitemId, data.metadata.durations);
            }
        });

        document.addEventListener('DOMContentLoaded', () => {
            this.initialize();
        });

        const simulationToggle = document.querySelector('.switch input[type="checkbox"]');
        if (simulationToggle) {
            simulationToggle.addEventListener('change', () => {
                this.handleSimulationToggle();
            });
        }
    }

    handleDeviceUpdate(msg) {
        const { device_uuid: deviceUuid, data: data } = msg;
        const {ID: dataitemId, VALUE: value} = data;

        if (!deviceUuid) {
            console.warn('Could not extract device ID from:', dataitemId);
            return;
        }

        if (dataitemId.includes('concentration')) {
            this.handleConcentrationUpdate(data);
        }

        this.deviceManager.updateDevice(deviceUuid, dataitemId, value, {
            durations: data.durations,
            avgValue: data.avg_value,
            timestamp: data.timestamp
        });
    }

    handleConcentrationUpdate(data) {
        const { ID: dataitemId, VALUE: value, avg_value, timestamp } = data;
        
        if (avg_value && Object.keys(avg_value).length > 0) {
            this.chartManager.updateParticleConcentration(
                dataitemId, 
                avg_value.value, 
                avg_value.timestamp
            );
        }
        
        const processedValue = this.chartManager.convertToMicrogram(value);
        this.updateConcentrationDisplay(dataitemId, processedValue);
    }

    handleConnectionEstablished(data) {
        const { device_uuid: deviceUuid, data_items: dataitems } = data;
        this.deviceManager.initializeDevice(deviceUuid, dataitems);
        console.log(`Device ${deviceUuid} connection established`);
    }

    handleSimulationModeUpdate(data) {
        if (data.success) {
            this.storage.saveSimulationMode(data.value);
            console.log('Simulation mode updated:', data.value);
        } else {
            console.error('Failed to update simulation mode:', data.error);
            this.revertSimulationToggle();
        }
    }

    async handleSimulationToggle() {
        const checkbox = document.querySelector('.switch input[type="checkbox"]');
        const deviceUuid = document.querySelector('meta[name="device-uuid"]')?.content;
        
        if (!deviceUuid) {
            console.error('Device UUID not found');
            this.revertSimulationToggle();
            return;
        }

        try {
            await this.sseClient.sendSimulationMode(deviceUuid, checkbox.checked);
        } catch (error) {
            console.error('Error updating simulation mode:', error);
            this.revertSimulationToggle();
            alert('Failed to update simulation mode. Please try again.');
        }
    }

    revertSimulationToggle() {
        const checkbox = document.querySelector('.switch input[type="checkbox"]');
        if (checkbox) {
            checkbox.checked = !checkbox.checked;
        }
    }

    updateConcentrationDisplay(dataitemId, value) {
        const displayElement = document.getElementById(dataitemId);
        if (displayElement) {
            displayElement.textContent = `${value.toFixed(3)} µg/m³`;
        }
        
        const valueOnlyElement = document.getElementById(`${dataitemId}_value`);
        if (valueOnlyElement) {
            valueOnlyElement.textContent = value.toFixed(3);
        }
    }

    extractDeviceUuid(dataItemId) {
        const match = dataItemId.match(/^([^_]+)/);
        return match ? match[1] : null;
    }

    initializeActiveTab() {
        const path = window.location.pathname;
        const matches = path.match(/\/devices\/([^\/]+)/);
        if (matches && matches[1]) {
            this.selectTab(matches[1]);
        }
    }

    selectTab(deviceUuid) {
        console.log("Tab selected for device:", deviceUuid);
        
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        const selectedTab = document.getElementById(`${deviceUuid}_tab`);
        if (selectedTab) {
            selectedTab.classList.add('active');
        }
    }

    restoreSimulationMode() {
        const checkbox = document.querySelector('.switch input[type="checkbox"]');
        if (checkbox) {
            const storedMode = this.storage.getSimulationMode();
            checkbox.checked = storedMode;
        }
    }

    initializeJsPlumb() {
        if (typeof jsPlumb === 'undefined') {
            console.warn('jsPlumb not available, skipping connection visualization');
            return;
        }

        jsPlumb.ready(() => {
            jsPlumb.setContainer("jsplumb-container");

            const spindleCards = Array.from(document.querySelectorAll('.spindle-card'));
            const gateCards = Array.from(document.querySelectorAll('.gate-card'));
            const dustCollectorCard = document.querySelector('.dust-collector-card');

            // Connect spindles to matching gates
            spindleCards.forEach(spindle => {
                const spindlePrefix = spindle.id;

                gateCards.forEach(gate => {
                    const gateId = gate.id.replace('card-', '');
                    const gatePrefix = this.deviceManager.getDevicePrefix(gateId);
                    
                    if (spindlePrefix === gatePrefix) {
                        jsPlumb.connect({
                            source: spindle.id,
                            target: gate.id,
                            anchors: ["Top", "Top"],
                            endpoint: "Blank",
                            connector: ["Flowchart", { stub: 20, gap: 0, cornerRadius: 5 }],
                            paintStyle: { stroke: "#222", strokeWidth: 15 },
                            overlays: [] 
                        });
                    }
                });
            });

            if (dustCollectorCard) {
                gateCards.forEach(gate => {
                    jsPlumb.connect({
                            source: gate.id,
                            target: dustCollectorCard.id,
                            anchors: ["Right", "Left"],
                            endpoint: "Blank",
                            connector: ["Flowchart", { stub: 20, gap: 0, cornerRadius: 5 }],
                            paintStyle: { stroke: "#222", strokeWidth: 15 },
                            overlays: [] 
                        });
                });
            }
        });
    }

    getDevice(deviceUuid) {
        return this.deviceManager.getDevice(deviceUuid);
    }

    getAllDevices() {
        return this.deviceManager.getAllDevices();
    }

    getDeviceStatus(deviceUuid) {
        return this.deviceManager.getDeviceStatus(deviceUuid);
    }

    destroy() {
        if (this.sseClient) {
            this.sseClient.disconnect();
        }
        
        if (this.chartManager && this.chartManager.airQualityCharts) {
            this.chartManager.airQualityCharts.forEach(chart => {
                if (chart && typeof chart.destroy === 'function') {
                    chart.destroy();
                }
            });
        }
        
        this.initialized = false;
    }
}

const dashboard = new Dashboard();
