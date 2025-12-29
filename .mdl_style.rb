# .mdl_style.rb
# Markdown Lint Configuration

# 1. Enable all rules by default
all

# 2. Disable Line Length (MD013)
exclude_rule 'MD013'

# 3. Ordered List Prefixes (MD029)
# Allow '1. 2. 3.' style (ordered) which matches Prettier defaults
rule 'MD029', :style => :ordered

# 4. Allow Duplicate Headers (MD024)
rule 'MD024', :allow_different_nesting => true

# 5. List Indentation (MD005, MD007)
# Defer to Prettier for indentation; mdl conflicts with task lists and nested spacing
exclude_rule 'MD005'
exclude_rule 'MD007'

# 6. Unordered List Style (MD004)
rule 'MD004', :style => :dash

# 7. Inline HTML (MD033)
exclude_rule 'MD033'

# 8. Emphasis used as header (MD036)
exclude_rule 'MD036'

# 9. Code block language (MD040)
exclude_rule 'MD040'

# 10. Header levels (MD001)
# Allow jumping levels (e.g., # title then ### section) which is common in notes
exclude_rule 'MD001'
