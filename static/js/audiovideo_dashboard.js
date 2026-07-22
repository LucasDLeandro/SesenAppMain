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

            if (headerText.toLowerCase() === 'ações' || headerText.toLowerCase() === 'acões' 
                || headerText.toLowerCase() === 'status & ações' || headerText === '') {
                th.appendTo(tr);
                return;
            }

            var input = $('<input type="text" class="form-control form-control-sm" />')
                .attr('placeholder', 'Filtrar ' + headerText)
                .css({
                    'width': '100%',
                    'font-size': '12px',
                    'padding': '4px 8px',
                    'border': '1px solid #ced4da',
                    'border-radius': '4px',
                    'background-color': '#f8f9fa'
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

    let dtEventos = $('#tbEventos').DataTable({
        responsive: true,
        language: { "sEmptyTable": "Nenhum registro encontrado", "sInfo": "Mostrando de _START_ até _END_ de _TOTAL_ registros", "sInfoEmpty": "Mostrando 0 até 0 de 0 registros", "sInfoFiltered": "(Filtrados de _MAX_ registros)", "sLengthMenu": "Mostrar _MENU_ resultados por página", "sLoadingRecords": "Carregando...", "sProcessing": "Processando...", "sZeroRecords": "Nenhum registro encontrado", "sSearch": "Pesquisar:", "oPaginate": { "sNext": "Próximo", "sPrevious": "Anterior", "sFirst": "Primeiro", "sLast": "Último" } },
        orderCellsTop: true
    });
    let dtEquipamentos = $('#tbEquipamentos').DataTable({
        responsive: true,
        language: { "sEmptyTable": "Nenhum registro encontrado", "sInfo": "Mostrando de _START_ até _END_ de _TOTAL_ registros", "sInfoEmpty": "Mostrando 0 até 0 de 0 registros", "sInfoFiltered": "(Filtrados de _MAX_ registros)", "sLengthMenu": "Mostrar _MENU_ resultados por página", "sLoadingRecords": "Carregando...", "sProcessing": "Processando...", "sZeroRecords": "Nenhum registro encontrado", "sSearch": "Pesquisar:", "oPaginate": { "sNext": "Próximo", "sPrevious": "Anterior", "sFirst": "Primeiro", "sLast": "Último" } },
        orderCellsTop: true
    });
    let dtOS = $('#tbOS').DataTable({
        responsive: true,
        language: { "sEmptyTable": "Nenhum registro encontrado", "sInfo": "Mostrando de _START_ até _END_ de _TOTAL_ registros", "sInfoEmpty": "Mostrando 0 até 0 de 0 registros", "sInfoFiltered": "(Filtrados de _MAX_ registros)", "sLengthMenu": "Mostrar _MENU_ resultados por página", "sLoadingRecords": "Carregando...", "sProcessing": "Processando...", "sZeroRecords": "Nenhum registro encontrado", "sSearch": "Pesquisar:", "oPaginate": { "sNext": "Próximo", "sPrevious": "Anterior", "sFirst": "Primeiro", "sLast": "Último" } },
        orderCellsTop: true
    });
    let dtTVs = $('#tbTVs').DataTable({
        responsive: true,
        language: { "sEmptyTable": "Nenhum registro encontrado", "sInfo": "Mostrando de _START_ até _END_ de _TOTAL_ registros", "sInfoEmpty": "Mostrando 0 até 0 de 0 registros", "sSearch": "Pesquisar:" },
        orderCellsTop: true
    });

    async function carregarDados() {
        try {
            const reqEq = await fetch('/gestao_patrimonio/api/equipamentos-av/');
            const reqEv = await fetch('/audiovideo/api/eventos/');
            const reqOs = await fetch('/audiovideo/api/os/');
            const reqTv = await fetch('/gestao_patrimonio/api/tvs/');

            const eq = await reqEq.json();
            const ev = await reqEv.json();
            const os = await reqOs.json();
            const tvs = await reqTv.json();

            $('#metric-equipamentos').text(eq.length);
            $('#metric-eventos').text(ev.filter(e => e.status !== 'concluido' && e.status !== 'cancelado').length);
            $('#metric-os').text(os.filter(o => o.status !== 'concluida').length);

            // Tabela Equipamentos
            dtEquipamentos.clear();
            eq.forEach(item => {
                let badge = `<span class="status-badge status-${item.status}">${item.status.toUpperCase()}</span>`;
                dtEquipamentos.row.add([
                    item.id,
                    item.nome,
                    item.categoria.toUpperCase(),
                    item.patrimonio || item.numero_serie || '-',
                    badge
                ]);
            });
            dtEquipamentos.draw();

            // Tabela Eventos
            dtEventos.clear();
            ev.forEach(item => {
                let badge = `<span class="status-badge status-${item.status}">${item.status.toUpperCase()}</span>`;
                let dataIni = new Date(item.data_inicio).toLocaleString('pt-BR');
                let actions = '';
                if(item.status !== 'concluido' && item.status !== 'cancelado') {
                    actions = `<button class="btn btn-sm btn-success" onclick="abrirModalConcluirEvento(${item.id}, '${item.nome}')">Concluir</button>`;
                }
                dtEventos.row.add([
                    item.id,
                    item.nome,
                    item.local,
                    dataIni,
                    item.solicitante,
                    badge + ' ' + actions
                ]);
            });
            dtEventos.draw();

            // Tabela OS
            dtOS.clear();
            os.forEach(item => {
                let badge = `<span class="status-badge status-${item.status}">${item.status.toUpperCase()}</span>`;
                let dataAb = new Date(item.data_abertura).toLocaleString('pt-BR');
                let equipName = item.equipamento_detalhes ? item.equipamento_detalhes.nome : 'ID: ' + item.equipamento;
                
                dtOS.row.add([
                    item.protocolo || 'N/A',
                    equipName,
                    item.defeito_relatado,
                    dataAb,
                    badge
                ]);
            });
            dtOS.draw();

            // Tabela TVs
            dtTVs.clear();
            tvs.forEach(item => {
                let badge = `<span class="status-badge status-${item.status}">${item.status.toUpperCase()}</span>`;
                dtTVs.row.add([
                    item.id,
                    `${item.marca} - ${item.modelo}`,
                    `${item.tamanho_polegadas}"`,
                    item.patrimonio,
                    item.localizacao_atual || 'Não informada',
                    badge
                ]);
            });
            dtTVs.draw();

            // Aplicar filtros de coluna após carregar dados (apenas na primeira vez)
            aplicarFiltroColunas(dtEventos);
            aplicarFiltroColunas(dtEquipamentos);
            aplicarFiltroColunas(dtOS);
            aplicarFiltroColunas(dtTVs);

            // Povoar Dropdowns de Equipamentos
            let selMultiple = document.getElementById('selEquipamentos');
            let selSingle = document.getElementById('selEquipamentoOS');
            if(selMultiple) selMultiple.innerHTML = '';
            if(selSingle) selSingle.innerHTML = '';

            eq.forEach(item => {
                let text = item.nome + ' (' + (item.patrimonio || item.numero_serie || 'Sem pat.') + ')';
                if(selMultiple) selMultiple.add(new Option(text, item.id));
                if(selSingle) selSingle.add(new Option(text, item.id));
            });
            
        } catch (e) {
            console.error("Erro ao carregar dados do Audio/Video", e);
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

    async function postFormData(url, formId) {
        let form = document.getElementById(formId);
        let formData = new FormData(form);
        let object = {};

        // Custom logic for equipments multiple insert
        if (formId === 'formEquipamento') {
            let pString = formData.get('patrimonios');
            let pArray = pString.split(',').map(s => s.trim()).filter(s => s);
            
            if (pArray.length > 1) {
                // Prepare array for bulk create
                let payloads = [];
                for (let pat of pArray) {
                    payloads.push({
                        nome: formData.get('nome'),
                        categoria: formData.get('categoria'),
                        tipo_instalacao: formData.get('tipo_instalacao'),
                        marca: formData.get('marca'),
                        modelo: formData.get('modelo'),
                        sala_local: formData.get('sala_local'),
                        patrimonio: pat
                    });
                }
                object = payloads;
            } else {
                formData.forEach((value, key) => { object[key] = value; });
                if(pArray.length === 1) object['patrimonio'] = pArray[0];
                delete object['patrimonios'];
            }
        } else {
            formData.forEach((value, key) => {
                if(!Reflect.has(object, key)){
                    object[key] = value;
                    return;
                }
                if(!Array.isArray(object[key])){
                    object[key] = [object[key]];
                }
                object[key].push(value);
            });

            if (formId === 'formEvento') {
                let select = document.getElementById('selEquipamentos');
                if(select) {
                    let selected = [...select.options].filter(option => option.selected).map(option => option.value);
                    object['equipamentos_alocados'] = selected;
                }
            }
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(object)
            });
            if (response.ok) {
                alert('Salvo com sucesso!');
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

    window.salvarEquipamento = function() { postFormData('/gestao_patrimonio/api/equipamentos-av/', 'formEquipamento'); }
    window.salvarEvento = function() { postFormData('/audiovideo/api/eventos/', 'formEvento'); }
    window.salvarOS = function() { postFormData('/audiovideo/api/os/', 'formOS'); }
    window.salvarTV = function() { postFormData('/gestao_patrimonio/api/tvs/', 'formTV'); }

    window.abrirModalConcluirEvento = function(id, nome) {
        document.getElementById('concluirEventoId').value = id;
        document.getElementById('concluirEventoNome').innerText = nome;
        document.getElementById('relatorioConclusao').value = '';
        new bootstrap.Modal(document.getElementById('modalConcluirEvento')).show();
    }

    window.confirmarConclusaoEvento = async function() {
        let id = document.getElementById('concluirEventoId').value;
        let relatorio = document.getElementById('relatorioConclusao').value;
        
        try {
            const response = await fetch(`/audiovideo/api/eventos/${id}/concluir/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ relatorio_conclusao: relatorio })
            });
            if (response.ok) {
                alert('Evento concluído e equipamentos liberados!');
                bootstrap.Modal.getInstance(document.getElementById('modalConcluirEvento')).hide();
                carregarDados();
            } else {
                alert('Erro ao concluir evento.');
            }
        } catch(e) {
            console.error(e);
        }
    }
});
