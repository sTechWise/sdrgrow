"""
Industry-grade site audit for sdrgrow.com
Checks: JSON-LD, canonical, internal links, sitemap, images, meta tags,
        schema, broken references, duplicate content, redirects, robots.txt
"""
import json
import re
import os
import sys
from collections import Counter

ROOT = r'c:\Users\rubaya\Desktop\sTechWise\SDR GROW'
BLOG_DIR = os.path.join(ROOT, 'blog')
DOMAIN = 'https://sdrgrow.com'

errors = []
warnings = []
passed = []

def err(category, msg):
    errors.append((category, msg))
    print(f"  FAIL: {msg}")

def warn(category, msg):
    warnings.append((category, msg))
    print(f"  WARN: {msg}")

def ok(msg):
    passed.append(msg)
    print(f"  OK: {msg}")

# Collect all HTML files
root_pages = {}
for f in os.listdir(ROOT):
    if f.endswith('.html') and os.path.isfile(os.path.join(ROOT, f)):
        with open(os.path.join(ROOT, f), 'r', encoding='utf-8') as fh:
            root_pages[f] = fh.read()

blog_pages = {}
for f in os.listdir(BLOG_DIR):
    if f.endswith('.html') and not f.startswith('_'):
        with open(os.path.join(BLOG_DIR, f), 'r', encoding='utf-8') as fh:
            blog_pages[f] = fh.read()

all_pages = {}
for f, c in root_pages.items():
    all_pages[f] = c
for f, c in blog_pages.items():
    all_pages[f'blog/{f}'] = c

# ================================================================
print("=" * 60)
print("1. JSON-LD STRUCTURED DATA VALIDATION")
print("=" * 60)
for filepath, content in all_pages.items():
    blocks = re.findall(r'<script\s+type="application/ld\+json">\s*(.*?)\s*</script>', content, re.DOTALL)
    if not blocks and 'blog/' in filepath:
        slug = filepath.replace('blog/', '').replace('.html', '')
        if slug != 'apex-staffing-case-study':
            warn("JSON-LD", f"{filepath}: no JSON-LD schema found")
        continue
    for i, block in enumerate(blocks):
        try:
            parsed = json.loads(block)
        except json.JSONDecodeError as e:
            err("JSON-LD", f"{filepath} block {i+1}: {e}")

if not any(c == "JSON-LD" for c, _ in errors):
    ok(f"All JSON-LD blocks valid across {len(all_pages)} pages")

# ================================================================
print("\n" + "=" * 60)
print("2. CANONICAL TAGS")
print("=" * 60)
skip_canonical = {'404.html'}
for filepath, content in all_pages.items():
    if filepath in skip_canonical:
        continue
    canon = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', content)
    if not canon:
        err("Canonical", f"{filepath}: missing canonical tag")
        continue
    url = canon.group(1)
    if 'www.' in url:
        err("Canonical", f"{filepath}: canonical uses www ({url})")
    if not url.startswith('https://'):
        err("Canonical", f"{filepath}: canonical not HTTPS ({url})")
    if url.endswith('/') and url != f'{DOMAIN}/':
        warn("Canonical", f"{filepath}: canonical has trailing slash ({url})")
    # Self-referencing check (skip redirect pages)
    slug = filepath.replace('.html', '')
    if slug == 'index':
        expected = f'{DOMAIN}/'
    elif slug.startswith('blog/'):
        expected = f'{DOMAIN}/{slug}'
    else:
        expected = f'{DOMAIN}/{slug}'
    # apex-staffing is a redirect, canonical should point to target
    if 'apex-staffing' in filepath:
        continue
    if url != expected:
        err("Canonical", f"{filepath}: canonical mismatch (got {url}, expected {expected})")

if not any(c == "Canonical" for c, _ in errors):
    ok("All pages have correct self-referencing HTTPS non-www canonical tags")

