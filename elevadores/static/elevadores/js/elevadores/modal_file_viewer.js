window.openGenericFileViewer = function(fileUrl, fileName) {
    if (!fileUrl) return;
    
    const container = document.getElementById('fileViewerContainer');
    const downloadBtn = document.getElementById('btnDownloadFileViewer');
    const modalTitle = document.getElementById('modalFileViewerLabel');
    
    // Configura o link de download
    downloadBtn.href = fileUrl;
    
    // Tenta extrair o nome do arquivo da URL se não for passado
    let name = fileName || fileUrl.split('/').pop().split('?')[0];
    modalTitle.innerHTML = `<i class="bi bi-file-earmark-text me-2 text-primary fs-4"></i> ${name}`;
    
    // Identifica o tipo pelo ramal
    const ext = name.split('.').pop().toLowerCase();
    
    container.innerHTML = ''; // Limpa o container
    
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) {
        // Imagem
        container.innerHTML = `<img src="${fileUrl}" class="img-fluid" style="max-height: 70vh; object-fit: contain;" alt="${name}">`;
    } else if (['mp4', 'webm', 'ogg'].includes(ext)) {
        // Vídeo
        container.innerHTML = `
            <video controls class="w-100" style="max-height: 70vh;">
                <source src="${fileUrl}" type="video/${ext === 'mp4' ? 'mp4' : (ext === 'webm' ? 'webm' : 'ogg')}">
                Seu navegador não suporta a tag de vídeo.
            </video>
        `;
    } else if (['pdf'].includes(ext)) {
        // PDF
        // Adiciona um timestamp na URL para evitar cache do header X-Frame-Options antigo
        const timestampUrl = fileUrl.includes('?') ? `${fileUrl}&t=${new Date().getTime()}` : `${fileUrl}?t=${new Date().getTime()}`;
        
        container.innerHTML = `<object data="${timestampUrl}" type="application/pdf" width="100%" height="600px" style="border: none;">
            <iframe src="${timestampUrl}" width="100%" height="600px" style="border: none;">
                <p>Seu navegador não suporta a visualização de PDFs. <a href="${fileUrl}">Clique aqui para baixar</a></p>
            </iframe>
        </object>`;
    } else {
        // Outros arquivos (Word, Excel, etc)
        container.innerHTML = `
            <div class="p-5 text-center">
                <i class="bi bi-file-earmark-arrow-down text-secondary" style="font-size: 5rem;"></i>
                <h4 class="mt-3 text-dark">Arquivo não suporta visualização direta</h4>
                <p class="text-muted">Clique em "Baixar Arquivo" para visualizá-lo em seu dispositivo.</p>
            </div>
        `;
    }
    
    // Mostra o modal
    const modalEl = document.getElementById('modalFileViewer');
    // Para sobrepor outros modais, ajusta o z-index
    const m = new bootstrap.Modal(modalEl);
    m.show();
}
