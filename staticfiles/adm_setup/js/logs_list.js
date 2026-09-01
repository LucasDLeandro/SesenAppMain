const dtLanguage = {
    "sEmptyTable": "Nenhum log encontrado",
    "sInfo": "Mostrando de _START_ até _END_ de _TOTAL_ registros",
    "sInfoEmpty": "Mostrando 0 até 0 de 0 registros",
    "sInfoFiltered": "(Filtrados de _MAX_ registros)",
    "sLengthMenu": "Mostrar _MENU_ resultados por página",
    "sLoadingRecords": "Carregando...",
    "sProcessing": "Processando...",
    "sZeroRecords": "Nenhum registro encontrado",
    "sSearch": "Pesquisar:",
    "oPaginate": {
        "sNext": "Próximo",
        "sPrevious": "Anterior",
        "sFirst": "Primeiro",
        "sLast": "Último"
    },
    "oAria": {
        "sSortAscending": ": Ordenar colunas de forma ascendente",
        "sSortDescending": ": Ordenar colunas de forma descendente"
    }
};

$(document).ready(function() {
    $('#tabela-logs').DataTable({
        ajax: {
            url: '/logs/api/system-logs/',
            dataSrc: ''
        },
        columns: [
            { 
                data: 'timestamp',
                render: function(data) {
                    if(!data) return '-';
                    let d = new Date(data);
                    return d.toLocaleDateString('pt-BR') + ' às ' + d.toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'});
                }
            },
            { data: 'usuario' },
            { 
                data: 'action',
                render: function(data) {
                    if (data === 'CREATE') return '<span class="badge bg-success">Criação</span>';
                    if (data === 'UPDATE') return '<span class="badge bg-warning text-dark">Atualização</span>';
                    if (data === 'DELETE') return '<span class="badge bg-danger">Exclusão</span>';
                    return data;
                }
            },
            { data: 'modulo' },
            { data: 'object_id' },
            {
                data: null,
                orderable: false,
                className: 'text-center',
                render: function(data, type, row) {
                    return `<button class="btn btn-sm btn-outline-primary" onclick="abrirModalDados('${row.id}')" title="Visualizar Dados"><i class="bi bi-eye"></i></button>`;
                }
            }
        ],
        language: dtLanguage,
        responsive: true,
        order: [[0, 'desc']]
    });
});

window.abrirModalDados = function(logId) {
    let table = $('#tabela-logs').DataTable();
    let rowData = table.rows().data().toArray().find(r => r.id == logId);
    let tbody = $('#tabelaDadosJson tbody');
    tbody.empty();
    
    if (rowData && rowData.dados) {
        let dados = rowData.dados;
        if (Object.keys(dados).length === 0) {
            tbody.append('<tr><td colspan="2" class="text-center text-muted">Nenhum dado salvo (Log antigo ou sem dados).</td></tr>');
        } else {
            for (let key in dados) {
                let value = dados[key];
                if (value === null) value = '<span class="text-muted">null</span>';
                else if (value === '') value = '<span class="text-muted">vazio</span>';
                tbody.append(`<tr><td class="fw-bold text-secondary">${key}</td><td>${value}</td></tr>`);
            }
        }
    } else {
        tbody.append('<tr><td colspan="2" class="text-center text-muted">Nenhum dado salvo (Log antigo).</td></tr>');
    }
    
    let modal = new bootstrap.Modal(document.getElementById('modalVisualizarDados'));
    modal.show();
}
