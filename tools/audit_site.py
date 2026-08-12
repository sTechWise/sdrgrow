import json
import re
import os
import glob

blog_dir = r'c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog'
root_dir = r'c:\Users\rubaya\Desktop\sTechWise\SDR GROW'

# All HTML files to check
root_pages = ['index.html', 'about.html', 'blog.html', 'book.html', 'privacy.html', 'terms.html']
blog_files = [f for f in os.listdir(blog_dir) if f.endswith('.html') and not f.startswith('_')]

print("=" * 70)
print("PART 1: JSON-LD VALIDATION")
print("=" * 70)

json_ld_results = []

for f in blog_files:
    filepath = os.path.join(blog_dir, f)
    with open(filepath, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    # Find all JSON-LD blocks
    blocks = re.findall(r'<script\s+type="application/ld\+json">\s*(.*?)\s*</script>', content, re.DOTALL)
    
    if not blocks:
        json_ld_results.append((f, "NO JSON-LD FOUND", ""))
        continue
    
    all_valid = True
    errors = []
    for i, block in enumerate(blocks):
        try:
            json.loads(block)
        except json.JSONDecodeError as e:
            all_valid = False
            errors.append(f"Block {i+1}: {str(e)}")
    
    if all_valid:
        json_ld_results.append((f, "VALID", f"{len(blocks)} block(s)"))
    else:
        json_ld_results.append((f, "BROKEN", "; ".join(errors)))

print(f"{'File':<60} {'Status':<10} {'Details'}")
print("-" * 120)
for name, status, details in json_ld_results:
    print(f"{name:<60} {status:<10} {details}")

print("\n" + "=" * 70)
print("PART 2: CANONICAL TAG AUDIT")
print("=" * 70)

canonical_results = []

# Check root pages
for f in root_pages:
    filepath = os.path.join(root_dir, f)
    if not os.path.exists(filepath):
        canonical_results.append((f, "FILE NOT FOUND", "", ""))
        continue
    with open(filepath, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    canon_match = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', content)
    if canon_match:
        canon_url = canon_match.group(1)
        # Determine expected URL
        if f == 'index.html':
            expected = 'https://sdrgrow.com/'
        else:
            expected = f'https://sdrgrow.com/{f.replace(".html", "")}'
        
        issues = []
        if 'www.' in canon_url:
            issues.append("USES WWW")
        if canon_url != expected and canon_url != expected.rstrip('/'):
            issues.append(f"EXPECTED: {expected}")
        
        canonical_results.append((f, "YES", canon_url, "; ".join(issues) if issues else "OK"))
    else:
        canonical_results.append((f, "NO", "", "MISSING CANONICAL TAG"))

# Check blog pages
for f in blog_files:
    filepath = os.path.join(blog_dir, f)
    with open(filepath, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    slug = f.replace('.html', '')
    expected = f'https://sdrgrow.com/blog/{slug}'
    
    canon_match = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', content)
    if canon_match:
        canon_url = canon_match.group(1)
        issues = []
        if 'www.' in canon_url:
            issues.append("USES WWW")
        if canon_url != expected and canon_url != expected + '/':
            issues.append(f"MISMATCH: got {canon_url}, expected {expected}")
        if canon_url.endswith('/') and expected and not expected.endswith('/'):
            issues.append("HAS TRAILING SLASH")
        
        canonical_results.append((f"blog/{f}", "YES", canon_url, "; ".join(issues) if issues else "OK"))
    else:
        canonical_results.append((f"blog/{f}", "NO", "", "MISSING CANONICAL TAG"))

print(f"{'File':<60} {'Has Canon':<10} {'URL':<55} {'Issue'}")
print("-" * 160)
for name, has, url, issue in canonical_results:
    print(f"{name:<60} {has:<10} {url:<55} {issue}")

print("\n" + "=" * 70)
print("PART 3: VERCEL.JSON / REDIRECT CHECK")
print("=" * 70)

vercel_path = os.path.join(root_dir, 'vercel.json')
if os.path.exists(vercel_path):
    with open(vercel_path, 'r', encoding='utf-8') as fh:
        print("vercel.json EXISTS:")
        print(fh.read())
else:
    print("vercel.json DOES NOT EXIST")

redirects_path = os.path.join(root_dir, '_redirects')
if os.path.exists(redirects_path):
    with open(redirects_path, 'r', encoding='utf-8') as fh:
        print("_redirects EXISTS:")
        print(fh.read())
else:
    print("_redirects DOES NOT EXIST")
