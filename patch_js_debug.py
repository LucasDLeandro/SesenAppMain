import re

with open(r'C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js', 'r', encoding='utf-8') as f:
    content = f.read()


old_ajax = """    $.ajax({
        url: endpoint,
        type: 'POST',
        data: JSON.stringify({ justificativa: justificativa }),
        contentType: 'application/json',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        success: function() {
            Swal.fire('Cancelado!', 'A solicita\u00e7\u00e3o foi cancelada.', 'success');
            // Recarrega as tabelas para refletir o cancelamento
            if ($.fn.DataTable.isDataTable('#tabela-recebidas-modal')) {
                $('#tabela-recebidas-modal').DataTable().ajax.reload(null, false);
            }
            if ($.fn.DataTable.isDataTable('#tabela-senhas')) {
                $('#tabela-senhas').DataTable().ajax.reload(null, false);
            }
            if (typeof carregarWidgetRecebidas === 'function') {
                carregarWidgetRecebidas();
            }
            if (typeof carregarWidgetDemandasDashboard === 'function') {
                carregarWidgetDemandasDashboard();
            }
        },
        error: function() {
            Swal.fire('Erro', 'Ocorreu um erro ao cancelar.', 'error');
        }
    });"""

new_ajax = """    $.ajax({
        url: endpoint,
        type: 'POST',
        data: JSON.stringify({ justificativa: justificativa }),
        contentType: 'application/json',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        success: function() {
            Swal.fire('Cancelado!', 'A solicita\u00e7\u00e3o foi cancelada.', 'success');
            // Recarrega as tabelas para refletir o cancelamento
            if ($.fn.DataTable.isDataTable('#tabela-recebidas-modal')) {
                $('#tabela-recebidas-modal').DataTable().ajax.reload(null, false);
            }
            if ($.fn.DataTable.isDataTable('#tabela-senhas')) {
                $('#tabela-senhas').DataTable().ajax.reload(null, false);
            }
            if (typeof carregarWidgetRecebidas === 'function') {
                carregarWidgetRecebidas();
            }
            if (typeof carregarWidgetDemandasDashboard === 'function') {
                carregarWidgetDemandasDashboard();
            }
        },
        error: function(xhr) {
            console.error("ERRO AO CANCELAR:", xhr.responseText);
            let erroMsg = "Ocorreu um erro ao cancelar. Verifique o console.";
            try {
                let response = JSON.parse(xhr.responseText);
                if (response.error) {
                    erroMsg = response.error;
                    console.error("TRACEBACK DO BACKEND:", response.traceback);
                }
            } catch (e) {}
            Swal.fire('Erro', erroMsg, 'error');
        }
    });"""

content = content.replace(old_ajax, new_ajax)

with open(r'C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("JS Debug Patch Applied!")
