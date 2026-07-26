import os
import re
import json

blog_dir = r"c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog"
drafts_dir = r"c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog\_drafts"
blog_html_path = r"c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog.html"

def update_blog_file(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update hero meta date and author
    def hero_meta_sub(m):
        meta_str = m.group(0)
        read_time = "5 min read"
        rt_m = re.search(r"(\d+\s*min\s*read)", meta_str)
        if rt_m:
            read_time = rt_m.group(1)
        return f'<div class="blog-meta">By <a href="https://linkedin.com/company/sdrgrow" target="_blank" rel="noopener" style="color: inherit; text-decoration: underline;">Abir, Founder of SDR GROW</a> · July 2026 · {read_time}</div>'

    content = re.sub(r'<div class="blog-meta">.*?</div>', hero_meta_sub, content)

    # 2. Update trust block
    new_trust_block = '''<div class="trust-block">
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
  </div>'''

    content = re.sub(r'<div class="trust-block">[\s\S]*?</div>\s*</div>\s*</div>\s*</div>\s*</div>', new_trust_block, content)
    # also handle any stray </div></div> left over
    content = re.sub(r'(<span>Published: July 2026</span>\s*</div>\s*</div>\s*</div>\s*</div>\s*)</div>', r'\1', content)

    # 3. Update footer Product links
    content = content.replace('<li><a href="/">Feature Modules</a></li>', '<li><a href="/#modules">Feature Modules</a></li>')
    content = content.replace('<li><a href="/">16-Touch Engine</a></li>', '<li><a href="/#process">16-Touch Engine</a></li>')
    content = content.replace('<li><a href="/">Pricing</a></li>', '<li><a href="/#value">Pricing</a></li>')

    # 4. JSON-LD updates: author, datePublished, dateModified
    def json_ld_sub(m):
        try:
            json_txt = m.group(1)
            data = json.loads(json_txt)
            
            def update_obj(obj):
                if isinstance(obj, dict):
                    if obj.get("@type") == "Article":
                        obj["author"] = {
                            "@type": "Person",
                            "name": "Abir",
                            "url": "https://linkedin.com/company/sdrgrow"
                        }
                        obj["datePublished"] = "2026-07-01"
                        if "dateModified" in obj:
                            del obj["dateModified"]
                    for k, v in list(obj.items()):
                        update_obj(v)
                elif isinstance(obj, list):
                    for item in obj:
                        update_obj(item)

            update_obj(data)
            return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'
        except Exception as e:
            ld_str = m.group(0)
            ld_str = re.sub(r'"author":\s*\{[^}]+\}', '"author":{"@type":"Person","name":"Abir","url":"https://linkedin.com/company/sdrgrow"}', ld_str)
            ld_str = re.sub(r'"datePublished":\s*"[^"]+"', '"datePublished":"2026-07-01"', ld_str)
            ld_str = re.sub(r',?\s*"dateModified":\s*"[^"]+"', '', ld_str)
            return ld_str

    content = re.sub(r'<script type="application/ld\+json">([\s\S]*?)</script>', json_ld_sub, content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

for f in os.listdir(blog_dir):
    if f.endswith(".html") and f != "apex-staffing-case-study.html":
        update_blog_file(os.path.join(blog_dir, f))

if os.path.exists(drafts_dir):
    for f in os.listdir(drafts_dir):
        if f.endswith(".html"):
            update_blog_file(os.path.join(drafts_dir, f))

if os.path.exists(blog_html_path):
    with open(blog_html_path, "r", encoding="utf-8") as f:
        bcontent = f.read()

    bcontent = re.sub(r'<div class="blog-meta">(?:March|December|January|February|April|May|June)\s+2025\s*·\s*', '<div class="blog-meta">July 2026 · ', bcontent)
    bcontent = re.sub(r'<div class="blog-meta">(?:March|December|January|February|April|May|June)\s+2026\s*·\s*', '<div class="blog-meta">July 2026 · ', bcontent)

    with open(blog_html_path, "w", encoding="utf-8") as f:
        f.write(bcontent)

print("Blog metadata updated cleanly.")
