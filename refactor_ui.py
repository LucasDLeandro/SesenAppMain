import os
import re

def refactor_file(filepath):
    encoding_used = 'utf-8'
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='utf-16') as f:
                content = f.read()
            encoding_used = 'utf-16'
        except Exception:
            print(f"Skipping {filepath} due to encoding.")
            return

    original = content

    # 1. Dashboard Header
    content = re.sub(r'class="dashboard-header(?! compact-header)', r'class="dashboard-header compact-header', content)
    
    # 2. H2 to H4 inside dashboard-header (approximate regex)
    # Finds <div class="dashboard-header... down to <h2 ...> and replaces h2 with h4
    def header_sub(match):
        header_block = match.group(0)
        header_block = header_block.replace('<h2', '<h4').replace('</h2>', '</h4>')
        # Also replace btn-lg with btn-compact in the header block
        header_block = header_block.replace('btn-lg', 'btn-compact')
        return header_block
    
    content = re.sub(r'<div class="dashboard-header.*?(?=<div class="dashboard-header|$)', header_sub, content, flags=re.DOTALL)
    
    # Alternatively, just replace btn-lg globally if they are yellow primary buttons
    content = content.replace('btn-warning btn-lg', 'btn-warning btn-compact')
    content = content.replace('btn-primary btn-lg', 'btn-primary btn-compact')
    
    # 3. KPI Grid spacing
    content = content.replace('class="row g-3', 'class="row g-compact')
    
    # 4. Card Compact
    content = re.sub(r'class="card(?! card-compact)', r'class="card card-compact', content)
    
    # 5. Table Dense
    content = re.sub(r'<table([^>]*?)class="([^"]*?)"', 
                     lambda m: f'<table{m.group(1)}class="{m.group(2)} table-dense"' if 'table-dense' not in m.group(2) else m.group(0), 
                     content)

    if content != original:
        with open(filepath, 'w', encoding=encoding_used) as f:
            f.write(content)
        print(f'Refactored: {filepath}')

def main():
    root_dir = r'C:\Lucas\SesenAppMain'
    
    # Also templates dir
    for root, dirs, files in os.walk(root_dir):
        if any(x in root for x in ['node_modules', '.git', 'env', '__pycache__', 'migrations', '.kilo']): 
            continue
            
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                refactor_file(filepath)

if __name__ == '__main__':
    main()
