import os
import re
import json

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{META_TITLE}</title>
  <meta name="description" content="{META_DESC}">
  <link rel="canonical" href="https://sdrgrow.com/blog/{SLUG}">
  <meta name="robots" content="index, follow">

  <meta property="og:type" content="article">
  <meta property="og:url" content="https://sdrgrow.com/blog/{SLUG}">
  <meta property="og:title" content="{TITLE_TAG}">
  <meta property="og:description" content="{META_DESC}">
  <meta property="og:image" content="https://sdrgrow.com/assets/og-image.png">
  <meta property="og:site_name" content="SDR GROW">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{TITLE_TAG}">
  <meta name="twitter:description" content="{META_DESC}">
  <meta name="twitter:image" content="https://sdrgrow.com/assets/og-image.png">

  <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
  <link rel="apple-touch-icon" href="/assets/logo.png">
  <meta name="theme-color" content="#20A7C7">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&family=Open+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/style.min.css">

  <script async src="https://www.googletagmanager.com/gtag/js?id=G-77X4J912VN"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-77X4J912VN');
  </script>

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://sdrgrow.com/"}},
      {{"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://sdrgrow.com/blog"}},
      {{"@type": "ListItem", "position": 3, "name": "{TITLE_TAG}", "item": "https://sdrgrow.com/blog/{SLUG}"}}
    ]
  }}
  </script>

  <style>
    .article-hero {{ padding: 100px 0 60px; background: var(--bg-light); border-bottom: 1px solid var(--border); }}
    .article-hero .featured-tag {{ margin-bottom: 16px; }}
    .article-hero h1 {{ font-family: var(--font-display); font-size: clamp(2rem, 4vw, 2.8rem); font-weight: 700; color: var(--text-primary); letter-spacing: -0.02em; margin-bottom: 16px; max-width: 720px; }}
    .article-hero .blog-meta {{ font-family: var(--font-body); font-size: 0.85rem; color: var(--text-muted); }}
    .article-body {{ padding: 60px 0 80px; background: var(--bg-white); }}
    .article-content {{ max-width: 720px; margin: 0 auto; }}
    .article-content h2 {{ font-family: var(--font-heading); font-size: 1.4rem; font-weight: 600; color: var(--text-primary); margin: 40px 0 16px; }}
    .article-content h3 {{ font-family: var(--font-heading); font-size: 1.15rem; font-weight: 600; color: var(--text-primary); margin: 30px 0 12px; }}
    .article-content p {{ font-family: var(--font-paragraph); font-size: 1rem; color: var(--text-secondary); line-height: 1.85; margin-bottom: 18px; }}
    .article-content ul, .article-content ol {{ padding-left: 24px; margin-bottom: 18px; }}
    .article-content li {{ font-family: var(--font-paragraph); font-size: 0.95rem; color: var(--text-secondary); line-height: 1.8; margin-bottom: 8px; }}
    .article-content strong {{ color: var(--text-primary); }}
    .article-content blockquote {{ border-left: 3px solid var(--accent); padding: 16px 24px; margin: 24px 0; background: var(--accent-light); border-radius: 0 var(--radius) var(--radius) 0; }}
    .article-content blockquote p {{ margin: 0; font-style: italic; color: var(--text-primary); }}
    .article-content table {{ width: 100%; border-collapse: collapse; margin: 24px 0; font-family: var(--font-paragraph); font-size: 0.92rem; }}
    .article-content th {{ text-align: left; padding: 12px; border-bottom: 2px solid var(--border); color: var(--text-primary); font-weight: 600; }}
    .article-content td {{ padding: 12px; border-bottom: 1px solid var(--border); color: var(--text-secondary); }}
    .article-content tr:hover {{ background: var(--bg-light); }}
    .article-cta {{ text-align: center; padding: 40px; background: var(--bg-light); border: 1px solid var(--border); border-radius: var(--radius-lg); margin: 40px 0; }}
    .article-cta p {{ margin-bottom: 20px; }}
    .article-back {{ display: inline-flex; align-items: center; gap: 8px; font-family: var(--font-body); font-size: 0.88rem; font-weight: 500; color: var(--accent); margin-bottom: 32px; transition: gap 0.2s ease; }}
    .article-back:hover {{ gap: 12px; }}
  </style>
