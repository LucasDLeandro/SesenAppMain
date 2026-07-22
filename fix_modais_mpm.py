import os

filepath = r"c:\Lucas\SesenAppMain\elevadores\templates\ordens\includes\modais_mpm.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the exact start and end to replace
start_idx = content.find('<label class="form-label small fw-bold text-muted">Apresentação</label>')
end_idx = content.find('<!-- 4. VISTO DO CLIENTE -->')
if end_idx == -1:
    end_idx = content.find('<i class="bi bi-pen me-2"></i> 4. Visto do Cliente')

if start_idx != -1 and end_idx != -1:
    # We will reconstruct the whole section 2 and 3
    # Actually, let's just find the exact block.
    # It's better to just write the HTML block we want and inject it.
    pass
