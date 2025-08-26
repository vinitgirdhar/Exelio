// Chart.js default configuration and utilities
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.color = '#6c757d';

// Default color palettes
const CHART_COLORS = {
    primary: '#0d6efd',
    success: '#198754',
    danger: '#dc3545',
    warning: '#ffc107',
    info: '#0dcaf0',
    light: '#f8f9fa',
    dark: '#212529',
    secondary: '#6c757d'
};

const CHART_PALETTE = [
    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF',
    '#4BC0C0', '#36A2EB', '#FF6384', '#FFCE56'
];

// Utility function to generate random colors
function generateColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(CHART_PALETTE[i % CHART_PALETTE.length]);
    }
    return colors;
}

// Chart configuration presets
const CHART_CONFIGS = {
    bar: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                backgroundColor: 'rgba(0,0,0,0.8)',
                titleColor: '#fff',
                bodyColor: '#fff',
                borderColor: '#444',
                borderWidth: 1
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(255,255,255,0.1)'
                },
                ticks: {
                    color: '#6c757d'
                }
            },
            x: {
                grid: {
                    color: 'rgba(255,255,255,0.1)'
                },
                ticks: {
                    color: '#6c757d'
                }
            }
        }
    },
    
    line: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                labels: {
                    color: '#6c757d'
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0,0,0,0.8)',
                titleColor: '#fff',
                bodyColor: '#fff',
                borderColor: '#444',
                borderWidth: 1
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(255,255,255,0.1)'
                },
                ticks: {
                    color: '#6c757d'
                }
            },
            x: {
                grid: {
                    color: 'rgba(255,255,255,0.1)'
                },
                ticks: {
                    color: '#6c757d'
                }
            }
        }
    },
    
    scatter: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                labels: {
                    color: '#6c757d'
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0,0,0,0.8)',
                titleColor: '#fff',
                bodyColor: '#fff',
                borderColor: '#444',
                borderWidth: 1
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(255,255,255,0.1)'
                },
                ticks: {
                    color: '#6c757d'
                }
            },
            x: {
                type: 'linear',
                position: 'bottom',
                grid: {
                    color: 'rgba(255,255,255,0.1)'
                },
                ticks: {
                    color: '#6c757d'
                }
            }
        }
    },
    
    pie: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'right',
                labels: {
                    color: '#6c757d',
                    usePointStyle: true,
                    padding: 15
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0,0,0,0.8)',
                titleColor: '#fff',
                bodyColor: '#fff',
                borderColor: '#444',
                borderWidth: 1,
                callbacks: {
                    label: function(context) {
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = ((context.parsed / total) * 100).toFixed(1);
                        return `${context.label}: ${context.parsed} (${percentage}%)`;
                    }
                }
            }
        }
    }
};

// Function to create a chart with preset configuration
function createChart(canvas, type, data, customOptions = {}) {
    const baseConfig = CHART_CONFIGS[type] || CHART_CONFIGS.bar;
    
    const config = {
        type: type,
        data: data,
        options: {
            ...baseConfig,
            ...customOptions
        }
    };
    
    return new Chart(canvas, config);
}

// Function to format numbers for display
function formatNumber(num) {
    if (typeof num !== 'number') return num;
    
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toFixed(0);
}

// Function to download chart as image
function downloadChart(chart, filename = 'chart.png') {
    const url = chart.toBase64Image();
    const link = document.createElement('a');
    link.download = filename;
    link.href = url;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Animation helper for chart updates
function animateChart(chart, newData) {
    chart.data = newData;
    chart.update('active');
}

// Responsive chart helper
function makeChartResponsive(chart) {
    window.addEventListener('resize', function() {
        chart.resize();
    });
}

// Export functions for global use
window.ChartUtils = {
    CHART_COLORS,
    CHART_PALETTE,
    CHART_CONFIGS,
    generateColors,
    createChart,
    formatNumber,
    downloadChart,
    animateChart,
    makeChartResponsive
};