# ================================================================
print("\n" + "=" * 60)
print("3. META TAGS (title, description, OG)")
print("=" * 60)
for filepath, content in all_pages.items():
    title = re.search(r'<title>([^<]*)</title>', content)
    desc = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', content)
    og_title = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', content)
    og_desc = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', content)
    og_img = re.search(r'<meta\s+property="og:image"\s+content="([^"]*)"', content)

    if not title or not title.group(1).strip():
        err("Meta", f"{filepath}: missing or empty <title>")
    elif len(title.group(1)) > 70:
        warn("Meta", f"{filepath}: title too long ({len(title.group(1))} chars)")

    if not desc or not desc.group(1).strip():
        if 'apex-staffing' not in filepath:
            err("Meta", f"{filepath}: missing meta description")
    elif len(desc.group(1)) > 160:
        warn("Meta", f"{filepath}: meta description too long ({len(desc.group(1))} chars)")

    if not og_title:
        warn("Meta", f"{filepath}: missing og:title")
    if not og_desc:
        warn("Meta", f"{filepath}: missing og:description")
    if not og_img:
        warn("Meta", f"{filepath}: missing og:image")

if not any(c == "Meta" for c, _ in errors):
    ok("All pages have title, description, and OG tags")

# ================================================================
print("\n" + "=" * 60)
print("4. INTERNAL LINK INTEGRITY")
print("=" * 60)
# Collect all internal href links
published_slugs = set()
for f in root_pages:
    published_slugs.add('/' + f.replace('.html', ''))
published_slugs.add('/')  # index
for f in blog_pages:
    published_slugs.add('/blog/' + f.replace('.html', ''))

broken_links = []
for filepath, content in all_pages.items():
    # Find all href="/..." links (internal)
    links = re.findall(r'href="(/[^"#]*)"', content)
    for link in links:
        # Skip known external paths, assets, mailto
        if link.startswith('/assets/') or link.startswith('/css/') or link.startswith('/js/'):
            continue
        # Normalize
        clean = link.rstrip('/')
        if clean == '':
            clean = '/'
        # Check anchor links like /#modules
        if clean.startswith('/#'):
            continue
        if clean not in published_slugs:
            broken_links.append((filepath, link))

if broken_links:
    seen = set()
    for fp, link in broken_links:
        key = f"{fp}->{link}"
        if key not in seen:
            seen.add(key)
            err("Links", f"{fp}: broken internal link {link}")
else:
    ok("All internal links point to existing pages")

# ================================================================
print("\n" + "=" * 60)
print("5. SITEMAP CONSISTENCY")
print("=" * 60)
sitemap_path = os.path.join(ROOT, 'sitemap.xml')
with open(sitemap_path, 'r', encoding='utf-8') as f:
    sitemap = f.read()

sitemap_urls = re.findall(r'<loc>([^<]+)</loc>', sitemap)

# Check for conflict markers
if '<<<<' in sitemap or '>>>>' in sitemap or '=====' in sitemap:
    err("Sitemap", "sitemap.xml contains merge conflict markers!")

# Check all published pages are in sitemap
for filepath in all_pages:
    if 'apex-staffing' in filepath:
        continue
    slug = filepath.replace('.html', '')
    if slug == 'index':
        expected_url = f'{DOMAIN}/'
    else:
        expected_url = f'{DOMAIN}/{slug}'
    # Skip privacy/terms (noindex)
    if slug in ('privacy', 'terms'):
        continue
    if expected_url not in sitemap_urls:
        warn("Sitemap", f"{filepath}: not in sitemap ({expected_url})")

# Check no sitemap entry points to non-existent page
for url in sitemap_urls:
    path = url.replace(DOMAIN, '')
    if path == '/':
        continue
    slug = path.lstrip('/')
    html_file = slug + '.html'
    if not os.path.exists(os.path.join(ROOT, html_file)):
        err("Sitemap", f"sitemap entry {url} has no matching file ({html_file})")

if not any(c == "Sitemap" for c, _ in errors):
    ok(f"Sitemap has {len(sitemap_urls)} URLs, all consistent")

