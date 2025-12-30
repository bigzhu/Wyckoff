import os
import re

def fix_nested_links(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find nested links where the inner link points to 术语速查手册.md
    # We look for: [ ... [inner](...术语速查手册.md...) ... ](...)
    # We capture:
    # 1. The start of the outer link text
    # 2. The inner link text
    # 3. The inner link url (to discard)
    # 4. The end of the outer link text
    
    # This regex is a bit complex. Let's try to just find lines with this issue and process them.
    # A line has an issue if it has `](` *after* a `](...术语速查手册.md...)` but *before* the next `[`?
    # No, that's not reliable.
    
    # Simpler regex: match the specific nested structure
    # Outer link start: \[
    # Content before inner: ([^\[\]]*)
    # Inner link: \[([^\]]+)\]\([^)]*术语速查手册\.md[^)]*\)
    # Content after inner: ([^\[\]]*)
    # Outer link end: \]
    # Outer link URL: \([^)]+\)
    
    pattern = re.compile(r'\[([^\[\]]*)\[([^\]]+)\]\([^)]*术语速查手册\.md[^)]*\)([^\[\]]*)\]\(([^)]+)\)')
    
    def replacer(match):
        prefix = match.group(1)
        inner_text = match.group(2)
        suffix = match.group(3)
        outer_url = match.group(4)
        print(f"Fixing nested link in {file_path}: [{prefix}{inner_text}{suffix}]({outer_url})")
        return f'[{prefix}{inner_text}{suffix}]({outer_url})'

    new_content = content
    # Also handle images: ![ ... [inner](...) ... ](...)
    image_pattern = re.compile(r'!\[([^\[\]]*)\[([^\]]+)\]\([^)]*术语速查手册\.md[^)]*\)([^\[\]]*)\]\(([^)]+)\)')
    
    def image_replacer(match):
        prefix = match.group(1)
        inner_text = match.group(2)
        suffix = match.group(3)
        outer_url = match.group(4)
        print(f"Fixing nested image alt in {file_path}: ![{prefix}{inner_text}{suffix}]({outer_url})")
        return f'![{prefix}{inner_text}{suffix}]({outer_url})'

    new_content = pattern.sub(replacer, new_content)
    new_content = image_pattern.sub(image_replacer, new_content)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

root_dir = "/Users/bigzhu/Sync/Projects/Wyckoff/docs"
count = 0

for root, dirs, files in os.walk(root_dir):
    if ".vuepress" in dirs:
        dirs.remove(".vuepress")
        
    for file in files:
        if file.endswith(".md"):
            full_path = os.path.join(root, file)
            if fix_nested_links(full_path):
                count += 1

print(f"Processed {count} files.")
