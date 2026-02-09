class Devices{
    constructor(storageManager) {
        this.storage = storageManager;
        this.devices = new Map();
        this.listeners = new Map();

        this.restoreDeviceStates();
    }

    on(event, callback) {
        if(!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    emit(event, data) {
        if(this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => callback(data));
        }
    }

    restoreDeviceStates() {
        const savedStates = this.storage.getDeviceStates();
        
        Object.entries(savedStates).forEach(([deviceUuid, dataitems]) => {
            this.devices.set(deviceUuid, {
                uuid: deviceUuid,
                dataitems: new Map(Object.entries(dataitems)),
                lastUpdate: Date.now() - 30000
            });
            
            this.updateDeviceUI(dataitems);
        });
        
        console.log('Restored device states:', savedStates);
    }

    initializeDevice(deviceUuid, dataitems) {
        // Get existing saved state for this device
        const existingSavedState = this.storage.getDeviceState(deviceUuid);
        
        // Merge new dataitems with existing saved state (saved state takes precedence)
        const mergedDataitems = { ...dataitems, ...existingSavedState };
        
        this.devices.set(deviceUuid, {
            uuid: deviceUuid,
            dataitems: new Map(Object.entries(mergedDataitems)),
            lastUpdate: Date.now()
        });

        // Save the merged state (don't overwrite existing states for other devices)
        this.storage.saveDeviceState(deviceUuid, mergedDataitems);
        
        // Update UI with merged state
        this.updateDeviceUI(mergedDataitems);
        this.emit('deviceInitialized', { deviceUuid, dataitems: mergedDataitems });
    }

    updateDevice(deviceUuid, dataitemId, value, metadata = {}) {
        if (!this.devices.has(deviceUuid)) {
            console.warn(`Device ${deviceUuid} not found, creating new device`);
            this.devices.set(deviceUuid, {
                uuid: deviceUuid,
                dataitems: new Map(),
                lastUpdate: Date.now()
            });
        }

        const device = this.devices.get(deviceUuid);
        const lastState = device.dataitems.get(dataitemId);

        device.dataitems.set(dataitemId, value);
        device.lastUpdate = Date.now();

        this.storage.updateDeviceState(deviceUuid, dataitemId, value);
        this.updateDataitemUI(dataitemId, value);

        this.emit('deviceUpdated', {
            deviceUuid,
            dataitemId,
            value,
            lastState,
            metadata
        });
    }

    updateDeviceUI(dataitems) {
        Object.entries(dataitems).forEach(([id, value]) => {
            this.updateDataitemUI(id, value);
        });
    }

     updateDataitemUI(dataitemId, value){
        const dataitemElem = document.getElementById(dataitemId);
        if(!dataitemElem) return;

        if (dataitemId.includes('Tool')) {
            this.updateToolUI(dataitemElem, value);
        } else if (dataitemId.includes('Gate')) {
            this.updateGateUI(dataitemElem, value);
        } else if (dataitemId.includes('concentration')) {
            this.updateConcentrationUI(dataitemElem, value);
        }
    }

    updateToolUI(element, value){
        element.style.color = (value === "ON" ? "#6ed43f" : "red");
        if (element.parentElement) {
            element.parentElement.style.border = (value === "ON" ? "2px solid #6ed43f" : "2px solid red");
        }
    }
    
    updateGateUI(element, value) {
        element.src = (value === "OPEN" 
                ? "../static/icons/blast-gate-open.png" 
                : "../static/icons/blast-gate-closed.png");
    }

    updateConcentrationUI(element, value) {
        ////
    }

    getDevice(deviceUuid){
        return this.devices.get(deviceUuid);
    }

    getAllDevices(){
        return Array.from(this.devices.values());
    }

    getDevicePrefix(deviceUuid) {
        const match = deviceUuid.match(/^([A-Z]+\d+)/);
        return match ? match[1] : deviceUuid.substring(0, 2);
    }

    isDeviceOnline(deviceUuid, timeoutSeconds= 30){
        const device = this.devices.get(deviceUuid);
        if(!device) return false;

        const timeoutMs = timeoutSeconds * 1000;
        return (Date.now() - device.lastUpdate) < timeoutMs;
    }

    getDeviceStatus(deviceUuid) {
        const device = this.devices.get(deviceUuid);
        if(!device) return 'unknown';

        return this.isDeviceOnline(deviceUuid) ? 'online' : 'offline'
    }
}