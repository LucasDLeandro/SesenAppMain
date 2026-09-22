        document.getElementById('trocar-senha-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const senha_atual = document.getElementById('senha_atual').value;
            const nova_senha = document.getElementById('nova_senha').value;
            const confirma_senha = document.getElementById('confirma_senha').value;
            const btn = document.getElementById('btn-submit');
            const spinner = document.getElementById('spinner');
            const btnText = document.getElementById('btn-text');

            if (nova_senha !== confirma_senha) {
                Swal.fire('Atenção', 'A nova senha e a confirmação não conferem.', 'warning');
                return;
            }

            // Loading state
            btn.disabled = true;
            spinner.style.display = 'inline-block';
            btnText.textContent = 'Processando...';

            try {
                const response = await fetch('/trocar-senha/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ senha_atual, nova_senha, confirma_senha })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Senha alterada!',
                        text: 'Sua nova senha foi salva com sucesso.',
                        showConfirmButton: false,
                        timer: 1500
                    }).then(() => {
                        // Após trocar a senha, o JWT já está no cookie e será válido.
                        // Só recarregar para o backend que fará a troca.
                        // Ou idealmente o JWT antigo continua válido, o backend não o invalidou 
                        // a menos que tivéssemos feito logout de todas as sessões.
                        window.location.href = data.redirect_url || '/';
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Falha ao trocar senha',
                        text: data.error || 'Verifique seus dados e tente novamente.'
                    });
                    btn.disabled = false;
                    spinner.style.display = 'none';
                    btnText.textContent = 'Salvar Nova Senha';
                }
            } catch (error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro de conexão',
                    text: 'Não foi possível conectar ao servidor.'
                });
                btn.disabled = false;
                spinner.style.display = 'none';
                btnText.textContent = 'Salvar Nova Senha';
            }
        });
