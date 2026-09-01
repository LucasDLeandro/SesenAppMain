    const formatBRL = (value) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    };

    const formatDateBR = (isoDate) => {
        if (!isoDate) return '-';
        const parts = isoDate.split('-');
        return `${parts[2]}/${parts[1]}/${parts[0]}`;
    };

    document.addEventListener('DOMContentLoaded', async () => {
        try {
            const response = await fetch('/contratos/api/dashboard-metrics/');
            const data = await response.json();

            // Populate Top Metrics
            document.getElementById('val-ativos').innerText = data.total_ativos;
            document.getElementById('val-estimado').innerText = formatBRL(data.valor_estimado);
            document.getElementById('val-glosas').innerText = formatBRL(data.total_glosas);
            
            const processosTot = (data.processos_planejamento || 0) + (data.processos_selecao || 0);
            document.getElementById('val-processos').innerText = processosTot;

            // Populate Upcoming Expirations
            const tbody = document.getElementById('lista-vencimentos');
            tbody.innerHTML = '';
            if (data.proximos_vencer && data.proximos_vencer.length > 0) {
                data.proximos_vencer.forEach(c => {
                    tbody.innerHTML += `
                        <tr>
                            <td class="ps-4">
                                <div class="fw-bold text-dark">${c.num_contrato}</div>
                                <div class="small text-muted text-truncate" style="max-width: 150px;">${c.empresa}</div>
                            </td>
                            <td><span class="badge bg-warning text-dark px-2 py-1 rounded-pill">${formatDateBR(c.termino_vigencia)}</span></td>
                        </tr>
                    `;
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="2" class="text-center py-4 text-muted">Nenhum contrato próximo ao vencimento.</td></tr>';
            }

            // Render ApexChart
            const options = {
                series: [{
                    name: 'Valor Estimado',
                    data: [data.valor_estimado, data.valor_estimado, data.valor_estimado, data.valor_estimado, data.valor_estimado, data.valor_estimado]
                }, {
                    name: 'Valor Medido',
                    data: [0, 0, 0, 0, 0, data.total_medido] // Simplificado, idealmente viria do backend mês a mês
                }],
                chart: {
                    type: 'bar',
                    height: 320,
                    toolbar: { show: false },
                    fontFamily: 'inherit'
                },
                plotOptions: {
                    bar: {
                        horizontal: false,
                        columnWidth: '55%',
                        borderRadius: 4
                    },
                },
                dataLabels: { enabled: false },
                stroke: { show: true, width: 2, colors: ['transparent'] },
                xaxis: {
                    categories: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'], // Mock categories
                },
                yaxis: {
                    labels: {
                        formatter: function (val) {
                            return "R$ " + (val/1000).toFixed(0) + "k";
                        }
                    }
                },
                fill: { opacity: 1 },
                colors: ['#3498db', '#2ecc71'],
                tooltip: {
                    y: { formatter: function (val) { return formatBRL(val); } }
                }
            };
            const chart = new ApexCharts(document.querySelector("#chart-execucao"), options);
            chart.render();

        } catch (error) {
            console.error("Erro ao buscar métricas:", error);
        }
    });
</script>
