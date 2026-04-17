export function formatDataIso(data) {
    const yyyy = data.getFullYear();
    const mm = String(data.getMonth() + 1).padStart(2, '0');
    const dd = String(data.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
}

export function mesAnoAtual() {
    const agora = new Date();
    const ano = agora.getFullYear();
    const mes = agora.getMonth();

    const dataDiaInicio = new Date(ano, mes, 1)
    const dataDiaFim = new Date(ano, mes + 1, 0)

    return {
        inicio: dataDiaInicio,
        fim: dataDiaFim,
        ano_atual: ano,
        mes_atual: mes,
    }
}