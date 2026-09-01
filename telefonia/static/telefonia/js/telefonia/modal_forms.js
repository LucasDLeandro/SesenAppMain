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
    form_senha.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Verifica se é edição (tem ID)
        const id_field = form_senha.querySelector('[name="id"]').value;
        const isUpdate = id_field && id_field.trim() !== '';
        
        if (isUpdate) {
            // Se for update, usa o comportamento padrão
            submitFormToAPI(e, form_senha, modal_senha, '/telefonia/api/senhas/', 'Solicitação de senha atualizada com sucesso!');
            return;
        }

        // Se for criação, monta o JSON com o array de colaboradores
        const payload = {
            protocolo: form_senha.querySelector('[name="protocolo"]').value,
            solicitante: form_senha.querySelector('[name="solicitante"]').value,
            unidade: form_senha.querySelector('[name="unidade"]').value,
            sigla_unidade: form_senha.querySelector('[name="sigla_unidade"]').value,
            edificios: form_senha.querySelector('[name="edificios"]').value,
            desvio: form_senha.querySelector('[name="desvio"]').value,
            tel_desvio_externo: form_senha.querySelector('[name="tel_desvio_externo"]').value,
            colaboradores: []
        };

        const cards = document.querySelectorAll('#lista_colaboradores_senhas .user-card');
        cards.forEach(card => {
            const colab = {
                primeiro_nome: card.querySelector('.input-primeiro-nome').value,
                sobrenome: card.querySelector('.input-sobrenome').value,
                ramal: card.querySelector('.input-ramal').value,
                email: card.querySelector('.input-email').value,
                cargo: card.querySelector('.select-cargo').value,
                numero_contrato: card.querySelector('.input-numero-contrato').value,
                empresa_vinculada: card.querySelector('.input-empresa').value,
                fiscal_contrato: card.querySelector('.input-fiscal').value,
                unidade_fiscal: card.querySelector('.input-unidade-fiscal').value
            };
            payload.colaboradores.push(colab);
        });

        try {
            const resposta = await fetch('/telefonia/api/senhas/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(payload)
            });

            if (resposta.ok) {
                await Swal.fire("Sucesso!", "Senhas solicitadas com sucesso!", "success");
                form_senha.reset();
                modal_senha.hide();
                window.location.reload();
            } else {
                let erros;
                try {
                    erros = await resposta.json();
                } catch (e) {
                    erros = {};
                }
                console.error("Erro na API:", erros);

                // Constrói mensagem de erro legível
                let mensagemErro = "Não foi possível salvar. Verifique os dados inseridos.";
                if (erros && typeof erros === 'object') {
                    const campos = Object.entries(erros).map(([campo, msgs]) => {
                        const msgStr = Array.isArray(msgs) ? msgs.join(', ') : String(msgs);
                        return `<b>${campo}</b>: ${msgStr}`;
                    }).join('<br>');
                    if (campos) mensagemErro = campos;
                }

                Swal.fire({
                    title: "Erro ao Salvar!",
                    html: mensagemErro,
                    icon: "error"
                });
            }
        } catch (erro) {
            console.error("Erro critico: ", erro);
            Swal.fire("Erro Crítico!", "Erro ao conectar com o servidor.", "error");
        }
    });
}

if (form_aparelho) {
    // Adicionar logica para clonar linhas
    const btnAddAparelho = document.getElementById('btn-add-aparelho-row');
    if (btnAddAparelho) {
        btnAddAparelho.addEventListener('click', function() {
            const container = document.getElementById('aparelhos-container');
            const originalRow = container.querySelector('.aparelho-row');
            
            // Verifica se está editando um (se tem ID). Se tiver, não pode clonar (esconder o botão de add via CSS)
            const idVal = document.getElementById('id_oculto_aparelho').value;
            if (idVal) {
                Swal.fire('Aviso', 'Não é possível adicionar múltiplos aparelhos no modo de edição.', 'warning');
                return;
            }
            
            const newRow = originalRow.cloneNode(true);
            
            // Limpa os valores
            newRow.querySelectorAll('input').forEach(input => input.value = '');
            newRow.querySelectorAll('select').forEach(select => select.value = 'funciona');
            
            // Exibe o botão de remover
            const btnRemove = newRow.querySelector('.btn-remove-aparelho');
            if (btnRemove) {
                btnRemove.classList.remove('d-none');
                btnRemove.addEventListener('click', function() {
                    newRow.remove();
                });
            }
            
            container.appendChild(newRow);
        });
    }

    form_aparelho.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Verifica se é edição
        const id_field = form_aparelho.querySelector('[name="id"]');
        const isUpdate = id_field && id_field.value.trim() !== '';
        
        if (isUpdate) {
            // Se for update, usa submitFormToAPI normal, pois editamos 1 de cada vez
            submitFormToAPI(e, form_aparelho, modal_aparelho, '/gestao_patrimonio/api/aparelhos-telefonicos/', 'Aparelho atualizado com sucesso!');
            return;
        }

        // É criação. Vamos pegar todas as rows
        const rows = document.querySelectorAll('#aparelhos-container .aparelho-row');
        let aparelhosList = [];
        
        for (let row of rows) {
            let patrimonio = row.querySelector('.input-patrimonio').value;
            let modelo = row.querySelector('.input-modelo').value;
            let funcao = row.querySelector('.input-funcao') ? row.querySelector('.input-funcao').value : 'fixo';
            let fcn = row.querySelector('.input-fcn').value;
            let mac = row.querySelector('.input-mac').value;
            let integridade = row.querySelector('.input-integridade').value;
            
            aparelhosList.push({
                patrimonio: patrimonio,
                modelo: modelo,
                funcao_aparelho: funcao,
                fcn: fcn,
                mac_address: mac,
                integridade: integridade
            });
        }
        
        // Dispara requisições concorrentes ou em série. Série é mais seguro pra n falhar metade.
        // O DRF por padrao suporta bulk create se tiver um ListSerializer, mas como não temos certeza, mandamos um loop assíncrono.
        Swal.fire({
            title: 'Salvando...',
            text: `Salvando ${aparelhosList.length} aparelho(s)`,
            allowOutsideClick: false,
            didOpen: () => { Swal.showLoading(); }
        });
        
        try {
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            let erros = 0;
            
            for (let ap of aparelhosList) {
                let formData = new FormData();
                formData.append('patrimonio', ap.patrimonio);
                formData.append('modelo', ap.modelo);
                formData.append('fcn', ap.fcn);
                formData.append('mac_address', ap.mac_address);
                formData.append('integridade', ap.integridade);
                
                const res = await fetch('/gestao_patrimonio/api/aparelhos-telefonicos/', {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-CSRFToken': csrftoken }
                });
                
                if (!res.ok) {
                    erros++;
                    console.error("Erro ao salvar aparelho", ap, await res.text());
                }
            }
            
            if (erros > 0) {
                Swal.fire("Atenção", `Alguns aparelhos não puderam ser salvos (${erros} erros). Verifique se não há patrimônios duplicados no sistema.`, "warning");
            } else {
                Swal.fire("Sucesso!", "Todos os aparelhos foram salvos.", "success");
                form_aparelho.reset();
                modal_aparelho.hide();
                window.location.reload();
            }
            
        } catch(err) {
            console.error(err);
            Swal.fire("Erro Crítico!", "Erro ao conectar com o servidor.", "error");
        }
    });
}

