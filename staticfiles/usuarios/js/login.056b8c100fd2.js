        document.getElementById('login-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const btn = document.getElementById('login-btn');
            const spinner = document.getElementById('spinner');
            const btnText = document.getElementById('btn-text');

            // Loading state
            btn.disabled = true;
            spinner.style.display = 'inline-block';
            btnText.textContent = 'Autenticando...';

            try {
                // Remove trailing slashes and ensure exact match, or use django {% url 'login' %}
                const response = await fetch('/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        // CSRF is optional for JWT endpoints if properly configured, but let's just pass data
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Login bem-sucedido!',
                        text: 'Redirecionando...',
                        showConfirmButton: false,
                        timer: 1500
                    }).then(() => {
                        window.location.href = data.redirect_url || '/';
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Falha no login',
                        text: data.error || 'Usuário ou senha inválidos.'
                    });
                    btn.disabled = false;
                    spinner.style.display = 'none';
                    btnText.textContent = 'Entrar';
                }
            } catch (error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro de conexão',
                    text: 'Não foi possível conectar ao servidor.'
                });
                btn.disabled = false;
                spinner.style.display = 'none';
                btnText.textContent = 'Entrar';
            }
        });
