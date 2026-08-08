import re

blog_html_path = r'c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog.html'

with open(blog_html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Image mappings for categories/slugs
image_map = {
    "best-outbound-systems-recruitment-agencies": "assets/blog-outreach.png",
    "sdr-grow-vs-clay": "assets/blog-leads.png",
    "sdr-grow-vs-hiring-an-sdr": "assets/blog-benchmarks.png",
    "sdr-grow-vs-instantly": "assets/blog-deliverability.png",
    "sdr-grow-vs-smartlead": "assets/blog-deliverability.png",
    "sdr-grow-vs-apollo": "assets/blog-leads.png",
    "sdr-grow-vs-lemlist": "assets/blog-linkedin.png",
    "sdr-grow-vs-diy-stack": "assets/blog-benchmarks.png",
    "sdr-grow-vs-lead-gen-agency": "assets/blog-outreach.png"
}

# Regex replacement function for cards missing img tags
def replace_card_img(match):
    slug = match.group(1)
    tag = match.group(2)
    img = image_map.get(slug, "assets/blog-outreach.png")
    return f'<a href="/blog/{slug}" class="blog-card-img" style="background: none; overflow: hidden; display: block;">\n              <img src="{img}" alt="{tag}" style="width: 100%; height: 100%; object-fit: cover;" loading="lazy">\n            </a>'

# Replace any comparison style cards with real image cards
pattern = r'<a href="/blog/([a-z0-9-]+)" class="blog-card-img"[^>]*>([^<]+)</a>'
updated_content = re.sub(pattern, replace_card_img, content)

with open(blog_html_path, 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("Updated blog.html cards with cover images.")