# ================================================================
print("\n" + "=" * 60)
print("6. IMAGE / ASSET REFERENCES")
print("=" * 60)
missing_assets = set()
for filepath, content in all_pages.items():
    # Find src="..." references
    srcs = re.findall(r'(?:src|href)="([^"]+)"', content)
    for src in srcs:
        # Skip external URLs, data URIs, anchors, JS
        if src.startswith('http') or src.startswith('data:') or src.startswith('#'):
            continue
        if src.startswith('mailto:') or src.startswith('javascript:'):
            continue
        # Resolve path
        if src.startswith('/'):
            full_path = os.path.join(ROOT, src.lstrip('/'))
        elif 'blog/' in filepath:
            full_path = os.path.join(BLOG_DIR, src)
            if not os.path.exists(full_path):
                full_path = os.path.join(ROOT, src)
        else:
            full_path = os.path.join(ROOT, src)
        if not os.path.exists(full_path):
            key = f"{filepath}: {src}"
            if key not in missing_assets:
                missing_assets.add(key)
                # Only error for images/css/js, not internal page links
                if any(src.endswith(ext) for ext in ['.png', '.jpg', '.webp', '.svg', '.ico', '.css', '.js', '.woff2']):
                    err("Assets", f"{filepath}: missing asset {src}")

if not any(c == "Assets" for c, _ in errors):
    ok("All image and asset references resolve to existing files")

# ================================================================
print("\n" + "=" * 60)
print("7. BLOG CARD GRID INTEGRITY")
print("=" * 60)
with open(os.path.join(ROOT, 'blog.html'), 'r', encoding='utf-8') as f:
    blog_index = f.read()

card_links = re.findall(r'href="/blog/([^"]+)"', blog_index)
unique_card_slugs = sorted(set(card_links))

# Cards linking to non-existent pages
for slug in unique_card_slugs:
    if slug + '.html' not in blog_pages:
        err("Cards", f"blog.html card links to /blog/{slug} but file doesn't exist")

# Duplicate cards
link_counts = Counter(card_links)
for slug, count in link_counts.items():
    if count > 3:
        err("Cards", f"blog.html has {count//3} duplicate cards for /blog/{slug}")

# Published pages missing cards
skip_slugs = {'apex-staffing-case-study'}
for f in blog_pages:
    slug = f.replace('.html', '')
    if slug not in skip_slugs and slug not in unique_card_slugs:
        warn("Cards", f"/blog/{slug} is published but has no card on blog.html")

# Card count
card_count = blog_index.count('class="blog-card')
ok(f"Blog grid has {card_count} cards, {len(unique_card_slugs)} unique posts")

# ================================================================
print("\n" + "=" * 60)
print("8. VERCEL.JSON CONFIGURATION")
print("=" * 60)
with open(os.path.join(ROOT, 'vercel.json'), 'r', encoding='utf-8') as f:
    try:
        vercel = json.load(f)
        ok("vercel.json is valid JSON")
    except json.JSONDecodeError as e:
        err("Vercel", f"vercel.json is invalid JSON: {e}")
        vercel = {}

if vercel.get('cleanUrls') != True:
    warn("Vercel", "cleanUrls is not true")
if vercel.get('trailingSlash') != False:
    warn("Vercel", "trailingSlash is not false")

# Check www redirect exists
has_www = False
for r in vercel.get('redirects', []):
    has_val = r.get('has', [])
    for h in has_val:
        if h.get('value') == 'www.sdrgrow.com':
            has_www = True
if has_www:
    ok("www -> non-www redirect exists")
else:
    err("Vercel", "Missing www -> non-www redirect")

# Check redirect targets exist
for r in vercel.get('redirects', []):
    dest = r.get('destination', '')
    if dest.startswith('/blog/'):
        slug = dest.replace('/blog/', '')
        if slug + '.html' not in blog_pages:
            err("Vercel", f"Redirect target {dest} has no matching file")

