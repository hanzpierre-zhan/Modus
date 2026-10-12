(() => {
    const button = document.getElementById('sidebar-logo-change');
    const input = document.getElementById('sidebar-logo-file');
    if (!button || !input) return;
    button.addEventListener('click', () => input.click());
    input.addEventListener('change', async () => {
        const file = input.files[0];
        if (!file) return;
        if (file.size > 2 * 1024 * 1024) {
            window.nucleusAlert('La imagen debe pesar como máximo 2 MB.');
            input.value = '';
            return;
        }
        const form = new FormData();
        form.append('file', file);
        button.disabled = true;
        button.setAttribute('aria-busy', 'true');
        try {
            const response = await fetch('/api/branding/logo', {method: 'POST', body: form, credentials: 'same-origin'});
            if (!response.headers.get('content-type')?.includes('application/json')) throw new Error('Revisa tu sesión y vuelve a intentar.');
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'No se pudo guardar el logo.');
            button.querySelector('img').src = result.url;
        } catch (error) {
            window.nucleusAlert(error.message);
        } finally {
            button.disabled = false;
            button.removeAttribute('aria-busy');
            input.value = '';
        }
    });
})();
