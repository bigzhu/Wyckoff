import os
import re

def strip_markdown_links_in_mermaid(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    mermaid_block_pattern = re.compile(r'```mermaid\n(.*?)```', re.DOTALL)
    
    new_content = content
    modified = False
    
    def replace_mermaid_content(match):
        nonlocal modified
        block_content = match.group(1)
        original_block_content = block_content
        
        # Regex to find markdown links: [text](url)
        # We replace it with just 'text'
        link_pattern = re.compile(r'\[([^\]]+)\]\([^\)]+\)')
        
        # We also need to handle cases where quotes might be missing around the whole label if it contains brackets
        # But first let's just strip the links inside the mermaid block
        new_block_content = link_pattern.sub(r'\1', block_content)
        
        # Also clean up any lingering internal path refs if they are just in text like "../foo.md" (unlikely but possible)
        
        if new_block_content != original_block_content:
            modified = True
            return f'```mermaid\n{new_block_content}```'
        return match.group(0)

    new_content = mermaid_block_pattern.sub(replace_mermaid_content, content)
    
    if modified:
        print(f"Removed nested links in Mermaid: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

root_dir = "/Users/bigzhu/Sync/Projects/Wyckoff/docs"
count = 0

for root, dirs, files in os.walk(root_dir):
    if ".vuepress" in dirs:
        dirs.remove(".vuepress")
    if "wyckoff_content" in dirs:
        dirs.remove("wyckoff_content")
        
    for file in files:
        if file.endswith(".md"):
            full_path = os.path.join(root, file)
            if strip_markdown_links_in_mermaid(full_path):
                count += 1

print(f"Processed {count} files.")