// Reset do modal ao abrir "Novo Aparelho"
document.getElementById('modal-aparelho-voip').addEventListener('show.bs.modal', function (e) {
    if (e.relatedTarget) { // Foi clicado pelo botão de novo
        form_aparelho.reset();
        document.getElementById('id_oculto_aparelho').value = '';
        
        // Remover todas as linhas adicionais
        const container = document.getElementById('aparelhos-container');
        const rows = container.querySelectorAll('.aparelho-row');
        for (let i = 1; i < rows.length; i++) {
            rows[i].remove();
        }
        
        // Mostrar o botão de add
        document.getElementById('div-add-aparelho').classList.remove('d-none');
    }
});



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
                    opt.hidden = true;
                } else {
                    opt.disabled = false;
                    opt.hidden = false;
                }
            });
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


// Lógica para adicionar cards dinâmicos de Senha Telefônica
let contadorColaboradoresSenha = 0;

function addColaboradorSenhaCard() {
    contadorColaboradoresSenha++;
    const idUnico = contadorColaboradoresSenha;
    const cardId = `colaborador-senha-card-${idUnico}`;
    const container = document.getElementById('lista_colaboradores_senhas');

    const cardHTML = `
        <div class="user-card" id="${cardId}">
            <div class="user-card-header">
                <div class="user-card-title">
                    <i class="bi bi-person-fill text-primary me-2"></i> 
                    <span>Usuário ${contadorColaboradoresSenha}</span>
                </div>
                <button type="button" class="btn-remove-user" onclick="document.getElementById('${cardId}').remove()" title="Remover Usuário">
                    <i class="bi bi-trash3-fill"></i>
                </button>
            </div>
            
            <div class="card-body p-0">
                <div class="row g-2 mb-2">
                    <div class="col-md-6">
                        <label class="form-label">Primeiro Nome <span class="text-danger">*</span></label>
                        <input type="text" class="form-control format-text input-primeiro-nome" maxlength="50" required>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Sobrenome <span class="text-danger">*</span></label>
                        <input type="text" class="form-control format-text input-sobrenome" maxlength="100" required>
                    </div>
                </div>
                
                <div class="row g-2 mb-2">
                    <div class="col-md-6">
                        <label class="form-label">Ramal</label>
                        <input type="text" class="form-control input-ramal" maxlength="10">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">E-mail Institucional</label>
                        <input type="email" class="form-control input-email" maxlength="255">
                    </div>
                </div>

                <div class="row g-2 mb-2">
                    <div class="col-md-12">
                        <label class="form-label">Cargo</label>
                        <select class="form-select select-cargo" onchange="toggleCargoFieldsDinâmico(this, ${idUnico})">
                            <option value="servidor" selected>Servidor</option>
                            <option value="colaborador">Colaborador</option>
                        </select>
                    </div>
                </div>

                <div id="dados_colaborador_detalhes_${idUnico}" style="display: none;" class="mt-2 p-3 rounded-3" style="background-color: #f1f5f9; border: 1px dashed #cbd5e1;">
                    <h6 class="text-secondary fw-bold mb-2" style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px;">
                        <i class="bi bi-briefcase-fill me-1"></i> Dados do Contrato
                    </h6>
                    <div class="row g-2 mb-2">
                        <div class="col-md-6">
                            <label class="form-label">Selecione o Contrato</label>
                            <select class="form-select select-contrato-existente" onchange="mudarContratoDinamico(this, ${idUnico})">
                                <option value="">-- Selecione --</option>
                                <option value="novo">+ Novo Contrato</option>
                            </select>
                        </div>
                        <div class="col-md-6 div-numero-contrato" style="display: none;">
                            <label class="form-label">Número do Contrato</label>
                            <input type="text" class="form-control input-numero-contrato" maxlength="50">
                        </div>
                    </div>
                    <div class="row g-2 mb-2">
                        <div class="col-md-6 div-empresa-vinculada" style="display: none;">
                            <label class="form-label">Empresa Vinculada</label>
                            <input type="text" class="form-control format-text input-empresa" maxlength="100">
                        </div>
                        <div class="col-md-6 div-fiscal-contrato" style="display: none;">
                            <label class="form-label">Fiscal do Contrato</label>
                            <input type="text" class="form-control format-text input-fiscal" maxlength="100">
                        </div>
                    </div>
                    <div class="row g-2">
                        <div class="col-md-12 div-unidade-fiscal" style="display: none;">
                            <label class="form-label">Unidade do Fiscal</label>
                            <input type="text" class="form-control format-text input-unidade-fiscal" maxlength="200">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', cardHTML);

    // Preenche os contratos no novo select criado
    if (window.contratosColaboradorCache) {
        const selectElem = container.querySelector(`#colaborador-senha-card-${idUnico} .select-contrato-existente`);
        window.contratosColaboradorCache.forEach(c => {
            selectElem.innerHTML += `<option value="${c.numero_contrato}">${c.numero_contrato}</option>`;
        });
    }
}

