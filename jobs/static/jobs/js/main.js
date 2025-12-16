// Theme initialization - apply immediately to prevent flash
(function() {
    const theme = document.body.getAttribute('data-theme') || 
                  (document.body.classList.contains('dark-theme') ? 'dark' : 'light');
    if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        document.body.classList.add('dark-theme');
    }
})();

// Theme toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Create form and submit
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = window.THEME_TOGGLE_URL || themeToggle.getAttribute('data-action') || '/jobs/toggle-theme/';
            
            // Get CSRF token
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
            
            const csrfToken = getCookie('csrftoken') || 
                            document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                            document.querySelector('meta[name=csrf-token]')?.getAttribute('content');
            
            if (csrfToken) {
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrfmiddlewaretoken';
                csrfInput.value = csrfToken;
                form.appendChild(csrfInput);
            }
            
            const themeInput = document.createElement('input');
            themeInput.type = 'hidden';
            themeInput.name = 'theme';
            themeInput.value = newTheme;
            form.appendChild(themeInput);
            
            document.body.appendChild(form);
            form.submit();
        });
    }

    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert.auto-dismiss');
    alerts.forEach(function(alert) {
        const delay = parseInt(alert.getAttribute('data-auto-dismiss')) || 3000;
        setTimeout(function() {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } else {
                alert.style.transition = 'opacity 0.3s';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            }
        }, delay);
    });
});

