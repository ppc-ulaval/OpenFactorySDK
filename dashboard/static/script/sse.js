class SSEConnection{
    constructor(){
        this.eventSource = null;
        this.reconnectAttemps = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.listeners = new Map();
    }

    connect(){
        if(this.eventSource){
            this.eventSource.close();
        }

        this.eventSource = new EventSource('/updates/all');

        this.eventSource.onopen = () => {
            this.reconnectAttempts = 0;
            this.emit('connected');
        };

        this.eventSource.onmessage = (event) => {
            try{
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Error parsing message:', error);
            }
        };

        this.eventSource.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.handleReconnect();
        };
    }

    handleMessage(data){
        if(data.event){
            this.emit(data.event, data);
        } else {
            this.emit('deviceUpdate', data);
        }
    }

    handleReconnect(){
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts ++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

            setTimeout(()=>{
                console.log(`Reconnecting.. attempts ${this.reconnectAttempts}`);
                this.connect();
            }, delay);
        } else {
            console.error('Max reconnection attemps reached');
            this.emit('connectionFailed');
        }
    }

    on(event, callback){
        if(!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    off(event, callback){
        if(this.listeners.has(event)) {
            const callbacks = this.listeners.get(event);
            const index = callbacks.indexOf(callback);
            if(index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }

    emit(event, data = null) {
        if(this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => callback(data));
        }
    }

    disconnect(){
        if(this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
    }

    async sendSimulationMode(deviceUuid) {
        const checkbox = document.querySelector('.switch input[type="checkbox"]');
        const enabled = checkbox.checked;
        try {
            const response = await fetch(`/simulation-mode/${deviceUuid}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ enabled: enabled })
            });

            if (!response.ok) {
                throw new Error('Failed to update simulation mode');
            }

            return await response.json();
        } catch (error) {
            console.error('Error updating simulation mode:', error);
            throw error;
        }
    }
}
