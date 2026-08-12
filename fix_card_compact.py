import os
import re

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

    # Fix card-compact-header, card-compact-body, etc.
    content = content.replace('card-compact-header', 'card-header')
    content = content.replace('card-compact-body', 'card-body')
    content = content.replace('card-compact-title', 'card-title')
    content = content.replace('card-compact-footer', 'card-footer')

    if content != original:
        with open(filepath, 'w', encoding=encoding_used) as f:
            f.write(content)
        print(f'Fixed: {filepath}')

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
