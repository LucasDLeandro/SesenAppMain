// modais
const modal_solicitacao = new bootstrap.Modal(document.getElementById('modal-solicitacao-telefone'));
const form_solicitacao = document.getElementById('form-solicitacao-telefone');

const modal_aparelho = new bootstrap.Modal(document.getElementById('modal-aparelho-voip'));
const form_aparelho = document.getElementById('form-aparelho-voip');


const modal_senha = new bootstrap.Modal(document.getElementById('modal-solicitacao-senha'));
const form_senha = document.getElementById('form-solicitacao-senha');

// Função genérica para envio de formulário para a API DRF
async function submitFormToAPI(evento, form_element, modal_instance, base_api_url, success_message) {
    evento.preventDefault();
    
    const formData = new FormData(form_element);
    
    let method = 'POST';
    let url = base_api_url;
    
    // Verifica se há um ID (campo 'id' ou 'id_oculto' etc, mas no FormData o name é 'id')
    const id_field = formData.get('id');
    if (id_field && id_field.trim() !== '') {
        method = 'PUT'; // Se tiver ID, trata como Update
        url = `${base_api_url}${id_field}/`;
    }
    
    // Limpa pontuações dos campos com máscara antes de enviar
    form_element.querySelectorAll('.mask-telefone, .mask-cpf, .mask-cnpj, .mask-cep, .mask-rg').forEach(input => {
        if(input.name && formData.has(input.name)) {
            // Strip any non-digit character except for RG which might have letters
            if (input.classList.contains('mask-rg')) {
                formData.set(input.name, input.value.replace(/[\.\-]/g, ''));
            } else {
                formData.set(input.name, input.value.replace(/\D/g, ''));
            }
        }
    });
    
    try {
        const resposta = await fetch(url, {
            method: method,
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        });

        if (resposta.ok) {
            const dados = await resposta.json();
            await Swal.fire({
                title: "Sucesso!",
                text: success_message,
                icon: "success"
            });
            form_element.reset();
            modal_instance.hide();
            // Recarrega a página para atualizar os dados, ou poderia atualizar a tabela via JS
            window.location.reload();
        } else {
            const erros = await resposta.json();
            console.log("Erros encontrados no formulário:", erros);
            Swal.fire("Erro!", "Não foi possível salvar. Verifique os dados inseridos.", "error");
        }

    } catch (erro) {
        console.error("Erro critico na conexão: ", erro);
        Swal.fire("Erro Crítico!", "Erro ao conectar com o servidor. Tente novamente mais tarde.", "error");
    }
}

// Listeners de submit para os formulários
if (form_solicitacao) {
    form_solicitacao.addEventListener('submit', function(e) {
        submitFormToAPI(e, form_solicitacao, modal_solicitacao, '/telefonia/api/solicitacoes/', 'Solicitação registrada com sucesso!');
    });
}

if (form_senha) {
    form_senha.addEventListener('submit', function(e) {
        submitFormToAPI(e, form_senha, modal_senha, '/telefonia/api/senhas/', 'Solicitação de senha registrada com sucesso!');
    });
}

if (form_aparelho) {
    form_aparelho.addEventListener('submit', function(e) {
        submitFormToAPI(e, form_aparelho, modal_aparelho, '/gestao_patrimonio/api/aparelhos-telefonicos/', 'Aparelho cadastrado com sucesso!');
    });
}