function mudarContratoDinamico(selectElement, idUnico) {
    const card = document.getElementById(`colaborador-senha-card-${idUnico}`);
    const inputNumero = card.querySelector('.input-numero-contrato');
    const inputEmpresa = card.querySelector('.input-empresa');
    const inputFiscal = card.querySelector('.input-fiscal');
    const inputUnidade = card.querySelector('.input-unidade-fiscal');
    
    // Mostra as divs que escondem os inputs do contrato
    card.querySelector('.div-numero-contrato').style.display = 'block';
    card.querySelector('.div-empresa-vinculada').style.display = 'block';
    card.querySelector('.div-fiscal-contrato').style.display = 'block';
    card.querySelector('.div-unidade-fiscal').style.display = 'block';

    if (selectElement.value === 'novo') {
        inputNumero.value = '';
        inputEmpresa.value = '';
        inputFiscal.value = '';
        inputUnidade.value = '';

        inputNumero.readOnly = false;
        inputEmpresa.readOnly = false;
        inputFiscal.readOnly = false;
        inputUnidade.readOnly = false;
    } else if (selectElement.value !== '') {
        const contrato = window.contratosColaboradorCache.find(c => c.numero_contrato === selectElement.value);
        if (contrato) {
            inputNumero.value = contrato.numero_contrato;
            inputEmpresa.value = contrato.empresa_vinculada;
            inputFiscal.value = contrato.fiscal_contrato;
            inputUnidade.value = contrato.unidade_fiscal;

            // Se selecionou um existente, bloqueia edição
            inputNumero.readOnly = true;
            inputEmpresa.readOnly = true;
            inputFiscal.readOnly = true;
            inputUnidade.readOnly = true;
        }
    } else {
        // Se voltou para o "-- Selecione --"
        card.querySelector('.div-numero-contrato').style.display = 'none';
        card.querySelector('.div-empresa-vinculada').style.display = 'none';
        card.querySelector('.div-fiscal-contrato').style.display = 'none';
        card.querySelector('.div-unidade-fiscal').style.display = 'none';
        inputNumero.value = '';
        inputEmpresa.value = '';
        inputFiscal.value = '';
        inputUnidade.value = '';
    }
}

function toggleCargoFieldsDinâmico(selectElement, idUnico) {
    const container = document.getElementById(`dados_colaborador_detalhes_${idUnico}`);
    if (selectElement.value === 'colaborador') {
        container.style.display = 'block';
        // Garante que o cache de contratos seja recarregado se não houver
        if (!window.contratosColaboradorCache || window.contratosColaboradorCache.length === 0) {
            if (typeof carregarContratos === 'function') {
                carregarContratos();
            }
        }
    } else {
        container.style.display = 'none';
        // Limpar campos
        container.querySelectorAll('input').forEach(input => input.value = '');
        container.querySelectorAll('select').forEach(sel => sel.value = '');
    }
}

// Inicializa com um card aberto ao abrir o modal
document.getElementById('modal-solicitacao-senha').addEventListener('show.bs.modal', function (e) {
    if (contadorColaboradoresSenha === 0) {
        addColaboradorSenhaCard();
    }
});

// -----------------------------------------
// FLUXO DO TÉCNICO (Concluir Senha)
// -----------------------------------------
window.abrirModalConcluirSenha = async function(id) {
    document.getElementById('id_conclusao_senha').value = id;
    document.getElementById('senha_gerada').value = '';
    document.getElementById('categoria_conclusao').value = '';
    document.getElementById('desvio_conclusao').value = 'False';
    document.getElementById('tel_desvio_conclusao').value = '';
    
    // Limpa campos visuais temporariamente
    document.getElementById('view_concluir_solicitante').innerText = 'Carregando...';
    document.getElementById('view_concluir_unidade').innerText = 'Carregando...';
    document.getElementById('view_concluir_usuario').innerText = 'Carregando...';
    document.getElementById('view_concluir_email').innerText = 'Carregando...';
    document.getElementById('view_concluir_ramal').innerText = 'Carregando...';
    document.getElementById('view_concluir_cargo').innerText = 'Carregando...';

    var myModal = new bootstrap.Modal(document.getElementById('modal-concluir-senha'));
    myModal.show();

    // Busca os dados da solicitação para exibir
    try {
        const res = await fetch(`/telefonia/api/senhas/${id}/`);
        if (res.ok) {
            const data = await res.json();
            document.getElementById('view_concluir_solicitante').innerText = data.solicitante || 'N/A';
            document.getElementById('view_concluir_unidade').innerText = data.unidade || 'N/A';
            document.getElementById('view_concluir_usuario').innerText = data.usuario || 'N/A';
            document.getElementById('view_concluir_email').innerText = data.email || 'N/A';
            document.getElementById('view_concluir_ramal').innerText = data.ramal || 'N/A';
            document.getElementById('view_concluir_cargo').innerText = data.cargo || 'servidor';
            if (data.categoria) document.getElementById('categoria_conclusao').value = data.categoria;
            if (data.desvio) document.getElementById('desvio_conclusao').value = 'True';
            if (data.tel_desvio_externo) document.getElementById('tel_desvio_conclusao').value = data.tel_desvio_externo;
        }
    } catch (err) {
        console.error("Erro ao buscar dados", err);
    }
}

