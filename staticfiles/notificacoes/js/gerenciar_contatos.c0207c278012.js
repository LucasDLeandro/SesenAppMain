document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';
    const tbody = document.getElementById('grid-contatos-body');
    const emptyRow = document.getElementById('empty-row-message');
    
    let idsToDelete = [];

    // Adicionar Linha Vazia
    document.getElementById('btn-add-contato-row').addEventListener('click', function(e) {
        e.preventDefault();
        console.log("Botão Linha Vazia Clicado!");
        addNewRow('', '', '');
    });

    function addNewRow(nome, telefone, cargo) {
        if (emptyRow) emptyRow.style.display = 'none';
        const tr = document.createElement('tr');
        tr.className = 'contato-row new-row';
        tr.innerHTML = `
            <td class="ps-4">
                <div class="input-group input-group-borderless" style="border-radius: 6px;">
                    <span class="input-group-text border-end-0 pe-1"><i class="bi bi-person-fill text-muted opacity-50"></i></span>
                    <select class="form-select input-borderless border-start-0 ps-1 input-nome fw-medium text-dark select2-nome" style="width: calc(100% - 40px);">
                        ${nome ? `<option value="${nome}" selected="selected">${nome}</option>` : ''}
                    </select>
                </div>
            </td>
            <td>
                <input type="text" class="form-control input-borderless input-telefone format-telefone text-muted" value="${telefone}" placeholder="(00) 00000-0000">
            </td>
            <td>
                <input type="text" class="form-control input-borderless input-role text-muted" value="${cargo}" placeholder="Cargo/Função">
            </td>
            <td class="text-center">
                <div class="form-check form-switch d-inline-block">
                    <input class="form-check-input input-ativo fs-5 m-0" type="checkbox" role="switch" style="cursor: pointer;" checked>
                </div>
            </td>
            <td class="text-center pe-4">
                <button type="button" class="btn btn-sm btn-remove-row-subtle btn-remove-row fs-5" title="Remover"><i class="bi bi-trash3"></i></button>
            </td>
        `;
        tbody.insertBefore(tr, tbody.firstChild);
        
        // Reapply mask if you are using jQuery mask plugin
        if (typeof $ !== 'undefined' && $.fn.mask) {
            $(tr).find('.format-telefone').mask('(00) 00000-0000');
        }
        // Initialize Select2
        initSelect2Nome($(tr).find('.select2-nome'));
    }

    // Inicializa Select2 no campo Nome (Autocomplete com Busca Global)
    function initSelect2Nome(element) {
        $(element).select2({
            theme: 'bootstrap-5',
            width: '100%',
            dropdownParent: $('#modal-editar-contatos'),
            placeholder: 'Nome do Contato...',
            tags: true, // Permite digitar um nome que não está na base
            allowClear: true,
            minimumInputLength: 2,
            language: {
                inputTooShort: function() { return "Digite 2+ caracteres para buscar"; },
                noResults: function() { return "Não encontrado (Será criado como novo)"; },
                searching: function() { return "Buscando na base global..."; }
            },
            ajax: {
                url: '/usuarios/api/global-contacts/search/',
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return { q: params.term };
                },
                processResults: function (data) {
                    return { 
                        results: data.results.map(function(item) {
                            return {
                                id: item.nome, // Salva o nome como valor
                                text: item.nome,
                                telefone: item.telefone,
                                cargo: item.cargo
                            };
                        })
                    };
                },
                cache: true
            }
        }).on('select2:select', function (e) {
            var data = e.params.data;
            var tr = $(this).closest('tr');
            if(data.telefone) {
                tr.find('.input-telefone').val(data.telefone).trigger('input');
                // Reapply mask
                if (typeof $ !== 'undefined' && $.fn.mask) {
                    tr.find('.format-telefone').mask('(00) 00000-0000');
                }
            }
            if(data.cargo) {
                tr.find('.input-role').val(data.cargo);
            }
        });
    }

    // Inicializa Select2 para as linhas já existentes
    $('.select2-nome').each(function() {
        initSelect2Nome(this);
    });

    // Remover Linha
    tbody.addEventListener('click', function(e) {
        const btn = e.target.closest('.btn-remove-row');
        if (btn) {
            const tr = btn.closest('tr');
            if (tr.classList.contains('existing-row')) {
                idsToDelete.push(tr.dataset.contatoId);
            }
            tr.remove();
            if (tbody.querySelectorAll('.contato-row').length === 0 && emptyRow) {
                emptyRow.style.display = 'table-row';
            }
        }
    });

    // Salvar Todos
    document.getElementById('btn-save-all-contatos').addEventListener('click', function() {
        const createList = [];
        const updateList = [];

        document.querySelectorAll('.contato-row').forEach(tr => {
            const isExisting = tr.classList.contains('existing-row');
            const id = isExisting ? tr.dataset.contatoId : null;
            const nome = tr.querySelector('.input-nome').value.trim();
            const telefone = tr.querySelector('.input-telefone').value.trim();
            const role = tr.querySelector('.input-role').value.trim();
            const is_ativo = tr.querySelector('.input-ativo').checked;

            if (!nome) return; // Ignora linhas sem nome

            const payload = { nome, telefone, role, is_ativo };

            if (isExisting) {
                payload.id = id;
                updateList.push(payload);
            } else {
                createList.push(payload);
            }
        });

        const finalData = {
            create: createList,
            update: updateList,
            delete: idsToDelete
        };

        fetch(window.URL_BULK_CONTATOS, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(finalData)
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.reload(); 
            } else {
                alert('Erro ao salvar contatos: ' + data.message);
            }
        })
        .catch(err => {
            console.error(err);
            alert('Erro na comunicação com o servidor.');
        });
    });
});