const form_concluir_solicitacao = document.getElementById('form-concluir-solicitacao');
if (form_concluir_solicitacao) {
    let aparelhosDisponiveis = [];
    const container = document.getElementById('instalacoes-container');
    const btnAdd = document.getElementById('btn-add-instalacao');

    function renderLinhaInstalacao(idUnico, defaultLocal = '') {
        const row = document.createElement('div');
        row.className = 'row mb-2 align-items-center instalacao-row';
        row.id = `instalacao-row-${idUnico}`;
        
        // Select Aparelho
        const colAp = document.createElement('div');
        colAp.className = 'col-md-3';
        const select = document.createElement('select');
        select.className = 'form-select select-aparelho-dinamico';
        select.required = true;
        select.innerHTML = '<option value="" disabled selected>Aparelho</option>';
        aparelhosDisponiveis.forEach(ap => {
            const opt = document.createElement('option');
            opt.value = ap.id;
            opt.textContent = ap.patrimonio + (ap.modelo ? ` - ${ap.modelo}` : '') + ` [${ap.status}]`;
            select.appendChild(opt);
        });
        colAp.appendChild(select);
        
        // Input Ramal
        const colRamal = document.createElement('div');
        colRamal.className = 'col-md-2';
        const inputRamal = document.createElement('input');
        inputRamal.type = 'text';
        inputRamal.className = 'form-control input-ramal-dinamico';
        inputRamal.placeholder = 'Ramal';
        inputRamal.required = true;
        colRamal.appendChild(inputRamal);
        
        // Input Local
        const colLocal = document.createElement('div');
        colLocal.className = 'col-md-3';
        const inputLocal = document.createElement('input');
        inputLocal.type = 'text';
        inputLocal.className = 'form-control input-local-dinamico';
        inputLocal.placeholder = 'Sala/Local';
        inputLocal.value = defaultLocal; // Preenche com o local base da solicitação se aplicável
        inputLocal.required = true;
        colLocal.appendChild(inputLocal);
        
        // Input MAC
        const colMac = document.createElement('div');
        colMac.className = 'col-md-3';
        const inputMac = document.createElement('input');
        inputMac.type = 'text';
        inputMac.className = 'form-control input-mac-dinamico';
        inputMac.placeholder = 'MAC Address';
        colMac.appendChild(inputMac);

        // Btn Remover
        const colBtn = document.createElement('div');
        colBtn.className = 'col-md-1 text-end';
        const btnRem = document.createElement('button');
        btnRem.type = 'button';
        btnRem.className = 'btn btn-sm btn-outline-danger';
        btnRem.innerHTML = '<i class="bi bi-trash"></i>';
        btnRem.onclick = function() {
            if (container.querySelectorAll('.instalacao-row').length > 1) {
                row.remove();
                atualizarOpcoesAparelho();
            } else {
                Swal.fire("Aviso", "A solicitação precisa ter pelo menos um aparelho instalado.", "warning");
            }
        };
        colBtn.appendChild(btnRem);
        
        row.appendChild(colAp);
        row.appendChild(colRamal);
        row.appendChild(colLocal);
        row.appendChild(colMac);
        row.appendChild(colBtn);
        
        container.appendChild(row);
        
        // Inicializar Select2 para busca
        $(select).select2({
            theme: 'bootstrap-5',
            dropdownParent: $('#modal-concluir-solicitacao'),
            width: '100%',
            language: {
                noResults: function() {
                    return "Nenhum aparelho encontrado";
                }
            }
        });

        // Listener no select para atualizar os demais ao mudar o valor
        $(select).on('change', atualizarOpcoesAparelho);
        
        // Atualiza imediatamente para que esta nova linha já respeite as seleções anteriores
        atualizarOpcoesAparelho();
    }
    
    // Função para não permitir escolher o mesmo aparelho em linhas diferentes
    function atualizarOpcoesAparelho() {
        const todosSelects = container.querySelectorAll('.select-aparelho-dinamico');
        const valoresSelecionados = Array.from(todosSelects)
                                        .map(sel => sel.value)
                                        .filter(val => val !== '');
                                        
        todosSelects.forEach(select => {
            const opcoes = select.querySelectorAll('option');
            opcoes.forEach(opt => {
                // Se o valor estiver na lista de selecionados, mas NÃO for o valor DESTE select atual, desabilita
                if (opt.value && valoresSelecionados.includes(opt.value) && opt.value !== select.value) {
                    opt.disabled = true;
                    opt.hidden = true; // No bootstrap e navegadores modernos o hidden esconde a opção do dropdown
                } else {
                    opt.disabled = false;
                    opt.hidden = false;
                }
            });
            // Notifica o select2 caso a opção tenha sido desabilitada
            if ($(select).data('select2')) {
                // Ao recriar opções no select2, basta chamar destroy e recriar ou recarregar
                $(select).select2({
                    theme: 'bootstrap-5',
                    dropdownParent: $('#modal-concluir-solicitacao'),
                    width: '100%',
                    language: {
                        noResults: function() {
                            return "Nenhum aparelho encontrado";
                        }
                    }
                });
            }
        });
    }

    document.getElementById('modal-concluir-solicitacao').addEventListener('show.bs.modal', async function () {
        container.innerHTML = ''; // Limpa linhas antigas
        
        try {
            const resposta = await fetch('/gestao_patrimonio/api/aparelhos-telefonicos/');
            if (resposta.ok) {
                aparelhosDisponiveis = await resposta.json();
                
                // O local_conclusao foi setado no input hidden (ou pegamos da API no click)
                // O list_telefonia.js preencheu document.getElementById('locais_conclusao').value
                // Mas agora deletamos locais_conclusao! Vou pegar do escopo global se precisar.
                // Como deletamos, o JS antigo de list_telefonia.js vai falhar ao achar locais_conclusao.
                // Vamos resolver isso: o valor local inicial será passado de outra forma.
                // Por enquanto criamos 1 linha vazia.
                
                // Podemos pegar o valor de um hidden que criaremos ou ler uma variável global.
                const hiddenLocal = document.getElementById('local_base_solicitacao');
                const defaultLocal = hiddenLocal ? hiddenLocal.value : '';
                renderLinhaInstalacao(Date.now(), defaultLocal);
            }
        } catch (erro) {
            console.error("Erro ao buscar aparelhos:", erro);
        }
    });
    
    if(btnAdd) {
        btnAdd.addEventListener('click', function() {
            renderLinhaInstalacao(Date.now());
        });
    }

    form_concluir_solicitacao.addEventListener('submit', async function(e) {
        e.preventDefault();
        const id = document.getElementById('id_conclusao_solicitacao').value;
        
        // Construir o payload
        const instalacoes = [];
        const rows = container.querySelectorAll('.instalacao-row');
        for(let r of rows) {
            const apId = r.querySelector('.select-aparelho-dinamico').value;
            const ramal = r.querySelector('.input-ramal-dinamico').value;
            const local = r.querySelector('.input-local-dinamico').value;
            const mac = r.querySelector('.input-mac-dinamico').value;
            if(!apId) {
                Swal.fire("Erro", "Selecione o aparelho em todas as linhas.", "error");
                return;
            }
            instalacoes.push({
                aparelho_id: apId,
                ramal: ramal,
                local: local,
                mac_address: mac
            });
        }
        
        const payload = {
            tecnico_responsavel: document.getElementById('tecnico_responsavel_conclusao').value,
            relatorio: document.getElementById('relatorio_conclusao').value,
            data_instalacao: document.getElementById('data_instalacao_conclusao').value,
            termo_transferencia_interna: document.getElementById('termo_transferencia_conclusao') ? document.getElementById('termo_transferencia_conclusao').value : '',
            instalacoes: instalacoes
        };
        
        try {
            const resposta = await fetch(`/telefonia/api/solicitacoes/${id}/concluir/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(payload)
            });
            if (resposta.ok) {
                await Swal.fire("Sucesso!", "Solicitação concluída com sucesso!", "success");
                form_concluir_solicitacao.reset();
                const modalEl = document.getElementById('modal-concluir-solicitacao');
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
                window.location.reload();
            } else {
                const erros = await resposta.json();
                console.log(erros);
                Swal.fire("Erro!", "Não foi possível salvar. Verifique os dados inseridos.", "error");
            }
        } catch (erro) {
            console.error(erro);
            Swal.fire("Erro Crítico!", "Erro ao conectar com o servidor.", "error");
        }
    });
}

// ==========================================
// Lógica para Remessa para Manutenção (Aparelhos Dinâmicos)
// ==========================================
const containerRemessa = document.getElementById('remessa-aparelhos-container');

window.atualizarOpcoesAparelhoRemessa = function() {
    if(!containerRemessa) return;
    const todosSelects = containerRemessa.querySelectorAll('.select-aparelho-dinamico-remessa');
    const valoresSelecionados = Array.from(todosSelects)
                                    .map(sel => sel.value)
                                    .filter(val => val !== '');
                                    
    todosSelects.forEach(select => {
        const opcoes = select.querySelectorAll('option');
        opcoes.forEach(opt => {
            if (opt.value && valoresSelecionados.includes(opt.value) && opt.value !== select.value) {
                opt.disabled = true;
                opt.hidden = true;
            } else {
                opt.disabled = false;
                opt.hidden = false;
            }
        });
        if ($(select).data('select2')) {
            $(select).select2({
                theme: 'bootstrap-5',
                dropdownParent: $('#modal-remessa-manutencao'),
                width: '100%',
                language: { noResults: () => "Nenhum aparelho encontrado" }
            });
        }
    });
};

window.renderLinhaAparelhoRemessa = function(idUnico) {
    if(!containerRemessa) return;
    const row = document.createElement('div');
    row.className = 'row mb-2 align-items-center instalacao-row-remessa';
    row.id = `remessa-row-${idUnico}`;
    
    // Select Aparelho
    const colAp = document.createElement('div');
    colAp.className = 'col-md-11';
    const select = document.createElement('select');
    select.className = 'form-select select-aparelho-dinamico-remessa';
    select.required = true;
    select.innerHTML = '<option value="" disabled selected>Aparelho</option>';
    
    const aparelhos = window.aparelhosDefeituososGlobal || [];
    aparelhos.forEach(ap => {
        const opt = document.createElement('option');
        opt.value = ap.id;
        opt.textContent = `Patrimônio: ${ap.patrimonio} - Modelo: ${ap.modelo}`;
        select.appendChild(opt);
    });
    colAp.appendChild(select);
    
    // Btn Remover
    const colBtn = document.createElement('div');
    colBtn.className = 'col-md-1 text-end';
    const btnRem = document.createElement('button');
    btnRem.type = 'button';
    btnRem.className = 'btn btn-sm btn-outline-danger';
    btnRem.innerHTML = '<i class="bi bi-trash"></i>';
    btnRem.onclick = function() {
        if (containerRemessa.querySelectorAll('.instalacao-row-remessa').length > 1) {
            row.remove();
            window.atualizarOpcoesAparelhoRemessa();
        } else {
            Swal.fire("Aviso", "A remessa precisa ter pelo menos um aparelho.", "warning");
        }
    };
    colBtn.appendChild(btnRem);
    
    row.appendChild(colAp);
    row.appendChild(colBtn);
    
    containerRemessa.appendChild(row);
    
    $(select).select2({
        theme: 'bootstrap-5',
        dropdownParent: $('#modal-remessa-manutencao'),
        width: '100%',
        language: { noResults: () => "Nenhum aparelho encontrado" }
    });

    $(select).on('change', window.atualizarOpcoesAparelhoRemessa);
    window.atualizarOpcoesAparelhoRemessa();
};

document.addEventListener('DOMContentLoaded', () => {
    const btnAddRemessa = document.getElementById('btn-add-aparelho-remessa');
    if(btnAddRemessa) {
        btnAddRemessa.addEventListener('click', function() {
            window.renderLinhaAparelhoRemessa(Date.now());
        });
    }
});