const formConcluirSenha = document.getElementById('form-concluir-senha');
if (formConcluirSenha) {
    formConcluirSenha.addEventListener('submit', async function(e) {
        e.preventDefault();
        const id = document.getElementById('id_conclusao_senha').value;
        const payload = {
            senha: document.getElementById('senha_gerada').value,
            categoria: document.getElementById('categoria_conclusao').value || null,
            desvio: document.getElementById('desvio_conclusao').value === 'True',
            tel_desvio_externo: document.getElementById('tel_desvio_conclusao').value || null,
            status: 'aguardando_supervisor'
        };

        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const resposta = await fetch(`/telefonia/api/senhas/${id}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(payload)
            });

            if (!resposta.ok) {
                const data = await resposta.json();
                throw new Error(data.error || 'Erro ao salvar a senha.');
            }

            Swal.fire('Sucesso!', 'Senha gerada e enviada para o Supervisor.', 'success');
            bootstrap.Modal.getInstance(document.getElementById('modal-concluir-senha')).hide();
            if(typeof $('#tabela-senhas') !== 'undefined') $('#tabela-senhas').DataTable().ajax.reload(null, false);
        } catch (error) {
            Swal.fire('Erro!', error.message, 'error');
        }
    });
}

// -----------------------------------------
// FLUXO DO SUPERVISOR (Finalizar e E-mail)
// -----------------------------------------
window.abrirModalFinalizarSenha = function(id, status = 'aguardando_supervisor') {
    document.getElementById('id_finalizacao_senha').value = id;

    // Esconder o bloco de Ação do Supervisor se for reenvio (já finalizado)
    const blocoAcao = document.getElementById('bloco_acao_supervisor_finalizacao');
    if (blocoAcao) {
        blocoAcao.style.display = (status === 'finalizada') ? 'none' : 'block';
    }

    // Configura o link para abrir o PDF em nova aba
    const linkPreview = document.getElementById('link_preview_senha');
    if (linkPreview) {
        linkPreview.href = `/telefonia/senha/${id}/pdf/`;
    }
    
    // Busca dados do email preview
    document.getElementById('email_para_finalizacao').value = 'Carregando...';
    document.getElementById('email_copia_finalizacao').value = 'Carregando...';
    document.getElementById('email_assunto_finalizacao').value = 'Carregando...';
    document.getElementById('email_corpo_finalizacao').value = 'Carregando...';
    
    const nomeArquivo = document.getElementById('nome_arquivo_senha_preview');
    if (nomeArquivo) nomeArquivo.innerText = 'Carregando...';

    fetch(`/telefonia/api/senhas/${id}/email-preview/`)
        .then(res => res.json())
        .then(data => {
            if(!data.error) {
                document.getElementById('email_para_finalizacao').value = data.to_email || '';
                document.getElementById('email_copia_finalizacao').value = data.bcc_email || '';
                document.getElementById('email_assunto_finalizacao').value = data.assunto || '';
                document.getElementById('email_corpo_finalizacao').value = data.corpo || '';
                if (nomeArquivo) nomeArquivo.innerText = data.filename || 'Documento.pdf';
            } else {
                console.error("Erro ao carregar preview do email:", data.error);
                if (nomeArquivo) nomeArquivo.innerText = 'Documento.pdf';
            }
        }).catch(err => {
            console.error("Erro:", err);
            if (nomeArquivo) nomeArquivo.innerText = 'Documento.pdf';
        });

    var myModal = new bootstrap.Modal(document.getElementById('modal-finalizar-senha'));
    myModal.show();
}

window.toggleCargoFinalizacao = function(valor) {
    const container = document.getElementById('dados_contrato_finalizacao');
    if (valor === 'colaborador') {
        container.style.display = 'block';
        if (!window.contratosColaboradorCache || window.contratosColaboradorCache.length === 0) {
            if (typeof window.carregarContratos === 'function') {
                window.carregarContratos();
            }
        }
        
        // Popula select se estiver vazio
        const selectElem = document.getElementById('select_contrato_finalizacao');
        if (selectElem.options.length <= 2 && window.contratosColaboradorCache) {
            window.contratosColaboradorCache.forEach(c => {
                selectElem.innerHTML += `<option value="${c.numero_contrato}">${c.numero_contrato}</option>`;
            });
        }
    } else {
        container.style.display = 'none';
        container.querySelectorAll('input').forEach(i => i.value = '');
    }
}

window.mudarContratoFinalizacao = function(valor) {
    const inputNumero = document.getElementById('numero_contrato_finalizacao');
    const inputEmpresa = document.getElementById('empresa_finalizacao');
    const inputFiscal = document.getElementById('fiscal_finalizacao');
    const inputUnidade = document.getElementById('unidade_fiscal_finalizacao');
    
    document.querySelector('.div_numero_contrato_finalizacao').style.display = 'block';
    document.querySelector('.div_empresa_finalizacao').style.display = 'block';
    document.querySelector('.div_fiscal_finalizacao').style.display = 'block';
    document.querySelector('.div_unidade_fiscal_finalizacao').style.display = 'block';

    if (valor === 'novo') {
        inputNumero.value = ''; inputEmpresa.value = ''; inputFiscal.value = ''; inputUnidade.value = '';
        inputNumero.readOnly = false; inputEmpresa.readOnly = false; inputFiscal.readOnly = false; inputUnidade.readOnly = false;
    } else if (valor !== '') {
        const contrato = window.contratosColaboradorCache.find(c => c.numero_contrato === valor);
        if (contrato) {
            inputNumero.value = contrato.numero_contrato; inputEmpresa.value = contrato.empresa_vinculada;
            inputFiscal.value = contrato.fiscal_contrato; inputUnidade.value = contrato.unidade_fiscal;
            inputNumero.readOnly = true; inputEmpresa.readOnly = true; inputFiscal.readOnly = true; inputUnidade.readOnly = true;
        }
    } else {
        document.querySelector('.div_numero_contrato_finalizacao').style.display = 'none';
        document.querySelector('.div_empresa_finalizacao').style.display = 'none';
        document.querySelector('.div_fiscal_finalizacao').style.display = 'none';
        document.querySelector('.div_unidade_fiscal_finalizacao').style.display = 'none';
        inputNumero.value = ''; inputEmpresa.value = ''; inputFiscal.value = ''; inputUnidade.value = '';
    }
}

const formFinalizarSenha = document.getElementById('form-finalizar-senha');
if (formFinalizarSenha) {
    formFinalizarSenha.addEventListener('submit', async function(e) {
        e.preventDefault();
        const id = document.getElementById('id_finalizacao_senha').value;
        const payload = {
            to_email: document.getElementById('email_para_finalizacao').value,
            bcc_email: document.getElementById('email_copia_finalizacao').value,
            assunto: document.getElementById('email_assunto_finalizacao').value,
            corpo: document.getElementById('email_corpo_finalizacao').value,
            status: 'finalizada'
        };

        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            // Endpoint novo que fará o UPDATE + Envio do Email
            const resposta = await fetch(`/telefonia/api/senhas/${id}/finalizar/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(payload)
            });

            if (!resposta.ok) {
                const data = await resposta.json();
                throw new Error(data.error || 'Erro ao finalizar a senha.');
            }

            Swal.fire('Sucesso!', 'Senha finalizada e e-mail enviado com sucesso.', 'success');
            bootstrap.Modal.getInstance(document.getElementById('modal-finalizar-senha')).hide();
            if(typeof $('#tabela-senhas') !== 'undefined') $('#tabela-senhas').DataTable().ajax.reload(null, false);
        } catch (error) {
            Swal.fire('Erro!', error.message, 'error');
        }
    });
}



