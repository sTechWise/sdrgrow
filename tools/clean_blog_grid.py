import re
import os

blog_html_path = r'c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog.html'

with open(blog_html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Category to image map
img_map = {
    "Lead Generation": "assets/blog-leads.png",
    "LinkedIn": "assets/blog-linkedin.png",
    "Email": "assets/blog-deliverability.png",
    "Strategy": "assets/blog-outreach.png",
    "Comparison": "assets/blog-deliverability.png",
    "Data & Research": "assets/blog-benchmarks.png",
    "Case Study": "assets/blog-benchmarks.png",
    "Pricing": "assets/blog-benchmarks.png",
    "Niche": "assets/blog-outreach.png",
    "Copywriting": "assets/blog-brandvoice.png",
    "Intelligence": "assets/blog-benchmarks.png"
}

# Image overrides for specific slugs if needed
slug_img_override = {
    "sdr-grow-vs-clay": "assets/blog-leads.png",
    "sdr-grow-vs-hiring-an-sdr": "assets/blog-benchmarks.png",
    "best-outbound-systems-recruitment-agencies": "assets/blog-outreach.png",
    "sdr-grow-vs-smartlead": "assets/blog-deliverability.png",
    "sdr-grow-vs-instantly": "assets/blog-deliverability.png",
    "lead-engine": "assets/blog-leads.png"
}

# Extract all cards
card_pattern = r'<div class="blog-card fade-in">\s*<a href="/blog/([a-z0-9-]+)"[^>]*>.*?</a>\s*<div class="blog-card-body">\s*<span class="featured-tag">([^<]+)</span>\s*4>.*?</h4>\s*<p>(.*?)</p>\s*<div class="blog-meta">(.*?)</div>\s*<a href="/blog/[a-z0-9-]+" class="read-more"[^>]*>(.*?)</a>\s*</div>\s*</div>'

# We can also extract cards via regex on h4 titles
raw_cards = re.findall(r'(<div class="blog-card fade-in">.*?</div>\s*</div>)', html, re.DOTALL)

seen_slugs = set()
clean_cards = []

for card_code in raw_cards:
    slug_match = re.search(r'href="/blog/([a-z0-9-]+)"', card_code)
    if not slug_match:
        continue
    slug = slug_match.group(1)
    if slug in seen_slugs:
        continue
    seen_slugs.add(slug)

    # Extract tag
    tag_match = re.search(r'<span class="featured-tag">([^<]+)</span>', card_code)
    tag = tag_match.group(1).strip() if tag_match else 'Strategy'

    # Extract title
    title_match = re.search(r'<h4><a [^>]*>([^<]+)</a></h4>', card_code)
    title = title_match.group(1).strip() if title_match else slug.replace('-', ' ').title()

    # Extract description
    p_match = re.search(r'<p>(.*?)</p>', card_code, re.DOTALL)
    desc = p_match.group(1).strip() if p_match else ''

    # Extract meta
    meta_match = re.search(r'<div class="blog-meta">(.*?)</div>', card_code)
    meta = meta_match.group(1).strip() if meta_match else 'July 2026 · 6 min read'

    # Select image
    img = slug_img_override.get(slug, img_map.get(tag, "assets/blog-outreach.png"))

    card_html = f"""          <div class="blog-card fade-in">
            <a href="/blog/{slug}" class="blog-card-img" style="background: none; overflow: hidden; display: block;">
              <img src="{img}" alt="{title}" style="width: 100%; height: 100%; object-fit: cover;" loading="lazy">
            </a>
            <div class="blog-card-body">
              <span class="featured-tag">{tag}</span>
              <h4><a href="/blog/{slug}" style="color: inherit; text-decoration: none;">{title}</a></h4>
              <p>{desc}</p>
              <div class="blog-meta">{meta}</div>
              <a href="/blog/{slug}" class="read-more" style="margin-top: 12px;">Read Article →</a>
            </div>
          </div>"""
    clean_cards.append(card_html)

print(f"Total unique cards formatted: {len(clean_cards)}")

# Reconstruct blog.html
grid_start_idx = html.find('<div class="blog-grid stagger-children">')
newsletter_idx = html.find('<!-- NEWSLETTER -->')

if grid_start_idx != -1 and newsletter_idx != -1:
    before_grid = html[:grid_start_idx + len('<div class="blog-grid stagger-children">')]
    after_grid = html[newsletter_idx:]
    
    grid_content = "\n" + "\n".join(clean_cards) + "\n        </div>\n      </div>\n    </section>\n\n\n    "
    new_html = before_grid + grid_content + after_grid

    with open(blog_html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Successfully rebuilt blog.html grid!")
else:
    print("Error locating blog grid indexes in blog.html")
