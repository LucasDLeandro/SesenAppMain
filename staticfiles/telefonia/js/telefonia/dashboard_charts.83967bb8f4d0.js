document.addEventListener('DOMContentLoaded', async function() {
    try {
        const response = await fetch('/telefonia/api/stats/');
        const data = await response.json();

        // 1. Gráfico de Solicitações (Pie)
        const ctxSol = document.getElementById('chartSolicitacoes');
        if (ctxSol && data.solicitacoes) {
            const labelsSol = data.solicitacoes.map(item => item.status.toUpperCase());
            const dataSol = data.solicitacoes.map(item => item.total);
            const colorsSol = data.solicitacoes.map(item => {
                if(item.status === 'pendente' || item.status === 'em_analise') return '#ffc107'; // warning
                if(item.status === 'concluida') return '#198754'; // success
                if(item.status === 'rejeitada' || item.status === 'cancelada') return '#dc3545'; // danger
                return '#0d6efd'; // primary
            });

            new Chart(ctxSol, {
                type: 'doughnut',
                data: {
                    labels: labelsSol,
                    datasets: [{
                        data: dataSol,
                        backgroundColor: colorsSol,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right' }
                    }
                }
            });
        }

        // 2. Gráfico de Aparelhos (Bar)
        const ctxAp = document.getElementById('chartAparelhos');
        if (ctxAp && data.aparelhos) {
            const labelsAp = data.aparelhos.map(item => item.status.toUpperCase());
            const dataAp = data.aparelhos.map(item => item.total);
            const colorsAp = data.aparelhos.map(item => {
                if(item.status === 'estoque') return '#0dcaf0'; // info
                if(item.status === 'instalado') return '#198754'; // success
                if(item.status === 'defeituoso') return '#dc3545'; // danger
                return '#6c757d'; // secondary
            });

            new Chart(ctxAp, {
                type: 'bar',
                data: {
                    labels: labelsAp,
                    datasets: [{
                        label: 'Qtd Aparelhos',
                        data: dataAp,
                        backgroundColor: colorsAp,
                        borderRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Erro ao carregar dados dos gráficos da telefonia:', error);
    }
});
