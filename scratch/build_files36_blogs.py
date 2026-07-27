import os
import re

files_dir = r"C:\Users\rubaya\Downloads\SDR GROW\files (36)"
blog_dir = r"c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog"
blog_html_path = r"c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog.html"

# Mapping each file to category tag and featured image
page_meta = {
    "page1-done-for-you-outbound.html": {
        "tag": "Strategy",
        "img": "assets/blog-outreach.png"
    },
    "page2-client-acquisition-system.html": {
        "tag": "Strategy",
        "img": "assets/blog-leads.png"
    },
    "page3-alternative-to-hiring-sdr.html": {
        "tag": "Strategy",
        "img": "assets/blog-benchmarks.png"
    },
    "page4-how-agencies-get-clients.html": {
        "tag": "Lead Generation",
        "img": "assets/blog-linkedin.png"
    },
    "page5-sdr-grow-vs-smartlead.html": {
        "tag": "Comparison",
        "img": "assets/blog-deliverability.png"
    }
}

template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{META_TITLE}</title>
  <meta name="description" content="{DESCRIPTION}">
  <meta name="keywords" content="{KEYWORDS}">
  <link rel="canonical" href="https://sdrgrow.com/blog/{SLUG}">
  <meta name="robots" content="index, follow">

  <meta property="og:type" content="article">
  <meta property="og:url" content="https://sdrgrow.com/blog/{SLUG}">
  <meta property="og:title" content="{TITLE}">
  <meta property="og:description" content="{DESCRIPTION}">
  <meta property="og:image" content="https://sdrgrow.com/assets/og-image.png">
  <meta property="og:site_name" content="SDR GROW">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{TITLE}">
  <meta name="twitter:description" content="{DESCRIPTION}">
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
    function gtag(){dataLayer.push(arguments);}
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
      {{"@type": "ListItem", "position": 3, "name": "{SHORT_TITLE}", "item": "https://sdrgrow.com/blog/{SLUG}"}}
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
        <div class="blog-meta">By <a href="https://linkedin.com/company/sdrgrow" target="_blank" rel="noopener" style="color: inherit; text-decoration: underline;">Abir, Founder of SDR GROW</a> · July 2026 · {READ_TIME}</div>
      </div>
    </section>

    <div style="max-width:720px;margin:0 auto;padding:40px 20px 0;"><img src="/{FEATURED_IMG}" alt="{H1_TITLE}" style="width:100%;border-radius:12px;" loading="lazy"></div>

    <section class="article-body">
      <div class="container">
        <div class="article-content">
          <a href="/blog" class="article-back">← Back to Blog</a>

          {INNER_HTML}

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

new_cards = []

