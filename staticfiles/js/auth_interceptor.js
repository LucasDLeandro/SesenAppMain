/**
 * Interceptador de requisições para renovação automática de token JWT
 * 
 * Este script intercepta todas as requisições fetch e respostas,
 * tratando erros de autenticação (401) tentando renovar o token
 * antes de redirecionar para login.
 */

// Store original fetch
const originalFetch = window.fetch;

// Flag para evitar requisições recursivas de refresh
let isRefreshing = false;
let refreshSubscribers = [];

/**
 * Notifica todos os subscribers após renovação bem-sucedida
 */
function onRefreshed(token) {
    refreshSubscribers.forEach(callback => callback(token));
    refreshSubscribers = [];
}

/**
 * Adiciona callback à fila de espera
 */
function addRefreshSubscriber(callback) {
    refreshSubscribers.push(callback);
}

/**
 * Tenta renovar o access_token usando o refresh_token
 */
async function refreshAccessToken() {
    try {
        const response = await originalFetch('/api/token/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            const data = await response.json();
            return data.access;
        } else {
            // Refresh falhou, redireciona para login
            window.location.href = '/login/';
            return null;
        }
    } catch (error) {
        console.error('Erro ao renovar token:', error);
        window.location.href = '/login/';
        return null;
    }
}

/**
 * Intercepta fetch e trata erros de autenticação
 */
window.fetch = async function(...args) {
    let [resource, config] = args;
    
    // Não intercepta requisições de login ou refresh
    if (resource.includes('/login/') || resource.includes('/api/token')) {
        return originalFetch.apply(this, args);
    }

    let response = await originalFetch.apply(this, args);

    // Se recebe 401 (Unauthorized), tenta renovar token
    if (response.status === 401 && !isRefreshing) {
        isRefreshing = true;

        const newToken = await refreshAccessToken();

        if (newToken) {
            isRefreshing = false;
            onRefreshed(newToken);

            // Repete a requisição original com o novo token
            if (!config) {
                config = {};
            }
            if (!config.headers) {
                config.headers = {};
            }
            config.headers['Authorization'] = `Bearer ${newToken}`;
            return originalFetch(resource, config);
        } else {
            isRefreshing = false;
            return response; // Deixa a resposta 401 prosseguir
        }
    } else if (response.status === 401 && isRefreshing) {
        // Se já está refreshing, enfileira a requisição
        return new Promise(resolve => {
            addRefreshSubscriber(token => {
                if (!config) {
                    config = {};
                }
                if (!config.headers) {
                    config.headers = {};
                }
                config.headers['Authorization'] = `Bearer ${token}`;
                resolve(originalFetch(resource, config));
            });
        });
    }

    return response;
};

console.log('✓ JWT Auth Interceptor carregado');
