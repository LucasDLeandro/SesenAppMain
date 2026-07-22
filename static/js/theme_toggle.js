    const html = document.documentElement;
    const themeIcon = document.getElementById('themeIcon');
    const themeToggler = document.getElementById('themeToggler');

    function updateIcon(theme) {
        if (theme === 'dark') {
            themeIcon.classList.remove('bi-sun-fill');
            themeIcon.classList.add('bi-moon-stars-fill');
        } else {
            themeIcon.classList.remove('bi-moon-stars-fill');
            themeIcon.classList.add('bi-sun-fill');
        }
    }

    function setTheme(theme) {
        html.setAttribute('data-bs-theme', theme);
        updateIcon(theme);
        localStorage.setItem('theme', theme);
    }

    // Inicialização do tema salvo
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    themeToggler.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });

    // Torna modais grandes responsivos (fullscreen no celular)
    document.addEventListener('DOMContentLoaded', function() {
        const largeModals = document.querySelectorAll('.modal-lg, .modal-xl');
        largeModals.forEach(function(modal) {
            modal.classList.add('modal-fullscreen-md-down');
        });
    });
