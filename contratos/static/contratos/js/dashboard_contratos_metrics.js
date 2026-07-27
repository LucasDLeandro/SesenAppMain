    const formatBRL = (value) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    };

    const formatDateBR = (isoDate) => {
        if (!isoDate) return '-';
        const parts = isoDate.split('-');
        return `${parts[2]}/${parts[1]}/${parts[0]}`;
    };

    let chartExecucao = null;

    const carregarMetricas = async () => {
        try {
            const contrato_id = document.getElementById('filtro-global-contrato')?.value || '';
            const mes = document.getElementById('filtro-global-mes')?.value || '';
            const ano = document.getElementById('filtro-global-ano')?.value || '';

            const params = new URLSearchParams();
            if (contrato_id) params.append('contrato_id', contrato_id);
            if (mes) params.append('mes', mes);
            if (ano) params.append('ano', ano);

            const response = await fetch(`/contratos/api/dashboard-metrics/?${params.toString()}`);
            const data = await response.json();

            // Populate Top Metrics
            document.getElementById('val-global').innerText = formatBRL(data.valor_total_contratos);
            document.getElementById('val-estimado').innerText = formatBRL(data.valor_estimado);
            document.getElementById('val-pago').innerText = formatBRL(data.valor_pago);
            document.getElementById('val-glosas').innerText = formatBRL(data.total_glosas);
            
            // Populate Upcoming Expirations
            const tbody = document.getElementById('lista-vencimentos');
            if (tbody) {
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
            }

            // Render ApexChart
            if (data.chart_data && document.querySelector("#chart-execucao")) {
                const options = {
                    series: [{
                        name: 'Valor Estimado',
                        data: data.chart_data.estimado
                    }, {
                        name: 'Valor Pago',
                        data: data.chart_data.medido
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
                        categories: data.chart_data.categories,
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

                if (chartExecucao) {
                    chartExecucao.updateOptions(options);
                } else {
                    chartExecucao = new ApexCharts(document.querySelector("#chart-execucao"), options);
                    chartExecucao.render();
                }
            }

        } catch (error) {
            console.error("Erro ao buscar métricas:", error);
        }
    };

    // Expose to global scope so main JS can call it
    window.carregarMetricas = carregarMetricas;

    document.addEventListener('DOMContentLoaded', () => {
        carregarMetricas();
    });
