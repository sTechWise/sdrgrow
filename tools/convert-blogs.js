const fs = require('fs');
const path = require('path');

const SRC_DIRS = [
    "C:/Users/rubaya/Downloads/SDR GROW/files (27)",
    "C:/Users/rubaya/Downloads/SDR GROW/files (28)",
    "C:/Users/rubaya/Downloads/SDR GROW/files (29)",
    "C:/Users/rubaya/Downloads/SDR GROW/files (30)",
    "C:/Users/rubaya/Downloads/SDR GROW/files (31)",
    "C:/Users/rubaya/Downloads/SDR GROW/files (32)",
    "C:/Users/rubaya/Downloads/SDR GROW/files (33)",
    "C:/Users/rubaya/Downloads/SDR GROW/files (34)",
    "C:/Users/rubaya/Downloads/SDR GROW/files (35)"
];
const SCHEMA_FILE = "C:/Users/rubaya/Downloads/SDR GROW/files (35)/all-blog-schemas.html";
const OUT_DIR = "C:/Users/rubaya/Desktop/sTechWise/SDR GROW/blog/_drafts";
const OUT_MANIFEST = path.join(OUT_DIR, "manifest.json");

if (!fs.existsSync(OUT_DIR)) {
    fs.mkdirSync(OUT_DIR, { recursive: true });
}

let allSchemasText = "";
if (fs.existsSync(SCHEMA_FILE)) {
    allSchemasText = fs.readFileSync(SCHEMA_FILE, 'utf-8');
}

function extractSchema(filename) {
    const regex = new RegExp(`<!-- ===== ${filename} .*? ===== -->([\\s\\S]*?)(?=<!-- =====|$)`, 'i');
    const match = allSchemasText.match(regex);
    if (match) {
        return match[1].trim();
    }
    return "";
}

function generateArticleSchema(title, description, slug) {
    return `<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://sdrgrow.com/blog/${slug}"
  },
  "headline": "${title.replace(/"/g, '\\"')}",
  "description": "${description.replace(/"/g, '\\"')}",
  "image": "https://sdrgrow.com/assets/og-image.png",
  "author": {
    "@type": "Person",
    "name": "Abir",
    "url": "https://linkedin.com/company/sdrgrow"
  },
  "publisher": {
    "@type": "Organization",
    "name": "SDR GROW",
    "logo": {
      "@type": "ImageObject",
      "url": "https://sdrgrow.com/assets/logo.png"
    }
  },
  "datePublished": "2026-07-01",
  "dateModified": "2026-07-01"
}
</script>`;
}

function assignTag(title, filename) {
    const t = (title + " " + filename).toLowerCase();
    if (t.match(/vs|compared|best.*tools|alternatives|outbound-systems/)) return "Comparison";
    if (t.match(/email|deliverability|warmup|spam|spf|dkim|domain|inbox|send-volume|open-rates|infrastructure/)) return "Email";
    if (t.match(/linkedin|connection|profile|commenting/)) return "LinkedIn";
    if (t.match(/cold-email-that-wins|opening|follow-up|break-up|personalization|first-line|cta|templates|length|ab-testing/)) return "Copywriting";
    if (t.match(/cost|price|budget|roi|fees|payback|cheap-tools|lifetime-value|feast-or-famine|diy-stack-cost|real-cost/)) return "Pricing";
    if (t.match(/tech-recruitment|healthcare|finance|construction|legal|executive|temp-staffing|boutique|uk-to-us|picking-a-niche/)) return "Niche";
    if (t.match(/competitor|mentions|buying-signals|rival|warning-signs|trigger-events|funding-round|hiring-season|learning-from|fresh-postings|responding-to-rival/)) return "Intelligence";
    if (t.match(/lead-engine|lead-generation|first-client|client-acquisition/)) return "Lead Generation";
    if (t.match(/sequence|multichannel|outbound-vs|cold-email-vs-linkedin|one-person-agency|brand-voice|16-touch|visibility/)) return "Strategy";
    return "Strategy";
}

function generateKeywords(title) {
    const words = title.toLowerCase().replace(/[^a-z0-9\s]/g, '').split(/\s+/).filter(w => w.length > 3);
    return words.slice(0, 6).join(', ');
}

function calculateReadTime(text) {
    const words = text.split(/\s+/).length;
    const minutes = Math.ceil(words / 200);
    return `${minutes} min read`;
}