// ==========================================
// EVENTOS - EMPRESTIMO
// ==========================================
const modal_evento = new bootstrap.Modal(document.getElementById('modal-emprestimo-evento'));
const form_evento = document.getElementById('form-emprestimo-evento');

function resetModalEvento(skipCarregar = false) {
    form_evento.reset();
    $('#evento_id').val('');
    $('#evento_aparelhos').val(null).trigger('change');
    $('#div_evento_observacoes').addClass('d-none');
    $('#btn-recolher-evento').addClass('d-none');
    $('#btn-salvar-evento').removeClass('d-none');
    
    // Habilitar campos
    $('#form-emprestimo-evento input, #form-emprestimo-evento select, #form-emprestimo-evento textarea').prop('disabled', false);
    
    if (!skipCarregar) {
        // O select2 deve recarregar os disponíveis
        carregarAparelhosEvento();
    }
}

document.getElementById('modal-emprestimo-evento').addEventListener('show.bs.modal', function (e) {
    if (e.relatedTarget) { // Foi clicado no botão "Novo"
        resetModalEvento();
    }
});

async function carregarAparelhosEvento() {
    try {
        const res = await fetch('/gestao_patrimonio/api/aparelhos-telefonicos/?status=estoque');
        const data = await res.json();
        
        const select = $('#evento_aparelhos');
        select.empty();
        
        // Filtra aparelhos com funcao_aparelho === 'eventos'
        data.forEach(ap => {
            if (ap.funcao_aparelho === 'eventos') {
                const opt = new Option(`${ap.patrimonio} - ${ap.modelo} (${ap.mac_address || 'Sem MAC'})`, ap.id, false, false);
                select.append(opt);
            }
        });
        
        select.trigger('change');
    } catch (e) {
        console.error("Erro ao carregar aparelhos de eventos", e);
    }
}

// Inicializa select2
$(document).ready(function() {
    $('#evento_aparelhos').select2({
        theme: 'bootstrap-5',
        dropdownParent: $('#modal-emprestimo-evento'),
        placeholder: "Selecione um ou mais aparelhos"
    });
});

