import os
import re

def check_mermaid_syntax(start_dir):
    mermaid_block_pattern = re.compile(r'```mermaid(.*?)```', re.DOTALL)
    
    # Regex for Edge Labels: -->|Label| or -- Label -->
    # Capture the content inside pipes or between -- and -->
    edge_pipe_pattern = re.compile(r'(-->|-.->|==>)\s*\|(.*?)\|')
    edge_text_pattern = re.compile(r'--\s+(.*?)\s+-->')
    
    # Regex for Node Labels: id[Label] or id(Label) or id{Label}
    # We want to find cases where quotes are MISSING but special chars are present.
    # Group 1: ID, Group 2: Open, Group 3: Content, Group 4: Close
    node_pattern = re.compile(r'(\w+)\s*([\[\(\{])(.*?)([\]\}\)])')
    
    special_chars = ['(', ')', '[', ']', '<br>', '=', '，', '（', '）', '/']
    # Check for Chinese characters
    chinese_pattern = re.compile(r'[\u4e00-\u9fa5]')

    errors_found = False

    for root, dirs, files in os.walk(start_dir):
        if 'node_modules' in root or '.git' in root or '.vuepress' in root:
            continue
            
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all mermaid blocks
                for block_match in mermaid_block_pattern.finditer(content):
                    block_content = block_match.group(1)
                    start_line = content[:block_match.start()].count('\n') + 1
                    
                    lines = block_content.split('\n')
                    for i, line in enumerate(lines):
                        line_num = start_line + i
                        line = line.strip()
                        if not line or line.startswith('graph') or line.startswith('sequenceDiagram'):
                            continue
                        if line.startswith('%%') or line.startswith('classDef') or line.startswith('style'):
                            continue

                        # CHECK 1: Edge Labels inside Pipes |...|
                        for match in edge_pipe_pattern.finditer(line):
                            label = match.group(2)
                            if not (label.startswith('"') and label.endswith('"')):
                                # Check logic: If it has Chinese or special chars, it SHOULD be quoted
                                if chinese_pattern.search(label) or any(char in label for char in special_chars):
                                    print(f"❌ [Edge Label Unquoted] {file_path}:{line_num}")
                                    print(f"   Line: {line}")
                                    print(f"   Label: {label}")
                                    print("   Suggestion: Add quotes -> |\"" + label + "\"|")
                                    errors_found = True
                        
                        # CHECK 2: Node Labels id[...] or id(...)
                        # This is harder to parse perfectly with regex, but let's try strict check for parens
                        for match in node_pattern.finditer(line):
                            node_id = match.group(1)
                            opener = match.group(2)
                            label = match.group(3)
                            closer = match.group(4)
                            
                            # Skip if already quoted
                            if label.startswith('"') and label.endswith('"'):
                                continue
                            
                            # Logic: If opener is ( and label contains ), it BREAKS.
                            # Logic: If opener is [ and label contains ], it BREAKS.
                            if opener == '(' and ')' in label:
                                print(f"❌ [Node Syntax Vulnerable] {file_path}:{line_num}")
                                print(f"   Line: {line}")
                                print(f"   Issue: Unquoted ')' inside round brackets.")
                                print("   Suggestion: Add quotes -> (\"" + label + "\")")
                                errors_found = True
                            elif opener == '[' and ']' in label:
                                print(f"❌ [Node Syntax Vulnerable] {file_path}:{line_num}")
                                print(f"   Line: {line}")
                                print(f"   Issue: Unquoted ']' inside square brackets.")
                                print("   Suggestion: Add quotes -> [\"" + label + "\"]")
                                errors_found = True
                            
                            # Soft Check: Chinese or Special Chars should ideally be quoted for safety
                            elif chinese_pattern.search(label) or any(char in label for char in special_chars):
                                if '<br>' in label: # HTML breaks MUST be quoted usually or they cause issues in some renderers
                                    print(f"⚠️ [Node Label Unquoted HTML] {file_path}:{line_num}")
                                    print(f"   Line: {line}")
                                    print("   Suggestion: Add quotes -> [\"" + label + "\"]")
                                # This is Warning only, unless it's strictly broken
                                
    if not errors_found:
        print("✅ No obvious syntax errors found.")

if __name__ == "__main__":
    print("🔍 Scanning for Mermaid Syntax Errors...")
    check_mermaid_syntax("docs")