</head>
<body>
  <a href="#main-content" class="skip-nav">Skip to main content</a>
  <header role="banner">
    <nav class="navbar" id="navbar" aria-label="Main navigation">
      <div class="container">
        <a href="/" class="nav-logo" aria-label="SDR GROW Home"><img src="/assets/logo.webp" alt="SDR GROW Logo" class="brand-logo"> SDR<span>GROW</span></a>
        <div class="nav-links" id="navLinks">
          <a href="/">Home</a>
          <a href="/about">About</a>
          <a href="/blog" class="nav-active">Blog</a>
          <a href="/book" class="nav-cta">Book a Call</a>
        </div>
        <button class="nav-toggle" id="navToggle" aria-label="Toggle navigation menu" aria-expanded="false">
          <span></span><span></span><span></span>
        </button>
      </div>
    </nav>
  </header>

  <main id="main-content">
    <section class="article-hero">
      <div class="container">
        <span class="featured-tag">{TAG}</span>
        <h1>{H1_TITLE}</h1>
        <div class="blog-meta">By <a href="https://linkedin.com/company/sdrgrow" target="_blank" rel="noopener" style="color: inherit; text-decoration: underline;">Abir, Founder of SDR GROW</a> · July 2026 · 6 min read</div>
      </div>
    </section>

    <section class="article-body">
      <div class="container">
        <div class="article-content">
          <a href="/blog" class="article-back">← Back to Blog</a>

          {BODY_HTML}

          <div class="article-cta">
            <p><strong>Ready to build predictable pipeline for your agency?</strong></p>
            <a href="/book" class="btn-primary">Book a Strategy Call →</a>
          </div>
        </div>
      </div>
    </section>
  </main>

  <div class="trust-block">
    <div class="container">
      <div class="trust-inner">
        <div class="trust-author">
          <div class="trust-avatar">AH</div>
          <div class="trust-info">
            <strong><a href="https://linkedin.com/company/sdrgrow" target="_blank" rel="noopener" style="color: inherit; text-decoration: none;">Abir, Founder of SDR GROW</a></strong>
            <p>Founder of SDR GROW. Builds outbound systems for recruitment and staffing agencies.</p>
          </div>
        </div>
        <div class="trust-dates">
          <span>Published: July 2026</span>
        </div>
      </div>
    </div>
  </div>

  <footer class="footer" role="contentinfo">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand-col">
          <div class="footer-brand"><img src="/assets/logo.webp" alt="SDR GROW Logo" class="brand-logo"> SDR<span>GROW</span></div>
          <p class="footer-desc">The outbound operating system built for recruitment agencies.</p>
          <p class="footer-address"><svg viewBox="0 0 24 24"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>San Jose, CA</p>
        </div>
        <div class="footer-col"><h4>Product</h4><ul><li><a href="/#modules">Feature Modules</a></li><li><a href="/#process">16-Touch Engine</a></li><li><a href="/#value">Pricing</a></li></ul></div>
        <div class="footer-col"><h4>Company</h4><ul><li><a href="/about">About Us</a></li><li><a href="/blog">Blog</a></li><li><a href="mailto:contact@sdrgrow.com">Contact</a></li></ul></div>
        <div class="footer-col"><h4>Legal</h4><ul><li><a href="/privacy">Privacy Policy</a></li><li><a href="/terms">Terms of Service</a></li></ul></div>
      </div>
      <div class="footer-bottom">
        <p class="footer-copy">&copy; 2026 SDR GROW. All rights reserved.</p>
      </div>
    </div>
  </footer>
  <script src="/js/script.min.js" defer></script>
