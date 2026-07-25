const fs = require('fs');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');
const draftsDir = path.join(rootDir, 'blog', '_drafts');
const manifestPath = path.join(draftsDir, 'manifest.json');
const blogDir = path.join(rootDir, 'blog');
const sitemapPath = path.join(rootDir, 'sitemap.xml');
const llmsPath = path.join(rootDir, 'llms.txt');
const blogHtmlPath = path.join(rootDir, 'blog.html');

// Read count argument
const countArg = process.argv[2];
const limit = countArg ? parseInt(countArg, 10) || 3 : 3;

if (!fs.existsSync(manifestPath)) {
  console.log(`Manifest file not found at ${manifestPath}. Nothing to publish.`);
  process.exit(0);
}

let manifestRaw = fs.readFileSync(manifestPath, 'utf8');
let manifest;
try {
  manifest = JSON.parse(manifestRaw);
} catch (err) {
  console.error(`Error parsing manifest.json:`, err);
  process.exit(1);
}

let items = [];
if (Array.isArray(manifest)) {
  items = manifest;
} else if (manifest && Array.isArray(manifest.blogs)) {
  items = manifest.blogs;
} else if (manifest && Array.isArray(manifest.drafts)) {
  items = manifest.drafts;
}

const unpublished = items.filter(item => item.published === false || item.status === 'draft' || (!item.published && item.status !== 'published'));

if (unpublished.length === 0) {
  console.log('No unpublished blogs found in manifest.json.');
  process.exit(0);
}

const toPublish = unpublished.slice(0, limit);
console.log(`Publishing ${toPublish.length} blog(s)...`);

const today = new Date().toISOString().split('T')[0];

let sitemapContent = fs.existsSync(sitemapPath) ? fs.readFileSync(sitemapPath, 'utf8') : '';
let llmsContent = fs.existsSync(llmsPath) ? fs.readFileSync(llmsPath, 'utf8') : '';
let blogHtmlContent = fs.existsSync(blogHtmlPath) ? fs.readFileSync(blogHtmlPath, 'utf8') : '';

for (const blog of toPublish) {
  // Determine draft file name and slug
  let draftFilename = blog.draftFilename || blog.filename || blog.file || blog.draftFile || (blog.id ? `${blog.id}.html` : null);
  let slug = blog.slug;

  if (!slug && draftFilename) {
    slug = draftFilename.replace(/^\d+-/, '').replace(/\.html$/, '');
  }

  if (!draftFilename && slug && fs.existsSync(draftsDir)) {
    const files = fs.readdirSync(draftsDir);
    const matched = files.find(f => f.endsWith(`${slug}.html`) || f === `${slug}.html`);
    if (matched) {
      draftFilename = matched;
    }
  }

  if (!slug) {
    console.error(`Could not determine slug for blog:`, blog);
    continue;
  }

  blog.slug = slug;
  const targetFilename = `${slug}.html`;
  const targetPath = path.join(blogDir, targetFilename);

  // Step 3a: Move HTML file from blog/_drafts/ to blog/
  if (draftFilename) {
    const sourcePath = path.join(draftsDir, draftFilename);
    if (fs.existsSync(sourcePath)) {
      fs.copyFileSync(sourcePath, targetPath);
      fs.unlinkSync(sourcePath);
      console.log(`Moved ${draftFilename} -> ${targetFilename}`);
    } else {
      console.warn(`Draft file not found at ${sourcePath}`);
    }
  } else {
    console.warn(`No draft file specified for slug ${slug}`);
  }

  // Step 3b: Append sitemap.xml entry
  const sitemapEntry = `  <url>\n    <loc>https://sdrgrow.com/blog/${slug}</loc>\n    <lastmod>${today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n`;
  if (sitemapContent.includes('</urlset>')) {
    sitemapContent = sitemapContent.replace('</urlset>', `${sitemapEntry}</urlset>`);
    console.log(`Added sitemap entry for /blog/${slug}`);
  }

  // Step 3c: Append llms.txt entry before ## Contact
  const title = blog.title || slug;
  const llmsEntry = `- [${title}](https://sdrgrow.com/blog/${slug})`;
  if (llmsContent.includes('## Contact')) {
    llmsContent = llmsContent.replace('## Contact', `${llmsEntry}\n\n## Contact`);
    console.log(`Added llms.txt entry for ${title}`);
  }

  // Step 3d: Insert card into blog.html
  const tag = blog.tag || blog.category || 'Outbound';
  const rawDescription = blog.description || '';
  const descriptionShort = rawDescription.length > 120 ? rawDescription.slice(0, 120) + '...' : rawDescription;
  const readTime = blog.readTime || blog.read_time || '5 min read';
  const cardDate = blog.date || 'July 2026';

  const cardHtml = `          <div class="blog-card fade-in">
            <a href="/blog/${slug}" class="blog-card-img" style="background: linear-gradient(135deg, var(--accent-light), var(--primary-light)); display: flex; align-items: center; justify-content: center; font-family: var(--font-display); font-size: 1.1rem; color: var(--accent); text-align: center; padding: 20px;">${tag}</a>
            <div class="blog-card-body">
              <span class="featured-tag">${tag}</span>
              <h4><a href="/blog/${slug}" style="color: inherit; text-decoration: none;">${title}</a></h4>
              <p>${descriptionShort}</p>
              <div class="blog-meta">${cardDate} · ${readTime}</div>
              <a href="/blog/${slug}" class="read-more" style="margin-top: 12px;">Read Article →</a>
            </div>
          </div>\n`;

  const gridCloseRegex = /(<\/div>\r?\n\s*<\/div>\r?\n\s*<\/section>\r?\n\s*<!-- NEWSLETTER -->)/;
  if (gridCloseRegex.test(blogHtmlContent)) {
    blogHtmlContent = blogHtmlContent.replace(gridCloseRegex, `${cardHtml}        </div>\n      </div>\n    </section>\n\n\n    <!-- NEWSLETTER -->`);
    console.log(`Inserted card for ${slug} into blog.html`);
  } else {
    const newsletterIdx = blogHtmlContent.indexOf('<!-- NEWSLETTER -->');
    if (newsletterIdx !== -1) {
      const beforeNewsletter = blogHtmlContent.slice(0, newsletterIdx);
      const afterNewsletter = blogHtmlContent.slice(newsletterIdx);
      const lastDivIdx = beforeNewsletter.lastIndexOf('</div>');
      if (lastDivIdx !== -1) {
        blogHtmlContent = beforeNewsletter.slice(0, lastDivIdx) + cardHtml + beforeNewsletter.slice(lastDivIdx) + afterNewsletter;
        console.log(`Inserted card for ${slug} into blog.html (fallback match)`);
      }
    }
  }

  // Step 4: Update manifest item status
  blog.published = true;
  if (blog.status) blog.status = 'published';
}

// Write updated files back
if (fs.existsSync(sitemapPath)) fs.writeFileSync(sitemapPath, sitemapContent, 'utf8');
if (fs.existsSync(llmsPath)) fs.writeFileSync(llmsPath, llmsContent, 'utf8');
if (fs.existsSync(blogHtmlPath)) fs.writeFileSync(blogHtmlPath, blogHtmlContent, 'utf8');
fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), 'utf8');

console.log(`Successfully published ${toPublish.length} blog(s) and updated manifest.json.`);
