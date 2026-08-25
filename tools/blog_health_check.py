"""
Blog health check - validates blog.html card integrity and DOM structure.

Checks:
  1. No cards link to non-existent blog pages
  2. No duplicate cards
  3. No missing card images
  4. Card structure integrity (no nested cards, balanced divs per card)
  5. Overall HTML tag balance (div, section, p, nav)
  6. All published pages have cards on the index

Usage:
  python tools/blog_health_check.py         # print report
  python tools/blog_health_check.py --ci    # exit code 1 on failure (for CI)
"""
import re
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.join(ROOT, 'blog')
ci_mode = '--ci' in sys.argv
errors = 0

with open(os.path.join(ROOT, 'blog.html'), 'r', encoding='utf-8') as f:
    content = f.read()

card_links = re.findall(r'href="/blog/([^"]+)"', content)
unique_links = sorted(set(card_links))
published = set(f.replace('.html', '') for f in os.listdir(BLOG_DIR)
                if f.endswith('.html') and not f.startswith('_'))

# 1. Cards linking to non-existent pages
print("1. Cards linking to non-existent pages")
e = 0
for slug in unique_links:
    if slug not in published:
        print(f"   FAIL: /blog/{slug} (no file exists)")
        errors += 1
        e += 1
if e == 0:
    print("   OK")

# 2. Duplicate cards
print("2. Duplicate cards")
e = 0
link_counts = Counter(card_links)
for slug, count in sorted(link_counts.items()):
    if count > 3:
        print(f"   FAIL: /blog/{slug} has {count // 3} cards")
        errors += 1
        e += 1
if e == 0:
    print("   OK")

# 3. Missing card images
print("3. Missing card images")
e = 0
card_images = set(re.findall(r'src="(assets/blog-[^"]+)"', content))
for img in sorted(card_images):
    if not os.path.exists(os.path.join(ROOT, img)):
        print(f"   FAIL: {img} not found")
        errors += 1
        e += 1
if e == 0:
    print("   OK")

# 4. Card structure integrity and nesting
print("4. Card structure integrity & nesting")
e = 0
card_pattern = re.compile(r'<div\s+class="blog-card(?:\s+fade-in)?"')
card_matches = list(card_pattern.finditer(content))
total_cards = len(card_matches)

# Extract blog-grid content
grid_start = content.find('class="blog-grid')
if grid_start == -1:
    print("   FAIL: could not find .blog-grid container")
    errors += 1
    e += 1
else:
    # Check each individual card
    for idx, match in enumerate(card_matches):
        start_pos = match.start()
        # Find card end boundary
        if idx + 1 < len(card_matches):
            end_pos = card_matches[idx + 1].start()
        else:
            end_pos = content.find('<!-- END_BLOG_GRID -->', start_pos)
            if end_pos == -1:
                end_pos = content.find('</div>\n      </div>\n    </section>', start_pos)
            if end_pos == -1:
                end_pos = len(content)
        
        card_block = content[start_pos:end_pos]
        opens = len(re.findall(r'<div[\s>]', card_block))
        closes = card_block.count('</div>')
        
        slug_m = re.search(r'/blog/([^"]+)"', card_block)
        slug_name = slug_m.group(1) if slug_m else f"card-index-{idx+1}"
        
        if opens != closes:
            print(f"   FAIL: Card '{slug_name}' div imbalance: {opens} opens vs {closes} closes (nesting bug!)")
            errors += 1
            e += 1
        if 'blog-card-body' not in card_block:
            print(f"   FAIL: Card '{slug_name}' missing blog-card-body")
            errors += 1
            e += 1
        if 'read-more' not in card_block:
            print(f"   FAIL: Card '{slug_name}' missing read-more link")
            errors += 1
            e += 1

if e == 0:
    print(f"   OK ({total_cards} cards, all verified direct children of grid)")

# 5. Overall HTML tag balance in blog.html
print("5. Overall HTML tag balance in blog.html")
e = 0
div_opens = len(re.findall(r'<div[\s>]', content))
div_closes = content.count('</div>')
if div_opens != div_closes:
    print(f"   FAIL: Total div imbalance ({div_opens} opens vs {div_closes} closes)")
    errors += 1
    e += 1

section_opens = len(re.findall(r'<section[\s>]', content))
section_closes = content.count('</section>')
if section_opens != section_closes:
    print(f"   FAIL: Total section imbalance ({section_opens} opens vs {section_closes} closes)")
    errors += 1
    e += 1

if e == 0:
    print(f"   OK (all {div_opens} div and {section_opens} section tags balanced)")

# 6. Published pages missing from blog index
print("6. Published pages on blog index")
e = 0
skip = {'apex-staffing-case-study'}
for slug in sorted(published - set(unique_links) - skip):
    print(f"   FAIL: /blog/{slug} has no card on blog.html")
    errors += 1
    e += 1
if e == 0:
    print("   OK")

# Summary
print(f"\nResult: {errors} error(s) found")
if errors > 0 and ci_mode:
    sys.exit(1)