async function salvarEvento() {
    if(!form_evento.checkValidity()) {
        form_evento.reportValidity();
        return;
    }
    
    const formData = new FormData(form_evento);
    // Para selects múltiplos
    const aparelhos = $('#evento_aparelhos').val() || [];
    formData.delete('aparelhos');
    aparelhos.forEach(a => formData.append('aparelhos', a));
    
    try {
        const res = await fetch('/telefonia/api/eventos/', {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': formData.get('csrfmiddlewaretoken') || document.querySelector('[name=csrfmiddlewaretoken]').value }
        });
        
        if (res.ok) {
            Swal.fire("Sucesso!", "Evento cadastrado com sucesso. Equipamentos instalados.", "success");
            modal_evento.hide();
            if ($.fn.DataTable.isDataTable('#tabela-recebidas-modal')) {
                $('#tabela-recebidas-modal').DataTable().ajax.reload(null, false);
            }
        } else {
            Swal.fire("Erro", "Verifique os campos obrigatórios.", "error");
        }
    } catch(e) {
        Swal.fire("Erro", "Erro ao conectar com o servidor.", "error");
    }
}

async function abrirModalEvento(id) {
    resetModalEvento(true);
    try {
        const res = await fetch(`/telefonia/api/eventos/${id}/`);
        const data = await res.json();
        
        $('#evento_id').val(data.id);
        $('#evento_nome').val(data.evento_nome);
        $('#evento_solicitante').val(data.solicitante);
        
        if (data.data_inicio) $('#evento_data_inicio').val(data.data_inicio.substring(0, 16));
        if (data.data_fim) $('#evento_data_fim').val(data.data_fim.substring(0, 16));
        
        $('#evento_local').val(data.local);
        
        // Bloquear os campos
        $('#form-emprestimo-evento input, #form-emprestimo-evento select').prop('disabled', true);
        
        // Esconder o select de aparelhos e mostrar lista fixa?
        // Como o select está disabled, ele serve como lista fixa, vamos preencher com as opções selecionadas.
        const select = $('#evento_aparelhos');
        select.empty();
        data.aparelhos_detalhes.forEach(ap => {
            const opt = new Option(`${ap.patrimonio} - ${ap.modelo} (${ap.mac_address || ''})`, ap.id, true, true);
            select.append(opt);
        });
        select.trigger('change');
        
        if (data.status === 'em_andamento') {
            $('#div_evento_observacoes').removeClass('d-none');
            $('#evento_observacoes').prop('disabled', false).val('');
            
            $('#btn-salvar-evento').addClass('d-none');
            $('#btn-recolher-evento').removeClass('d-none');
        } else {
            $('#div_evento_observacoes').removeClass('d-none');
            $('#evento_observacoes').prop('disabled', true).val(data.observacoes);
            
            $('#btn-salvar-evento').addClass('d-none');
            $('#btn-recolher-evento').addClass('d-none');
        }
        
        modal_evento.show();
        
    } catch(e) {
        Swal.fire("Erro", "Erro ao carregar os dados do evento.", "error");
    }
}

async function recolherEvento() {
    const id = $('#evento_id').val();
    const observacoes = $('#evento_observacoes').val();
    
    const formData = new FormData();
    formData.append('observacoes', observacoes);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    try {
        const res = await fetch(`/telefonia/api/eventos/${id}/recolher/`, {
            method: 'PATCH',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        });
        if (res.ok) {
            Swal.fire("Concluído!", "Equipamentos recolhidos e retornados ao estoque.", "success");
            modal_evento.hide();
            if ($.fn.DataTable.isDataTable('#tabela-recebidas-modal')) {
                $('#tabela-recebidas-modal').DataTable().ajax.reload(null, false);
            }
        } else {
            Swal.fire("Erro", "Não foi possível concluir a ação.", "error");
        }
    } catch(err) {
        Swal.fire("Erro", "Erro ao conectar.", "error");
    }
}

// Lógica Fase Administrativa Aparelhos
const modal_finalizar_administrativo = new bootstrap.Modal(document.getElementById('modal-finalizar-administrativo'));
const form_finalizar_administrativo = document.getElementById('form-finalizar-administrativo');

function abrirModalFinalizarAdministrativo(id) {
    document.getElementById('id_finalizacao_admin').value = id;
    form_finalizar_administrativo.reset();
    modal_finalizar_administrativo.show();
}