</body>
</html>"""

files = [
    (r"C:\Users\rubaya\Downloads\SDR GROW\files (37)\support1-recruitment-business-development.html", "Strategy", "blog-outreach.png"),
    (r"C:\Users\rubaya\Downloads\SDR GROW\files (37)\support2-how-to-build-a-recruitment-pipeline.html", "Strategy", "blog-benchmarks.png"),
    (r"C:\Users\rubaya\Downloads\SDR GROW\files (38)\support3-recruitment-leads.html", "Lead Generation", "blog-leads.png"),
    (r"C:\Users\rubaya\Downloads\SDR GROW\files (38)\support4-how-to-find-clients-for-a-staffing-agency.html", "Lead Generation", "blog-linkedin.png")
]

cards_to_add = []

for src_path, tag, img_file in files:
    with open(src_path, 'r', encoding='utf-8') as f:
        raw_html = f.read()

    # Extract metadata from comment block
    slug_match = re.search(r'PUBLISH AT:\s*/blog/([a-z0-9-]+)', raw_html)
    title_match = re.search(r'TITLE TAG:\s*(.+)', raw_html)
    
    slug = slug_match.group(1) if slug_match else os.path.splitext(os.path.basename(src_path))[0]
    title_tag = title_match.group(1).strip() if title_match else slug.replace('-', ' ').title()
    meta_title = f"{title_tag} — SDR GROW"

    # Extract article content
    art_match = re.search(r'<article>(.*?)</article>', raw_html, re.DOTALL)
    art_content = art_match.group(1).strip() if art_match else raw_html

    # Extract H1 title
    h1_match = re.search(r'<h1>(.*?)</h1>', art_content)
    h1_title = h1_match.group(1) if h1_match else title_tag
    # Remove H1 from body content as it is placed in hero
    body_content = re.sub(r'<h1>.*?</h1>', '', art_content, count=1).strip()

    # Extract first paragraph text for meta description
    first_p = re.search(r'<p>(.*?)</p>', body_content, re.DOTALL)
    meta_desc = re.sub(r'<[^>]+>', '', first_p.group(1)).strip() if first_p else title_tag
    if len(meta_desc) > 155:
        meta_desc = meta_desc[:152] + "..."

    # Build page HTML
    page_html = TEMPLATE.format(
        META_TITLE=meta_title,
        TITLE_TAG=title_tag,
        META_DESC=meta_desc,
        SLUG=slug,
        TAG=tag,
        H1_TITLE=h1_title,
        BODY_HTML=body_content
    )

    out_file = os.path.join(r"c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog", f"{slug}.html")
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(page_html)
    print(f"Created: {out_file}")

    # Prepare card for blog.html
    desc_short = meta_desc[:120] + "..." if len(meta_desc) > 120 else meta_desc
    cards_to_add.append({
        "slug": slug,
        "title": title_tag,
        "desc": desc_short,
        "tag": tag,
        "img": img_file
    })

# Add cards to blog.html
blog_html_path = r"c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog.html"
with open(blog_html_path, 'r', encoding='utf-8') as f:
    blog_page = f.read()

card_blocks = []
for card in cards_to_add:
    if card["slug"] not in blog_page:
        card_html = f"""          <div class="blog-card fade-in">
            <a href="/blog/{card['slug']}" class="blog-card-img" style="background: none; overflow: hidden; display: block;">
              <img src="assets/{card['img']}" alt="{card['title']}" style="width: 100%; height: 100%; object-fit: cover;" loading="lazy">
            </a>
            <div class="blog-card-body">
              <span class="featured-tag">{card['tag']}</span>
              <h4><a href="/blog/{card['slug']}" style="color: inherit; text-decoration: none;">{card['title']}</a></h4>
              <p>{card['desc']}</p>
              <div class="blog-meta">July 2026 · 6 min read</div>
              <a href="/blog/{card['slug']}" class="read-more" style="margin-top: 12px;">Read Article →</a>
            </div>
          </div>"""
        card_blocks.append(card_html)

if card_blocks:
    insertion_str = "\n".join(card_blocks) + "\n        </div>\n      </div>\n    </section>"
    blog_page = re.sub(r'</div>\s*</div>\s*</section>\s*(?=<!-- NEWSLETTER -->|\n\s*<!-- NEWSLETTER -->)', insertion_str, blog_page)
    with open(blog_html_path, 'w', encoding='utf-8') as f:
        f.write(blog_page)
    print("Added cards to blog.html")