function processMd(content, filename) {
    const lines = content.replace(/\r\n/g, '\n').split('\n');
    let title = "";
    let description = "";
    let htmlBody = [];
    let inList = false;
    let listType = "";
    let plainText = "";

    const closeList = () => {
        if (inList) {
            htmlBody.push(listType === 'ul' ? '</ul>' : '</ol>');
            inList = false;
        }
    };

    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        plainText += line + " ";

        if (i === 0 && line.startsWith('# ')) {
            title = line.replace('# ', '').trim();
            continue;
        }
        if (line.startsWith('Author:') || line.startsWith('Published:')) {
            continue;
        }
        if (!line) {
            continue;
        }

        if (!description && !line.startsWith('#') && !line.startsWith('-')) {
            description = line.replace(/\*\*/g, '').substring(0, 160);
            if (description.length === 160) description = description.trim() + "...";
        }

        line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        line = line.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

        if (line.startsWith('## ')) {
            closeList();
            htmlBody.push(`<h2>${line.replace('## ', '').trim()}</h2>`);
        } else if (line.match(/^[-*]\s+(.*)$/)) {
            if (!inList || listType !== 'ul') {
                closeList();
                htmlBody.push('<ul>');
                inList = true;
                listType = 'ul';
            }
            const match = line.match(/^[-*]\s+(.*)$/)[1];
            const content = match.replace(/^\[ \]\s*/, '');
            htmlBody.push(`<li>${content}</li>`);
        } else if (line.match(/^\d+\.\s+(.*)$/)) {
            if (!inList || listType !== 'ol') {
                closeList();
                htmlBody.push('<ol>');
                inList = true;
                listType = 'ol';
            }
            const content = line.match(/^\d+\.\s+(.*)$/)[1];
            htmlBody.push(`<li>${content}</li>`);
        } else if (line.startsWith('> ')) {
            closeList();
            htmlBody.push(`<blockquote><p>${line.replace('> ', '')}</p></blockquote>`);
        } else if (line.match(/^<strong>(.*?)\??<\/strong>$/)) {
            closeList();
            htmlBody.push(`<p><strong>${line.replace(/<\/?strong>/g, '')}?</strong></p>`);
        } else {
            closeList();
            htmlBody.push(`<p>${line}</p>`);
        }
    }
    closeList();
    
    const readTime = calculateReadTime(plainText);
    const tag = assignTag(title, filename);
    const keywords = generateKeywords(title);
    const slug = filename.replace(/^blog-\d+-/, '').replace('.md', '');
    let schema = extractSchema(filename);
    if (!schema) {
        schema = generateArticleSchema(title, description, slug);
    }

    return { title, description, htmlBody: htmlBody.join('\n'), tag, keywords, readTime, slug, schema };
}

function processHtml(content, filename) {
    let title = "Article";
    let description = "";
    let htmlBody = "";
    
    const articleMatch = content.match(/<article[^>]*>([\s\S]*?)<\/article>/i);
    if (articleMatch) {
        htmlBody = articleMatch[1].trim();
    } else {
        htmlBody = content;
    }

    const h1Match = htmlBody.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i);
    if (h1Match) {
        title = h1Match[1].replace(/<[^>]*>/g, '').trim();
        htmlBody = htmlBody.replace(/<h1[^>]*>[\s\S]*?<\/h1>/i, '');
    }

    // Strip Author/Published metadata paragraph from body
    htmlBody = htmlBody.replace(/<p>Author:[\s\S]*?<\/p>/i, '');

    // Get description from the first real content paragraph (not metadata)
    const allParagraphs = htmlBody.match(/<p[^>]*>([\s\S]*?)<\/p>/gi) || [];
    for (const pTag of allParagraphs) {
        const pContent = pTag.replace(/<[^>]*>/g, '').trim();
        if (pContent && !pContent.startsWith('Author:') && !pContent.startsWith('Published:') && pContent.length > 30) {
            description = pContent.substring(0, 160);
            if (description.length === 160) description = description.trim() + "...";
            break;
        }
    }

    const plainText = htmlBody.replace(/<[^>]*>/g, ' ');
    const readTime = calculateReadTime(plainText);
    const slug = filename.replace('.html', '');
    const tag = assignTag(title, filename);
    const keywords = generateKeywords(title);
    const schema = generateArticleSchema(title, description, slug);

    return { title, description, htmlBody, tag, keywords, readTime, slug, schema };
}

const comparisonFiles = [
    "best-outbound-systems-recruitment-agencies.html",
    "sdr-grow-vs-clay.html",
    "sdr-grow-vs-hiring-an-sdr.html",
    "sdr-grow-vs-instantly.html",
    "sdr-grow-vs-smartlead.html"
];

let items = [];

for (const dir of SRC_DIRS) {
    if (!fs.existsSync(dir)) continue;
    const files = fs.readdirSync(dir);
    for (const file of files) {
        const ext = path.extname(file).toLowerCase();
        if (ext === '.md' && file.startsWith('blog-')) {
            items.push({ type: 'md', path: path.join(dir, file), filename: file });
        } else if (ext === '.html' && comparisonFiles.includes(file)) {
            items.push({ type: 'html', path: path.join(dir, file), filename: file });
        }
    }
}

items.sort((a, b) => {
    if (a.type === 'html' && b.type === 'md') return -1;
    if (a.type === 'md' && b.type === 'html') return 1;
    if (a.type === 'html') {
        return comparisonFiles.indexOf(a.filename) - comparisonFiles.indexOf(b.filename);
    }
    const numA = parseInt(a.filename.match(/blog-(\d+)-/)[1], 10);
    const numB = parseInt(b.filename.match(/blog-(\d+)-/)[1], 10);
    return numA - numB;
});

