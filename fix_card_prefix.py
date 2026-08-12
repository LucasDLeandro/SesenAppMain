import os

def fix_file(filepath):
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
            return

    original = content

    content = content.replace('class="card card-header', 'class="card-header')
    content = content.replace('class="card card-body', 'class="card-body')
    content = content.replace('class="card card-title', 'class="card-title')
    content = content.replace('class="card card-footer', 'class="card-footer')

    if content != original:
        with open(filepath, 'w', encoding=encoding_used) as f:
            f.write(content)
        print(f'Fixed card prefix: {filepath}')

def main():
    root_dir = r'C:\Lucas\SesenAppMain'
    for root, dirs, files in os.walk(root_dir):
        if any(x in root for x in ['node_modules', '.git', 'env', '__pycache__', 'migrations', '.kilo']): 
            continue
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                fix_file(filepath)

if __name__ == '__main__':
    main()