for filename in sorted(os.listdir(files_dir)):
    if not filename.endswith(".html"):
        continue
    filepath = os.path.join(files_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract PUBLISH AT and TITLE TAG
    publish_at_m = re.search(r"PUBLISH AT:\s*/blog/([^\s\n]+)", content)
    title_tag_m = re.search(r"TITLE TAG:\s*([^\r\n]+)", content)

    if not publish_at_m or not title_tag_m:
        print(f"Skipping {filename}: Missing comments")
        continue

    slug = publish_at_m.group(1).strip()
    title_tag = title_tag_m.group(1).strip()
    meta_title = f"{title_tag} — SDR GROW"

    # Extract article content
    article_m = re.search(r"<article[^>]*>([\s\S]*?)</article>", content, re.IGNORECASE)
    if article_m:
        article_body = article_m.group(1).strip()
    else:
        article_body = content.strip()

    # Extract H1
    h1_m = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", article_body, re.IGNORECASE)
    if h1_m:
        h1_title = h1_m.group(1).replace("<[^>]*>", "").strip()
        # Remove H1 from body since it will be in hero
        inner_html = re.sub(r"<h1[^>]*>[\s\S]*?</h1>", "", article_body, count=1, flags=re.IGNORECASE).strip()
    else:
        h1_title = title_tag.split(" (")[0]
        inner_html = article_body

    # Remove author line in inner_html if present (e.g. <p><em>By Abir...</em></p>)
    inner_html = re.sub(r"<p>\s*<em>By Abir[\s\S]*?</em>\s*</p>", "", inner_html, flags=re.IGNORECASE).strip()

    # Extract description from first <p>
    p_m = re.search(r"<p[^>]*>([\s\S]*?)</p>", inner_html, re.IGNORECASE)
    if p_m:
        desc_text = re.sub(r"<[^>]*>", "", p_m.group(1)).strip()
        description = desc_text[:160] + ("..." if len(desc_text) > 160 else "")
    else:
        description = title_tag

    # Calculate read time (words / 200)
    words = len(re.sub(r"<[^>]*>", " ", inner_html).split())
    read_time = f"{max(3, round(words / 200))} min read"

    meta_info = page_meta.get(filename, {"tag": "Strategy", "img": "assets/blog-outreach.png"})
    tag = meta_info["tag"]
    featured_img = meta_info["img"]

    # Short title for breadcrumbs
    short_title = h1_title[:35] + ("..." if len(h1_title) > 35 else "")

    # Derive keywords from title
    keywords = ", ".join(h1_title.lower().replace("?", "").replace("(", "").replace(")", "").split()[:6])

    page_html = template
    page_html = page_html.replace("{META_TITLE}", meta_title)
    page_html = page_html.replace("{TITLE}", title_tag)
    page_html = page_html.replace("{H1_TITLE}", h1_title)
    page_html = page_html.replace("{DESCRIPTION}", description.replace('"', '&quot;'))
    page_html = page_html.replace("{KEYWORDS}", keywords)
    page_html = page_html.replace("{SLUG}", slug)
    page_html = page_html.replace("{TAG}", tag)
    page_html = page_html.replace("{READ_TIME}", read_time)
    page_html = page_html.replace("{FEATURED_IMG}", featured_img)
    page_html = page_html.replace("{SHORT_TITLE}", short_title.replace('"', '&quot;'))
    page_html = page_html.replace("{INNER_HTML}", inner_html)

    page_html = page_html.replace("{{", "{").replace("}}", "}")

    output_path = os.path.join(blog_dir, f"{slug}.html")
    with open(output_path, "w", encoding="utf-8") as out_f:
        out_f.write(page_html)

    print(f"Created {output_path}")

    # Build blog.html card
    card_html = f"""          <div class="blog-card fade-in">
            <a href="/blog/{slug}" class="blog-card-img" style="background: none; overflow: hidden; display: block;">
              <img src="/{featured_img}" alt="{h1_title}" style="width: 100%; height: 100%; object-fit: cover;" loading="lazy">
            </a>
            <div class="blog-card-body">
              <span class="featured-tag">{tag}</span>
              <h4><a href="/blog/{slug}" style="color: inherit; text-decoration: none;">{h1_title}</a></h4>
              <p>{description[:120]}...</p>
              <div class="blog-meta">July 2026 · {read_time}</div>
              <a href="/blog/{slug}" class="read-more" style="margin-top: 12px;">Read Article →</a>
            </div>
          </div>"""
    new_cards.append((slug, card_html))

# Insert cards into blog.html if not already present
with open(blog_html_path, "r", encoding="utf-8") as f:
    blog_html = f.read()

for slug, card in new_cards:
    if f"/blog/{slug}" not in blog_html:
        # Insert before closing grid container
        marker = '</div>\n      </div>\n    </section>'
        if marker in blog_html:
            blog_html = blog_html.replace(marker, f"{card}\n        {marker}")
        else:
            blog_html = blog_html.replace('</div>\n    </section>', f"{card}\n      </div>\n    </section>")
        print(f"Added card for {slug} to blog.html")

with open(blog_html_path, "w", encoding="utf-8") as f:
    f.write(blog_html)

print("Done processing files (36).")