const template = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{TITLE} — SDR GROW</title>
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

  {ARTICLE_SCHEMA_JSON_LD}
  
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://sdrgrow.com/"},
      {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://sdrgrow.com/blog"},
      {"@type": "ListItem", "position": 3, "name": "{TITLE_SHORT}", "item": "https://sdrgrow.com/blog/{SLUG}"}
    ]
  }
  </script>

  <style>
    .article-hero { padding: 100px 0 60px; background: var(--bg-light); border-bottom: 1px solid var(--border); }
    .article-hero .featured-tag { margin-bottom: 16px; }
    .article-hero h1 { font-family: var(--font-display); font-size: clamp(2rem, 4vw, 2.8rem); font-weight: 700; color: var(--text-primary); letter-spacing: -0.02em; margin-bottom: 16px; max-width: 720px; }
    .article-hero .blog-meta { font-family: var(--font-body); font-size: 0.85rem; color: var(--text-muted); }
    .article-body { padding: 60px 0 80px; background: var(--bg-white); }
    .article-content { max-width: 720px; margin: 0 auto; }
    .article-content h2 { font-family: var(--font-heading); font-size: 1.4rem; font-weight: 600; color: var(--text-primary); margin: 40px 0 16px; }
    .article-content p { font-family: var(--font-paragraph); font-size: 1rem; color: var(--text-secondary); line-height: 1.85; margin-bottom: 18px; }
    .article-content ul, .article-content ol { padding-left: 24px; margin-bottom: 18px; }
    .article-content li { font-family: var(--font-paragraph); font-size: 0.95rem; color: var(--text-secondary); line-height: 1.8; margin-bottom: 8px; }
    .article-content strong { color: var(--text-primary); }
    .article-content blockquote { border-left: 3px solid var(--accent); padding: 16px 24px; margin: 24px 0; background: var(--accent-light); border-radius: 0 var(--radius) var(--radius) 0; }
    .article-content blockquote p { margin: 0; font-style: italic; color: var(--text-primary); }
    .article-content table { width: 100%; border-collapse: collapse; margin: 24px 0; font-family: var(--font-paragraph); font-size: 0.92rem; }
    .article-content th { text-align: left; padding: 12px; border-bottom: 2px solid var(--border); color: var(--text-primary); font-weight: 600; }
    .article-content td { padding: 12px; border-bottom: 1px solid var(--border); color: var(--text-secondary); }
    .article-content tr:hover { background: var(--bg-light); }
    .article-cta { text-align: center; padding: 40px; background: var(--bg-light); border: 1px solid var(--border); border-radius: var(--radius-lg); margin: 40px 0; }
    .article-cta p { margin-bottom: 20px; }
    .article-back { display: inline-flex; align-items: center; gap: 8px; font-family: var(--font-body); font-size: 0.88rem; font-weight: 500; color: var(--accent); margin-bottom: 32px; transition: gap 0.2s ease; }
    .article-back:hover { gap: 12px; }
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
        <h1>{TITLE}</h1>
        <div class="blog-meta">By <a href="https://linkedin.com/company/sdrgrow" target="_blank" rel="noopener" style="color: inherit; text-decoration: underline;">Abir, Founder of SDR GROW</a> · July 2026 · {READ_TIME}</div>
      </div>
    </section>

    <section class="article-body">
      <div class="container">
        <div class="article-content">
          <a href="/blog" class="article-back">← Back to Blog</a>

          {ARTICLE_HTML_CONTENT}

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
</html>`;

let manifest = { blogs: [] };

for (let i = 0; i < items.length; i++) {
    const item = items[i];
    const content = fs.readFileSync(item.path, 'utf-8');
    let parsed;
    
    if (item.type === 'md') {
        parsed = processMd(content, item.filename);
    } else {
        parsed = processHtml(content, item.filename);
    }

    const order = i + 1;
    const draftFilename = `${order.toString().padStart(3, '0')}-${parsed.slug}.html`;

    let finalHtml = template
        .replace(/{TITLE}/g, parsed.title)
        .replace(/{DESCRIPTION}/g, parsed.description)
        .replace(/{KEYWORDS}/g, parsed.keywords)
        .replace(/{SLUG}/g, parsed.slug)
        .replace(/{TITLE_SHORT}/g, parsed.title.length > 30 ? parsed.title.substring(0, 30) + '...' : parsed.title)
        .replace(/{TAG}/g, parsed.tag)
        .replace(/{READ_TIME}/g, parsed.readTime)
        .replace(/{ARTICLE_SCHEMA_JSON_LD}/g, parsed.schema)
        .replace(/{ARTICLE_HTML_CONTENT}/g, parsed.htmlBody);

    fs.writeFileSync(path.join(OUT_DIR, draftFilename), finalHtml);
    
    manifest.blogs.push({
        order: order,
        draftFilename: draftFilename,
        slug: parsed.slug,
        title: parsed.title,
        description: parsed.description,
        tag: parsed.tag,
        readTime: parsed.readTime,
        datePublished: "2026-07-19",
        published: false
    });
}

fs.writeFileSync(OUT_MANIFEST, JSON.stringify(manifest, null, 2));
console.log("Successfully generated", manifest.blogs.length, "blogs.");
