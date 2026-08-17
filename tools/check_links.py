import re
import os

# Extract all blog links from blog.html
with open('blog.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all unique blog links
links = set(re.findall(r'href="/blog/([^"]+)"', content))

# Find all published files
published = set(f.replace('.html', '') for f in os.listdir('blog') if f.endswith('.html'))

# Find links pointing to non-existent pages
missing = links - published
for m in sorted(missing):
    print(f'MISSING PAGE: /blog/{m}')

# Find published pages not linked
unlinked = published - links - {'apex-staffing-case-study'}
for u in sorted(unlinked):
    print(f'UNLINKED PAGE: /blog/{u}')
