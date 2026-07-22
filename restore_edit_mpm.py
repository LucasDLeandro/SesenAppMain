import os

html_content = """
<!-- Modal Editar MPM -->
<div class="modal fade modal-ordens-wrapper" id="modalEditarMPM" tabindex="-1" aria-labelledby="modalEditarMPMLabel" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered modal-xl modal-dialog-scrollable">
    <div class="modal-content border-0 shadow-lg bg-body rounded-4">
      
      <!-- HEADER -->
      <div class="modal-header border-0 pb-3 pt-4 px-4 bg-light rounded-top-4 d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center gap-3">
          <div class="bg-warning bg-opacity-10 text-warning rounded-circle d-flex align-items-center justify-content-center flex-shrink-0" style="width: 48px; height: 48px;">
            <i class="bi bi-pencil-square fs-4"></i>
          </div>
          <div>
            <h5 class="modal-title fw-bolder mb-0 text-dark">Editar Relatório de Manutenção Preventiva</h5>
            <small class="text-muted" id="editMpmModalSubtitle">Alterar dados da vistoria</small>
          </div>
        </div>
        <button type="button" class="btn btn-secondary btn-sm px-3 rounded-pill fw-semibold shadow-sm" data-bs-dismiss="modal">
          <i class="bi bi-x-lg me-1"></i> Fechar
        </button>
      </div>

      <div class="modal-body p-4 bg-light bg-opacity-50">
        <div id="editMpmLoadingInfo" class="text-center py-4 d-none">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="text-muted mt-2 mb-0 small">Buscando dados da MPM...</p>
        </div>
        
        <form id="formEditarMpm" method="POST" enctype="multipart/form-data">
          <!-- ID Oculto para identificar a MPM na edição -->
          <input type="hidden" name="mpm_id" id="editMpmId">

          <div class="row g-4" id="editMpmFormContent">
            <!-- 1. DADOS BÁSICOS & CLIENTE -->
            <div class="col-12">
                <div class="card border-0 shadow-sm rounded-4">
                    <div class="card-body p-4">
                        <h6 class="fw-bold text-secondary text-uppercase mb-3" style="font-size: 0.85rem; letter-spacing: 0.5px;">
                            <i class="bi bi-building me-2"></i> 1. Dados do Cliente e Equipamento
                        </h6>
                        <div class="row g-3">
                            <div class="col-md-3">
                                <label class="form-label small fw-bold text-muted">Contrato / Cliente</label>
                                <select class="form-select" id="editMpmContrato" name="contrato">
                                    <option value="" selected>Selecione um contrato...</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label class="form-label small fw-bold text-muted">Mês/Ano de Referência <span class="text-danger">*</span></label>
                                <input type="month" class="form-control" id="editMpmMes" name="mes_referencia" required>
                            </div>
                            <div class="col-md-3">
                                <label class="form-label small fw-bold text-muted">Elevador <span class="text-danger">*</span></label>
                                <select class="form-select" id="editMpmElevador" name="elevador" required>
                                    <option value="" selected disabled>Selecione...</option>
                                    <option value="Social 1 - M2674">Social 1 - M2674</option>
                                    <option value="Social 2 - M2675">Social 2 - M2675</option>
                                    <option value="Social 3 - M2676">Social 3 - M2676</option>
                                    <option value="Social 4 - M2677">Social 4 - M2677</option>
                                    <option value="Social 5 - M2678">Social 5 - M2678</option>
                                    <option value="Serviço 6 - M2679">Serviço 6 - M2679</option>
                                    <option value="Privativo 7 - M2680">Privativo 7 - M2680</option>
                                    <option value="Social 8 - M2681">Social 8 - M2681</option>
                                    <option value="Social 9 - M2682">Social 9 - M2682</option>
                                    <option value="Privativo 10 - M2683">Privativo 10 - M2683</option>
                                    <option value="Social 11 - M2684">Social 11 - M2684</option>
                                    <option value="Social 12 - M2685">Social 12 - M2685</option>
                                    <option value="Social 13 - M2686">Social 13 - M2686</option>
                                    <option value="Serviço 14 - M2687">Serviço 14 - M2687</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label class="form-label small fw-bold text-muted">Situação do Equipamento <span class="text-danger">*</span></label>
                                <select class="form-select" id="editMpmSituacao" name="situacao_equipamento" required>
                                    <option value="Em Funcionamento">Em Funcionamento</option>
                                    <option value="Parado">Parado</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 2. CHECKLIST DE SERVIÇO -->
            <div class="col-12">
                <div class="card border-0 shadow-sm rounded-4">
                    <div class="card-body p-4">
                        <h6 class="fw-bold text-secondary text-uppercase mb-3" style="font-size: 0.85rem; letter-spacing: 0.5px;">
                            <i class="bi bi-list-check me-2"></i> 2. Serviço Prestado
                        </h6>
                        <div class="row g-3">
                            <div class="col-md-12">
                                <label class="form-label small fw-bold text-muted">Descrição do serviço executado / a executar</label>
                                <input type="text" class="form-control" id="editMpmDescricaoServico" name="descricao_servico" placeholder="Ex: Foi realizada a revisão mensal...">
                            </div>
                            
                            <!-- Checklists -->
                            <div class="col-md-2 col-sm-4 col-6">
                                <label class="form-label small fw-bold text-muted">Apresentação</label>
                                <select class="form-select form-select-sm" id="editMpmApresentacao" name="apresentacao">
                                    <option value="OK" selected>OK</option><option value="NOK">NOK</option><option value="NA">N/A</option>
                                </select>
                            </div>
                            <div class="col-md-2 col-sm-4 col-6">
                                <label class="form-label small fw-bold text-muted">Qualidade</label>
                                <select class="form-select form-select-sm" id="editMpmPerformance" name="performance_qualidade">
                                    <option value="OK" selected>OK</option><option value="NOK">NOK</option><option value="NA">N/A</option>
                                </select>
                            </div>
                            <div class="col-md-2 col-sm-4 col-6">
                                <label class="form-label small fw-bold text-muted">Limit. Velocidade</label>
                                <select class="form-select form-select-sm" id="editMpmLimitador" name="limitador_velocidade">
                                    <option value="OK" selected>OK</option><option value="NOK">NOK</option><option value="NA">N/A</option>
                                </select>
                            </div>
                            <div class="col-md-2 col-sm-4 col-6">
                                <label class="form-label small fw-bold text-muted">Controle (EL)</label>
                                <select class="form-select form-select-sm" id="editMpmControle" name="controle">
                                    <option value="OK" selected>OK</option><option value="NOK">NOK</option><option value="NA">N/A</option>
                                </select>
                            </div>
                            <div class="col-md-2 col-sm-4 col-6">
                                <label class="form-label small fw-bold text-muted">Poço (P)</label>
                                <select class="form-select form-select-sm" id="editMpmPoco" name="poco">
                                    <option value="OK" selected>OK</option><option value="NOK">NOK</option><option value="NA">N/A</option>
                                </select>
                            </div>
                            <div class="col-md-2 col-sm-4 col-6">
                                <label class="form-label small fw-bold text-muted">Encerramento</label>
                                <select class="form-select form-select-sm" id="editMpmEncerramento" name="encerramento">
                                    <option value="OK" selected>OK</option><option value="NOK">NOK</option><option value="NA">N/A</option>
                                </select>
                            </div>

                            <div class="col-md-6 mt-4">
                                <label class="form-label small fw-bold text-muted">Observação (Adicional)</label>
                                <textarea class="form-control" id="editMpmObservacao" name="observacao" rows="2" placeholder="Observações do serviço..."></textarea>
                            </div>
                            <div class="col-md-6 mt-4">
                                <label class="form-label small fw-bold text-muted">Foto do Poço (Opcional)</label>
                                <input type="file" class="form-control" id="editMpmFotoPoco" name="foto_poco" accept="image/*">
                            </div>
                            <div class="col-md-12 mt-4">
                                <label class="form-label small fw-bold text-muted">Anexo / Outra Mídia (Opcional)</label>
                                <input type="file" class="form-control" id="editMpmMidia" name="midia">
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 3 e 4. EXECUÇÃO E VISTO -->
            <div class="col-md-6">
                <div class="card border-0 shadow-sm rounded-4 h-100">
                    <div class="card-body p-4">
                        <h6 class="fw-bold text-secondary text-uppercase mb-3" style="font-size: 0.85rem; letter-spacing: 0.5px;">
                            <i class="bi bi-person-badge me-2"></i> 3. Execução Técnica
                        </h6>
                        <div class="row g-3">
                            <div class="col-md-12">
                                <label class="form-label small fw-bold text-muted">Nome do Técnico</label>
                                <select class="form-select" id="editMpmTecnicoNome" name="tecnico">
                                    <option value="" selected>Selecione o técnico</option>
                                </select>
                            </div>
                            <div class="col-md-4">
                                <label class="form-label small fw-bold text-muted">Chapa</label>
                                <input type="text" class="form-control" id="editMpmTecnicoChapa" name="tecnico_chapa">
                            </div>
                            <div class="col-md-8">
                                <label class="form-label small fw-bold text-muted">Data da Execução</label>
                                <input type="date" class="form-control" id="editMpmDataExecucao" name="data_execucao">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-muted">Hora Chegada</label>
                                <input type="time" class="form-control" id="editMpmHoraChegada" name="hora_chegada">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-muted">Hora Saída</label>
                                <input type="time" class="form-control" id="editMpmHoraSaida" name="hora_saida">
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="card border-0 shadow-sm rounded-4 h-100">
                    <div class="card-body p-4">
                        <h6 class="fw-bold text-secondary text-uppercase mb-3" style="font-size: 0.85rem; letter-spacing: 0.5px;">
                            <i class="bi bi-pen me-2"></i> 4. Visto do Cliente
                        </h6>
                        <div class="row g-3">
                            <div class="col-md-12">
                                <label class="form-label small fw-bold text-muted">Nome do Representante</label>
                                <input type="text" class="form-control" id="editMpmClienteNome" name="cliente_nome">
                            </div>
                            <div class="col-md-12">
                                <label class="form-label small fw-bold text-muted">E-mail</label>
                                <input type="email" class="form-control" id="editMpmClienteEmail" name="cliente_email" placeholder="email@tse.jus.br">
                            </div>
                            <div class="col-md-12">
                                <label class="form-label small fw-bold text-muted">Comentários do Cliente</label>
                                <input type="text" class="form-control" id="editMpmClienteComentarios" name="cliente_comentarios" placeholder="...">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-muted">Data do Visto</label>
                                <input type="date" class="form-control" id="editMpmClienteData" name="cliente_data">
                            </div>
                        </div>
                    </div>
                </div>
            </div>

          </div>

          <div class="d-flex justify-content-end gap-2 mt-4 pt-3 border-top">
            <button type="button" class="btn btn-light rounded-pill px-4 fw-semibold" data-bs-dismiss="modal">Cancelar</button>
            <button type="submit" class="btn btn-primary rounded-pill px-4 fw-bold shadow-sm">
              <i class="bi bi-check-lg me-2"></i> Salvar Alterações
            </button>
          </div>

        </form>
      </div>
    </div>
  </div>
</div>
"""

filepath = r"c:\Lucas\SesenAppMain\elevadores\templates\ordens\includes\modais_mpm.html"
with open(filepath, 'a', encoding='utf-8') as f:
    f.write("\n" + html_content + "\n")