if (form_finalizar_administrativo) {
    form_finalizar_administrativo.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const id = document.getElementById('id_finalizacao_admin').value;
        const formData = new FormData(form_finalizar_administrativo);
        
        try {
            const res = await fetch(`/telefonia/api/solicitacoes/${id}/finalizar_administrativo/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });
            
            if (res.ok) {
                Swal.fire('Sucesso!', 'Fase administrativa concluída e solicitação encerrada.', 'success');
                modal_finalizar_administrativo.hide();
                // Tenta recarregar a tabela principal (ou a de recebidas no modal)
                if ($.fn.DataTable.isDataTable('#tabela-solicitacoes')) {
                    $('#tabela-solicitacoes').DataTable().ajax.reload();
                }
                if ($.fn.DataTable.isDataTable('#tabela-recebidas-modal')) {
                    $('#tabela-recebidas-modal').DataTable().ajax.reload();
                }
                if (typeof carregarWidgetRecebidas === 'function') {
                    carregarWidgetRecebidas();
                }
            } else {
                Swal.fire('Erro', 'Ocorreu um erro ao finalizar a demanda.', 'error');
            }
        } catch(err) {
            Swal.fire('Erro', 'Erro ao comunicar com o servidor.', 'error');
        }
    });
}

// ===============================
// Lógica para Nada Consta
// ===============================
const modal_nada_consta_el = document.getElementById('modal-nada-consta');
const modal_nada_consta = modal_nada_consta_el ? new bootstrap.Modal(modal_nada_consta_el) : null;
const form_nada_consta = document.getElementById('form-nada-consta');

if (form_nada_consta) {
    form_nada_consta.addEventListener('submit', function(e) {
        submitFormToAPI(e, form_nada_consta, modal_nada_consta, '/telefonia/api/nada_consta/', 'Nada Consta registrado com sucesso!');
    });

    // Autocomplete Servidor Nada Consta
    const inputServidorNC = document.getElementById('servidor_nada_consta');
    const dropdownResultadosNC = document.getElementById('autocomplete-resultados');
    const cardVinculosNC = document.getElementById('card-vinculos-encontrados');

    if (inputServidorNC) {
        let timeoutIdNC;
        inputServidorNC.addEventListener('input', function(e) {
            clearTimeout(timeoutIdNC);
            const valor = e.target.value;
            if (valor.length >= 3) {
                timeoutIdNC = setTimeout(() => buscarViculosSenhaNC(valor), 400);
            } else {
                dropdownResultadosNC.style.display = 'none';
            }
        });
        
        document.addEventListener('click', function(e) {
            if (!inputServidorNC.contains(e.target) && dropdownResultadosNC && !dropdownResultadosNC.contains(e.target)) {
                dropdownResultadosNC.style.display = 'none';
            }
        });
    }

    async function buscarViculosSenhaNC(query) {
        try {
            const resposta = await fetch(`/telefonia/api/senhas/buscar_por_nome/?q=${encodeURIComponent(query)}`);
            if (resposta.ok) {
                const dados = await resposta.json();
                mostrarResultadosAutocompleteNC(dados);
            }
        } catch (erro) {
            console.error('Erro na busca de servidor', erro);
        }
    }

    function mostrarResultadosAutocompleteNC(resultados) {
        dropdownResultadosNC.innerHTML = '';
        if (resultados.length === 0) {
            dropdownResultadosNC.style.display = 'none';
            return;
        }
        
        resultados.forEach(item => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'list-group-item list-group-item-action py-2';
            btn.innerHTML = `<i class="bi bi-person text-secondary me-2"></i> <strong>${item.usuario}</strong> <small class="text-muted ms-2">(Ramal: ${item.ramal || 'S/N'})</small>`;
            
            btn.addEventListener('click', () => selecionarServidorNC(item));
            dropdownResultadosNC.appendChild(btn);
        });
        
        dropdownResultadosNC.style.display = 'block';
    }

    function selecionarServidorNC(item) {
        inputServidorNC.value = item.usuario;
        dropdownResultadosNC.style.display = 'none';
        
        // Preencher FKs ocultas
        document.getElementById('hidden_senha_vinculada').value = item.id;
        document.getElementById('hidden_aparelho_vinculado').value = item.aparelho_id || '';
        
        // Exibir Card
        document.getElementById('vinculo-email').innerText = item.email || 'Não cadastrado';
        document.getElementById('vinculo-ramal').innerText = item.ramal + (item.aparelho_mac ? ` (MAC: ${item.aparelho_mac})` : ' (Sem Aparelho)');
        
        cardVinculosNC.style.display = 'block';
        document.getElementById('solicitar_desvinculacao').checked = false;
    }

    // Resetar vínculos ao fechar modal
    modal_nada_consta_el.addEventListener('hidden.bs.modal', function () {
        if(cardVinculosNC) cardVinculosNC.style.display = 'none';
        const hiddenSenha = document.getElementById('hidden_senha_vinculada');
        if(hiddenSenha) hiddenSenha.value = '';
        const hiddenAparelho = document.getElementById('hidden_aparelho_vinculado');
        if(hiddenAparelho) hiddenAparelho.value = '';
        const cbDesvincular = document.getElementById('solicitar_desvinculacao');
        if(cbDesvincular) cbDesvincular.checked = false;
    });
}

const modal_concluir_nada_consta_el = document.getElementById('modal-concluir-nada-consta');
const modal_concluir_nada_consta = modal_concluir_nada_consta_el ? new bootstrap.Modal(modal_concluir_nada_consta_el) : null;
const form_concluir_nada_consta = document.getElementById('form-concluir-nada-consta');

function abrirModalConcluirNadaConsta(id, protocolo, dataStr, unidade, servidor, desvincular=false, ramalVinculado='') {
    document.getElementById('id_nada_consta_conclusao').value = id;
    document.getElementById('txt_protocolo_nada_consta').innerText = protocolo;
    document.getElementById('txt_data_nada_consta').innerText = dataStr;
    document.getElementById('txt_unidade_nada_consta').innerText = unidade;
    document.getElementById('txt_servidor_nada_consta').innerText = servidor;
    
    form_concluir_nada_consta.reset();
    document.getElementById('valor_devido_nada_consta').value = '0,00';
    
    const alerta = document.getElementById('alerta-desvinculacao');
    if (desvincular) {
        document.getElementById('ramal-alerta').innerText = ramalVinculado || 'Não identificado';
        alerta.style.display = 'block';
    } else {
        alerta.style.display = 'none';
    }

    modal_concluir_nada_consta.show();
}

if (form_concluir_nada_consta) {
    form_concluir_nada_consta.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const id_solicitacao = document.getElementById('id_nada_consta_conclusao').value;
        const formData = new FormData(form_concluir_nada_consta);
        
        let valor_devido_str = formData.get('valor_devido');
        let valor_devido = valor_devido_str.replace(/\./g, '').replace(',', '.');
        formData.set('valor_devido', valor_devido);
        formData.set('status', 'concluida');
        
        try {
            const resposta = await fetch(`/telefonia/api/nada_consta/${id_solicitacao}/`, {
                method: 'PATCH',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            if (resposta.ok) {
                if (parseFloat(valor_devido) > 0) {
                    window.open(`/telefonia/nada_consta/${id_solicitacao}/pdf/`, '_blank');
                }
                await Swal.fire("Sucesso!", "Solicitação concluída com sucesso!", "success");
                form_concluir_nada_consta.reset();
                modal_concluir_nada_consta.hide();
                window.location.reload();
            } else {
                const erros = await resposta.json();
                console.log(erros);
                Swal.fire("Erro!", "Não foi possível concluir.", "error");
            }
        } catch (erro) {
            Swal.fire("Erro Crítico!", "Erro ao conectar com o servidor.", "error");
        }
    });
}

// Inicializar IMask para o campo de valor
document.addEventListener("DOMContentLoaded", function() {
    const inputValorDevido = document.getElementById('valor_devido_nada_consta');
    if (inputValorDevido && typeof IMask !== 'undefined') {
        IMask(inputValorDevido, {
            mask: Number,
            scale: 2,
            signed: false,
            thousandsSeparator: '.',
            padFractionalZeros: true,
            normalizeZeros: true,
            radix: ',',
            mapToRadix: ['.']
        });
    }
});

// -----------------------------------------
// EDITAR SENHA
// -----------------------------------------
window.abrirModalEditarSenha = async function(id) {
    try {
        const res = await fetch(`/telefonia/api/senhas/${id}/`);
        if (!res.ok) throw new Error("Erro ao carregar dados da senha.");
        const data = await res.json();
        
        document.getElementById('id_editar_senha').value = data.id || '';
        document.getElementById('editar_protocolo_senha').value = data.protocolo || '';
        document.getElementById('editar_solicitante_senha').value = data.solicitante || '';
        document.getElementById('editar_unidade_senha').value = data.unidade || '';
        document.getElementById('editar_sigla_unidade_senha').value = data.sigla_unidade || '';
        document.getElementById('editar_edificios_senha').value = data.edificios || 'Ed. Sede/Anexo';
        
        document.getElementById('editar_primeiro_nome_senha').value = data.primeiro_nome || '';
        document.getElementById('editar_sobrenome_senha').value = data.sobrenome || '';
        document.getElementById('editar_email_senha').value = data.email || '';
        document.getElementById('editar_ramal_senha').value = data.ramal || '';
        document.getElementById('editar_categoria_senha').value = data.categoria || 'DDD';
        document.getElementById('editar_senha_registrada').value = data.senha || '';
        
        const cargo = data.cargo || 'servidor';
        document.getElementById('editar_cargo_senha').value = cargo;
        toggleCargoEditarSenha(cargo);
        
        if (cargo === 'colaborador') {
            document.getElementById('editar_numero_contrato_senha').value = data.numero_contrato || '';
            document.getElementById('editar_empresa_vinculada_senha').value = data.empresa_vinculada || '';
            document.getElementById('editar_fiscal_contrato_senha').value = data.fiscal_contrato || '';
            document.getElementById('editar_unidade_fiscal_senha').value = data.unidade_fiscal || '';
        } else {
            document.getElementById('editar_numero_contrato_senha').value = '';
            document.getElementById('editar_empresa_vinculada_senha').value = '';
            document.getElementById('editar_fiscal_contrato_senha').value = '';
            document.getElementById('editar_unidade_fiscal_senha').value = '';
        }
        
        document.getElementById('editar_desvio_senha').value = (data.desvio === true || data.desvio === 'True' || data.desvio === 'true') ? 'True' : 'False';
        document.getElementById('editar_ativo_senha').value = (data.ativo === true || data.ativo === 'True' || data.ativo === 'true') ? 'True' : 'False';
        document.getElementById('editar_tel_desvio_externo').value = data.tel_desvio_externo || '';
        
        new bootstrap.Modal(document.getElementById('modal-editar-senha')).show();
    } catch (error) {
        Swal.fire('Erro!', error.message, 'error');
    }
};

const formEditarSenha = document.getElementById('form-editar-senha');
if (formEditarSenha) {
    formEditarSenha.addEventListener('submit', async function(e) {
        e.preventDefault();
        const id = document.getElementById('id_editar_senha').value;
        const btnSubmit = document.querySelector('button[form="form-editar-senha"]');
        const originalText = btnSubmit.innerHTML;
        btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Salvando...';
        btnSubmit.disabled = true;

        const formData = new FormData(formEditarSenha);
        const data = Object.fromEntries(formData.entries());
        data.desvio = (data.desvio === 'True' || data.desvio === true);
        data.ativo = (data.ativo === 'True' || data.ativo === true);
        delete data.id; // Nao enviar o ID no payload
        
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const res = await fetch(`/telefonia/api/senhas/${id}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data)
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || JSON.stringify(err));
            }

            Swal.fire('Sucesso!', 'Solicitação de senha editada com sucesso.', 'success');
            bootstrap.Modal.getInstance(document.getElementById('modal-editar-senha')).hide();
            if(typeof $('#tabela-senhas') !== 'undefined') $('#tabela-senhas').DataTable().ajax.reload(null, false);
        } catch (error) {
            Swal.fire('Erro!', 'Ocorreu um erro ao editar a solicitação: ' + error.message, 'error');
        } finally {
            btnSubmit.innerHTML = originalText;
            btnSubmit.disabled = false;
        }
    });
}