# ================================================================
print("\n" + "=" * 60)
print("9. ROBOTS.TXT")
print("=" * 60)
robots_path = os.path.join(ROOT, 'robots.txt')
if os.path.exists(robots_path):
    with open(robots_path, 'r', encoding='utf-8') as f:
        robots = f.read()
    if 'Sitemap:' in robots:
        ok("robots.txt exists with sitemap reference")
    else:
        warn("Robots", "robots.txt exists but has no Sitemap: directive")
    if 'Disallow: /' in robots and 'User-agent: *' in robots:
        err("Robots", "robots.txt blocks all crawlers!")
else:
    warn("Robots", "robots.txt does not exist")

# ================================================================
print("\n" + "=" * 60)
print("10. DUPLICATE CONTENT CHECK")
print("=" * 60)
# Check for blog pages with very similar titles
titles = {}
for filepath, content in all_pages.items():
    title_match = re.search(r'<title>([^<]*)</title>', content)
    if title_match:
        t = title_match.group(1).strip()
        if t in titles:
            err("Duplicates", f"{filepath} and {titles[t]} have identical title: '{t}'")
        titles[t] = filepath

if not any(c == "Duplicates" for c, _ in errors):
    ok("No duplicate page titles found")

# ================================================================
print("\n" + "=" * 60)
print("11. LLMS.TXT CONSISTENCY")
print("=" * 60)
llms_path = os.path.join(ROOT, 'llms.txt')
if os.path.exists(llms_path):
    with open(llms_path, 'r', encoding='utf-8') as f:
        llms = f.read()
    llms_urls = re.findall(r'https://sdrgrow\.com/blog/([^\s\)]+)', llms)
    for slug in llms_urls:
        if slug + '.html' not in blog_pages:
            err("llms.txt", f"llms.txt references /blog/{slug} but file doesn't exist")
    if not any(c == "llms.txt" for c, _ in errors):
        ok(f"llms.txt has {len(llms_urls)} blog references, all valid")
else:
    warn("llms.txt", "llms.txt does not exist")

# ================================================================
print("\n" + "=" * 60)
print("12. HEADING STRUCTURE (H1)")
print("=" * 60)
for filepath, content in all_pages.items():
    h1_count = len(re.findall(r'<h1[^>]*>', content))
    if h1_count == 0:
        warn("H1", f"{filepath}: no H1 tag")
    elif h1_count > 1:
        warn("H1", f"{filepath}: {h1_count} H1 tags (should be exactly 1)")

if not any(c == "H1" for c, _ in warnings):
    ok("All pages have exactly one H1")

# ================================================================
print("\n" + "=" * 60)
print("13. MERGE CONFLICT MARKERS CHECK")
print("=" * 60)
conflict_found = False
for filepath, content in all_pages.items():
    if '<<<<<<' in content or '>>>>>>>' in content or '=======' in content:
        # Only flag if it looks like actual conflict markers (at start of line)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('<<<<<<<') or stripped.startswith('>>>>>>>') or stripped == '=======':
                err("Conflicts", f"{filepath} line {i+1}: merge conflict marker found")
                conflict_found = True
                break

if not conflict_found:
    ok("No merge conflict markers in any file")

# ================================================================
# FINAL REPORT
# ================================================================
print("\n" + "=" * 60)
print("FINAL REPORT")
print("=" * 60)
print(f"  Pages audited:  {len(all_pages)}")
print(f"  Checks passed:  {len(passed)}")
print(f"  Warnings:       {len(warnings)}")
print(f"  Errors:         {len(errors)}")

if errors:
    print(f"\n  ERRORS ({len(errors)}):")
    for cat, msg in errors:
        print(f"    [{cat}] {msg}")

if warnings:
    print(f"\n  WARNINGS ({len(warnings)}):")
    for cat, msg in warnings:
        print(f"    [{cat}] {msg}")

if errors:
    print("\n  VERDICT: ISSUES FOUND - fix errors before deploying")
    if '--ci' in sys.argv:
        sys.exit(1)
else:
    print("\n  VERDICT: SITE IS CLEAN AND PRODUCTION READY")
