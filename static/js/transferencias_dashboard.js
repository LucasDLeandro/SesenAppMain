$(document).ready(function() {

    // Função utilitária para aplicar filtros de pesquisa individual por coluna
    function aplicarFiltroColunas(tabela) {
        var tableNode = tabela.table().node();
        var thead = $(tableNode).find('thead');
        
        // Verifica se a linha de filtros já existe para evitar duplicidade
        if (thead.find('.filter-row').length) return;

        var tr = $('<tr class="filter-row"></tr>');

        tabela.columns().every(function(index) {
            var column = this;
            var headerText = $(column.header()).text().trim();
            var th = $('<th></th>');

            if (headerText.toLowerCase() === 'ações' || headerText.toLowerCase() === 'acões' || headerText === '') {
                th.appendTo(tr);
                return;
            }

            var input = $('<input type="text" class="form-control form-control-sm" />')
                .attr('placeholder', 'Filtrar ' + headerText)
                .css({
                    'width': '100%',
                    'font-size': '12px',
                    'padding': '4px 8px',
                    'border-radius': '4px'
                });

            var debounceTimer;
            input.on('keyup change', function() {
                var self = this;
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(function() {
                    if (column.search() !== self.value) {
                        column.search(self.value).draw();
                    }
                }, 300);
            });

            input.on('click', function(e) { e.stopPropagation(); });

            th.append(input).appendTo(tr);
        });

        thead.append(tr);
    }

    let dtTransf = $('#tbTransferencias').DataTable({
        responsive: true,
        language: { "sEmptyTable": "Nenhum registro encontrado", "sInfo": "Mostrando de _START_ até _END_ de _TOTAL_ registros", "sInfoEmpty": "Mostrando 0 até 0 de 0 registros", "sSearch": "Pesquisar:" },
        order: [[3, 'desc']],
        orderCellsTop: true
    });

    async function carregarDados() {
        try {
            const reqTr = await fetch('/gestao_patrimonio/api/transferencias/');
            const reqEq = await fetch('/gestao_patrimonio/api/equipamentos-base/');

            const transfs = await reqTr.json();
            const eqs = await reqEq.json();

            // Tabela Transferencias
            dtTransf.clear();
            transfs.forEach(item => {
                let eqName = item.equipamento_detalhes ? item.equipamento_detalhes.marca + ' ' + (item.equipamento_detalhes.modelo || '') : 'ID: ' + item.equipamento;
                let dataT = new Date(item.data_transferencia).toLocaleString('pt-BR');
                dtTransf.row.add([
                    item.id,
                    eqName,
                    `${item.origem} <i class="bi bi-arrow-right"></i> ${item.destino}`,
                    dataT,
                    item.responsavel,
                    item.numero_requisicao || '-'
                ]);
            });
            dtTransf.draw();

            // Aplicar filtros de coluna após carregar dados
            aplicarFiltroColunas(dtTransf);

            // Povoar Dropdown
            let selEq = document.getElementById('selEquipamento');
            if(selEq) {
                selEq.innerHTML = '';
                eqs.forEach(item => {
                    let text = `${item.marca} ${item.modelo || ''} (${item.patrimonio || 'Sem pat.'})`;
                    selEq.add(new Option(text, item.id + '|' + item.type));
                });
            }
            
        } catch (e) {
            console.error("Erro ao carregar dados", e);
        }
    }

    carregarDados();

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    window.salvarTransferencia = async function() {
        let form = document.getElementById('formTransferencia');
        let formData = new FormData(form);
        let object = {};
        formData.forEach((value, key) => object[key] = value);

        // O valor do select está no formato "id|type"
        let valArr = object['equipamento'].split('|');
        object['equipamento_id'] = valArr[0];
        object['equipamento_tipo'] = valArr[1];
        delete object['equipamento'];

        try {
            const response = await fetch('/gestao_patrimonio/api/transferencias/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(object)
            });
            if (response.ok) {
                alert('Transferência registrada!');
                $('.modal').modal('hide');
                form.reset();
                carregarDados();
            } else {
                const err = await response.json();
                console.log(err);
                alert('Erro ao salvar. Verifique os dados.');
            }
        } catch(e) {
            console.error(e);
            alert('Erro de rede ao salvar.');
        }
    }
});
