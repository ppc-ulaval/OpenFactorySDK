class Storage{
    constructor() {
        this.storage = sessionStorage;
        this.keys = {
            DEVICE_STATES: 'deviceStates',
            CHART_DATA: 'chartData',
            PARTICLE_DATA: 'particleData',
            PARTICLE_METADATA: 'particleMetadata',
            SIMULATION_MODE: 'simulationMode'
        };
    }

    set(key, value) {
        try{
            this.storage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error(`Failed to save ${key}:`, error);
            return false;
        }
    }

    get(key, defaultValue = null) {
        try {
            const item = this.storage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error(`Failed to load ${key}:`, error);
            return defaultValue;
        }
    }

    remove(key){
        try {
            this.storage.removeItem(key);
            return true;
        } catch (error) {
            console.error(`Failed to remove ${key}:`, error);
            return false;
        }
    }

    clear() {
        this.storage.clear();
    }

    getDeviceStates() {
        return this.get(this.keys.DEVICE_STATES, {});
    }

    getDeviceState(deviceUuid){
        const states = this.getDeviceStates();
        return states[deviceUuid] || {};
    }

    saveDeviceState(deviceUuid, dataitems){
        const existingStates = this.getDeviceStates();
        existingStates[deviceUuid] = { ...existingStates[deviceUuid], ...dataitems };
        return this.saveDeviceStates(existingStates);
    }

    saveDeviceStates(states) {
        return this.set(this.keys.DEVICE_STATES, states);
    }

    updateDeviceState(deviceUuid, dataitemId, value) {
        const states = this.getDeviceStates();
        if(!states[deviceUuid]) {
            states[deviceUuid] = {};
        }
        states[deviceUuid][dataitemId] = value;
        return this.saveDeviceStates(states);
    }

    getChartData(){
        return this.get(this.keys.CHART_DATA, {});
    }

    saveChartData(dataitemId, data, deviceUuid = null) {
        const chartData = this.getChartData();

        if (deviceUuid) {
            if (!chartData[deviceUuid]) {
                chartData[deviceUuid] = {};
            }
            chartData[deviceUuid][dataitemId] = data;
        } else {
            chartData[dataitemId] = data;
        }
        return this.set(this.keys.CHART_DATA, chartData);
       
    }

    getChartDataForDevice(dataitemId, deviceUuid = null) {
        const chartData = this.getChartData();

        if(deviceUuid && chartData[deviceUuid]) {
            return chartData[deviceUuid][dataitemId] || null;
        }

        return chartData[dataitemId] || null;
    }

    getParticleData(){
        return this.get(this.keys.PARTICLE_DATA, {});
    }

    saveParticleData(data){
        const storageData = {};

        Object.keys(data).forEach(type => {
            storageData[type] = data[type].map(point => ({
                x: point.x.getTime(),
                y: point.y
            }));
        });

        const success = this.set(this.keys.PARTICLE_DATA, storageData);

        if(success) {
            this.saveParticleMetadata(data);
        }

        return success;
    }

    saveParticleMetadata(data) {
        const metadata = {
            lastUpdate: Date.now(),
            dataRanges: {}
        };

        Object.keys(data).forEach(type => {
            if (data[type].length > 0) {
                metadata.dataRanges[type] = {
                    start: Math.min(...data[type].map(p => p.x.getTime())),
                    end: Math.max(...data[type].map(p => p.x.getTime())),
                    count: data[type].length
                };
            }
        });

        return this.set(this.keys.PARTICLE_METADATA, metadata);
    }

    loadParticleData(timeWindowMinutes = 5) {
        const storedData = this.get(this.keys.PARTICLE_DATA);

        if(!storedData) return null;

        const cutoffTime = Date.now() - (timeWindowMinutes * 2* 60 * 1000);
        const loadedData = {};

        Object.keys(storedData).forEach(type => {
            loadedData[type] = storedData[type]
                .map(point => ({
                    x: new Date(point.x),
                    y: point.y
                }))
                .filter(point => point.x.getTime() >= cutoffTime)
                .sort((a, b) => a.x.getTime() - b.x.getTime());
        });

        return loadedData;
    }

    getSimulationMode() {
        return this.get(this.keys.SIMULATION_MODE, false);
    }

    saveSimulationMode(enabled){
        return this.set(this.keys.SIMULATION_MODE, enabled);
    }
}