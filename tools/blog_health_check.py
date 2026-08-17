"""
Blog health check - validates blog.html card integrity.

Checks:
  1. No cards link to non-existent blog pages
  2. No duplicate cards
  3. No missing card images
  4. All cards are inside the grid container
  5. All published pages have cards on the index

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
for slug in unique_links:
    if slug not in published:
        print(f"   FAIL: /blog/{slug} (no file exists)")
        errors += 1
if errors == 0:
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

# 4. Card structure integrity
print("4. Card structure integrity")
card_count = content.count('class="blog-card')
grid_match = re.search(
    r'<div class="blog-grid stagger-children">(.*?)</div>\s*</div>\s*</section>',
    content, re.DOTALL)
if grid_match:
    grid_card_count = grid_match.group(1).count('class="blog-card')
    if card_count != grid_card_count:
        print(f"   FAIL: {card_count - grid_card_count} cards outside grid")
        errors += 1
    else:
        print(f"   OK ({card_count} cards)")
else:
    print("   WARN: could not find grid container")

# 5. Published pages missing from blog index
print("5. Published pages on blog index")
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
