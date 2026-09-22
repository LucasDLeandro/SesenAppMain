window.initDashboardClientes = function(tiposLabels, tiposData, clientesLabels, valoresData) {
    // Configuração Gráfico de Tipos
    const ctxTipo = document.getElementById('tipoChart').getContext('2d');
    new Chart(ctxTipo, {
        type: 'doughnut',
        data: {
            labels: tiposLabels.map(l => String(l).toUpperCase()),
            datasets: [{
                data: tiposData,
                backgroundColor: ['#0d6efd', '#198754', '#0dcaf0', '#ffc107'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });

    // Configuração Gráfico de Valores
    const ctxValor = document.getElementById('valorChart').getContext('2d');
    new Chart(ctxValor, {
        type: 'bar',
        data: {
            labels: clientesLabels,
            datasets: [{
                label: 'Valor Total (R$)',
                data: valoresData,
                backgroundColor: '#6610f2',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { borderDash: [2, 4] }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
};
