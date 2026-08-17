"""
Delete a blog post completely — removes the file, its card from blog.html,
its sitemap entry, its llms.txt entry, and adds a 301 redirect in vercel.json.

Usage:
  python tools/delete-blog.py <slug> [--redirect-to <target-slug>]

Example:
  python tools/delete-blog.py email-deliverability --redirect-to cold-email-deliverability
"""
import sys
import os
import re
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.join(ROOT, 'blog')


def remove_card_from_blog_html(slug):
    path = os.path.join(ROOT, 'blog.html')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match the entire blog-card div that links to this slug
    pattern = re.compile(
        r'\s*<div class="blog-card fade-in">\s*'
        r'<a href="/blog/' + re.escape(slug) + r'".*?</div>\s*</div>\s*</div>',
        re.DOTALL
    )
    new_content, count = pattern.subn('', content)
    if count > 0:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  blog.html: removed {count} card(s)")
    else:
        print(f"  blog.html: no card found for /blog/{slug}")


def remove_from_sitemap(slug):
    path = os.path.join(ROOT, 'sitemap.xml')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = re.compile(
        r'\s*<url>\s*<loc>https://sdrgrow\.com/blog/' + re.escape(slug) + r'</loc>.*?</url>',
        re.DOTALL
    )
    new_content, count = pattern.subn('', content)
    if count > 0:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  sitemap.xml: removed entry")
    else:
        print(f"  sitemap.xml: no entry found")


def remove_from_llms_txt(slug):
    path = os.path.join(ROOT, 'llms.txt')
    if not os.path.exists(path):
        print(f"  llms.txt: file not found")
        return
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = [l for l in lines if f'/blog/{slug}' not in l]
    if len(new_lines) < len(lines):
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"  llms.txt: removed entry")
    else:
        print(f"  llms.txt: no entry found")


def add_redirect(slug, target_slug):
    path = os.path.join(ROOT, 'vercel.json')
    with open(path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    redirect = {
        "source": f"/blog/{slug}",
        "destination": f"/blog/{target_slug}",
        "permanent": True
    }

    # Check if redirect already exists
    for r in config.get('redirects', []):
        if r.get('source') == redirect['source']:
            print(f"  vercel.json: redirect already exists")
            return

    # Add before the .html catch-all redirect
    redirects = config.get('redirects', [])
    insert_idx = len(redirects) - 1  # before last (.html -> $1)
    redirects.insert(insert_idx, redirect)
    config['redirects'] = redirects

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
        f.write('\n')
    print(f"  vercel.json: added 301 /blog/{slug} -> /blog/{target_slug}")


def delete_file(slug):
    path = os.path.join(BLOG_DIR, f'{slug}.html')
    if os.path.exists(path):
        os.remove(path)
        print(f"  blog/{slug}.html: deleted")
    else:
        print(f"  blog/{slug}.html: file not found (already deleted?)")


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/delete-blog.py <slug> [--redirect-to <target-slug>]")
        print("Example: python tools/delete-blog.py email-deliverability --redirect-to cold-email-deliverability")
        sys.exit(1)

    slug = sys.argv[1]
    target_slug = None

    if '--redirect-to' in sys.argv:
        idx = sys.argv.index('--redirect-to')
        if idx + 1 < len(sys.argv):
            target_slug = sys.argv[idx + 1]

    print(f"\nDeleting blog post: /blog/{slug}")
    print("-" * 40)

    delete_file(slug)
    remove_card_from_blog_html(slug)
    remove_from_sitemap(slug)
    remove_from_llms_txt(slug)

    if target_slug:
        add_redirect(slug, target_slug)
    else:
        print(f"  vercel.json: no redirect added (use --redirect-to <slug> to add one)")

    print("-" * 40)
    print("Done. Run 'python tools/blog_health_check.py' to verify.")
    print()


if __name__ == '__main__':
    main()
