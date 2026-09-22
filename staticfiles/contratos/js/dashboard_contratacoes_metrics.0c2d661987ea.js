    const formatBRL = (value) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(value);
    };

    document.addEventListener('DOMContentLoaded', async () => {
        try {
            // Fetch Contratações metrics
            const response = await fetch('/contratos/api/dashboard-contratacoes-metrics/');
            const data = await response.json();

            document.getElementById('val-processos').innerText = data.total_processos;
            document.getElementById('val-estimado').innerText = formatBRL(data.valor_estimado_total);
            document.getElementById('val-pac').innerText = data.no_pac;
            document.getElementById('val-atrasados').innerText = data.atrasados;

            // Fetch overall metrics for the phases chart
            const responseGeral = await fetch('/contratos/api/dashboard-metrics/');
            const dataGeral = await responseGeral.json();

            // Render ApexChart (Donut)
            const options = {
                series: [dataGeral.processos_planejamento || 0, dataGeral.processos_selecao || 0],
                labels: ['Planejamento', 'Seleção Fornecedor'],
                chart: {
                    type: 'donut',
                    height: 320,
                    fontFamily: 'inherit'
                },
                plotOptions: {
                    pie: {
                        donut: {
                            size: '65%',
                            labels: {
                                show: true,
                                name: { show: true },
                                value: { show: true }
                            }
                        }
                    }
                },
                dataLabels: { enabled: false },
                colors: ['#3498db', '#9b59b6'],
                legend: { position: 'bottom' }
            };
            const chart = new ApexCharts(document.querySelector("#chart-fases"), options);
            chart.render();

        } catch (error) {
            console.error("Erro ao buscar métricas:", error);
        }
    });
</script>
