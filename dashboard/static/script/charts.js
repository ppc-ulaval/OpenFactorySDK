class Charts{
    constructor(storageManager) {
        this.storage = storageManager;
        this.pieCharts = new Map();
        this.airQualityCharts = new Map();
        this.particleData = this.initializeParticleData();

        this.COLORS = ["#2F3061", "#ffb800", "#5BC0EB"];
        this.MAX_DATA_POINTS = 100;
        this.TIME_WINDOW_MINUTES = 5;
        
        this.chartConfigs = {
            pm1_concentration: {
                label: 'PM1',
                color: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                canvasId: 'pm1Chart'
            },
            pm2_5_concentration: {
                label: 'PM2.5',
                color: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                canvasId: 'pm25Chart'
            },
            pm4_concentration: {
                label: 'PM4',
                color: 'rgb(255, 205, 86)',
                backgroundColor: 'rgba(255, 205, 86, 0.1)',
                canvasId: 'pm4Chart'
            },
            pm10_concentration: {
                label: 'PM10',
                color: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                canvasId: 'pm10Chart'
            }
        };
    }

    initializeParticleData() {
        const data = {
            pm1_concentration: [],
            pm2_5_concentration: [],
            pm4_concentration: [],
            pm10_concentration: [],
        };

        const storedData = this.storage.loadParticleData(this.TIME_WINDOW_MINUTES);
        if(storedData) {
            Object.assign(data, storedData);
        }

        return data
    }

    initializePieCharts() {
        const toolElements = document.querySelectorAll('[id$="-pie-chart"]');

        toolElements.forEach(svg => {
            const dataitemId = svg.id.replace('-pie-chart', '');
            let chartData = this.storage.getChartDataForDevice(dataitemId);

            if(!chartData) {
                chartData = this.getDefaultChartData();
            }

            this.createPieChart(dataitemId, chartData);
        });
    }

    getDefaultChartData(){
        return {
            'OFF': 100,
            'ON':10,
            "UNAVAILABLE": 1
        };
    }

    createPieChart(dataitemId, data) {
        const svg = document.getElementById(dataitemId + '-pie-chart');
        if(!svg) return;

        const totalTime = Object.values(data).reduce((sum, val) => sum+val, 0);
        const labels = Object.keys(data);
        const values = Object.values(data);

        svg.innerHTML = '';

        const radius = 50;
        const centerX = 70;
        const centerY = 70;
        let currentAngle = -Math.PI /2;

        values.forEach((value, index) => {
             const sliceAngle = (value / totalTime) * 2 * Math.PI;
            const endAngle = currentAngle + sliceAngle;
            
            const x1 = centerX + radius * Math.cos(currentAngle);
            const y1 = centerY + radius * Math.sin(currentAngle);
            const x2 = centerX + radius * Math.cos(endAngle);
            const y2 = centerY + radius * Math.sin(endAngle);
            
            const largeArcFlag = sliceAngle > Math.PI ? 1 : 0;

            const pathData = [
                `M ${centerX} ${centerY}`,
                `L ${x1} ${y1}`,
                `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
                'Z'
            ].join(' ');
            
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', pathData);
            path.setAttribute('fill', this.COLORS[index % this.COLORS.length]);
            path.setAttribute('class', 'pie-slice');
            path.setAttribute('data-value', `${values[index].toFixed(1)}%`);
            path.setAttribute('data-label', labels[index] || `Item ${index + 1}`);
            
            svg.appendChild(path);
            
            currentAngle = endAngle;
        });

        this.updatePowerDurationText(dataitemId, totalTime);
        this.storage.saveChartData(dataitemId, data);
    }

    updatePowerDurationText(dataitemId, totalSeconds) {
        const powerDurationElem = document.getElementById(`${dataitemId}-power-duration`);
        if(!powerDurationElem) return;

        const minutes = totalSeconds / 60;
        const text = minutes > 2 
            ? `Total powered duration: ${minutes.toFixed(2)} minutes`
            : `Total powered duration: NA minutes`;

        powerDurationElem.innerText = text;
    }

    updateDeviceChart(dataitemId, analyticsData){
        this.createPieChart(dataitemId, analyticsData);
    }

    initializeAirQualityCharts() {
        Object.keys(this.chartConfigs).forEach(particleType => {
            const config = this.chartConfigs[particleType];
            const ctx = document.getElementById(config.canvasId);
            
            if (!ctx) {
                console.warn(`Canvas element not found: ${config.canvasId}`);
                return;
            }

            const timeRange = this.getOptimalTimeRange(particleType);

            this.airQualityCharts.set(particleType, new Chart(ctx, {
                type: 'line',
                data: {
                    datasets: [{
                        label: `${config.label} (µg/m³)`,
                        data: this.particleData[particleType] || [],
                        borderColor: config.color,
                        backgroundColor: config.backgroundColor,
                        fill: false,
                        tension: 0,
                        borderWidth: 2,
                        pointRadius: 0,
                        pointHoverRadius: 2,
                        spanGaps: false,
                        cubicInterpolationMode: 'monotone'
                    }]
                },
                options: this.getChartOptions(timeRange)
            }));
        });

        this.startRealTimeUpdates();
    }

    getChartOptions(timeRange) {
        return {
            responsive: true,
            interaction: { intersect: false },
            elements: { line: { tension: 0 } },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'second',
                        stepSize: 10,
                        displayFormats: { second: 'HH:mm:ss' }
                    },
                    display: true,
                    title: { display: true, text: 'Time' },
                    ticks: { maxTicksLimit: 10, source: 'auto' },
                    min: timeRange.min,
                    max: timeRange.max
                },
                y: {
                    display: true,
                    title: { display: true, text: 'Concentration (µg/m³)' },
                    beginAtZero: false,
                    ticks: { callback: (value) => value.toFixed(1) }
                }
            },
            animation: { duration: 0 }
        };
    }

    getOptimalTimeRange(particleType) {
        const now = new Date();
        const defaultRange = {
                min: new Date(now.getTime() - (this.TIME_WINDOW_MINUTES * 60 * 1000)),
                max: now
            };

        if(!this.particleData[particleType] || this.particleData[particleType].length === 0) {
            return defaultRange;
        }

        const data = this.particleData[particleType];
        const dataEnd = new Date(Math.max(...data.map(p =>p.x.getTime())));
        const timeSinceLastData = now.getTime() - dataEnd.getTime();
        const maxGapMs = 2 * 60 * 1000;
        
        if(timeSinceLastData > maxGapMs) {
            return {
                min: new Date(dataEnd.getTime() - (this.TIME_WINDOW_MINUTES * 60 * 1000)),
                max: dataEnd
            };
        }

        return defaultRange;
    }

    updateParticleConcentration(particleType, value, timestamp){
        if(!this.particleData[particleType]) return;

        const time = new Date(timestamp);
        console.log(value)
        const concentrationValue = this.convertToMicrogram(value);

        const existingIndex = this.particleData[particleType].findIndex(point => 
            Math.abs(point.x.getTime() - time.getTime()) < 1000
        );

        const dataPoint = { x: time, y: concentrationValue };

        if (existingIndex !== -1) {
            this.particleData[particleType][existingIndex] = dataPoint;
        } else {
            this.particleData[particleType].push(dataPoint);
        }

        this.particleData[particleType].sort((a, b) => a.x.getTime() - b.x.getTime());
        
        if (this.particleData[particleType].length > this.MAX_DATA_POINTS) {
            this.particleData[particleType] = this.particleData[particleType].slice(-this.MAX_DATA_POINTS);
        }

        this.updateSingleAirQualityChart(particleType);
        this.storage.saveParticleData(this.particleData);
    }

     updateSingleAirQualityChart(particleType) {
        const chart = this.airQualityCharts.get(particleType);
        if (!chart) return;

        const dataset = chart.data.datasets[0];
        dataset.data = [...this.particleData[particleType]];

        const timeRange = this.getOptimalTimeRange(particleType);
        chart.options.scales.x.min = timeRange.min;
        chart.options.scales.x.max = timeRange.max;

        chart.update('none');
    }

    convertToMicrogram(percentConcentration) {
        return (percentConcentration / 100) * 1225000 *1000;
    }

    startRealTimeUpdates() {
        setInterval(() => {
            this.updateAllAirQualityCharts();
            this.cleanupOldData();
        }, 1000);
    }

    updateAllAirQualityCharts() {
        this.airQualityCharts.forEach((chart, particleType) => {
            const timeRange = this.getOptimalTimeRange(particleType);
            chart.options.scales.x.min = timeRange.min;
            chart.options.scales.x.max = timeRange.max;
            chart.update('none');
        });
    }

    cleanupOldData() {
        const cutoffTime = new Date(Date.now() - (this.TIME_WINDOW_MINUTES * 2 * 60 * 1000));
        let dataChanged = false;

        Object.keys(this.particleData).forEach(particleType => {
            const originalLength = this.particleData[particleType].length;
            this.particleData[particleType] = this.particleData[particleType]
                .filter(point => point.x >= cutoffTime);

            if (this.particleData[particleType].length !== originalLength) {
                dataChanged = true;
            }
        });

        if (dataChanged) {
            this.storage.saveParticleData(this.particleData);
        }
    }
}