const fs = require('fs');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');
const blogDir = path.join(rootDir, 'blog');
const sitemapPath = path.join(rootDir, 'sitemap.xml');

const today = new Date().toISOString().split('T')[0];

const staticPages = [
  { url: 'https://sdrgrow.com/', priority: '1.0', changefreq: 'weekly' },
  { url: 'https://sdrgrow.com/about', priority: '0.7', changefreq: 'monthly' },
  { url: 'https://sdrgrow.com/blog', priority: '0.8', changefreq: 'weekly' },
  { url: 'https://sdrgrow.com/book', priority: '0.9', changefreq: 'monthly' }
];

let urls = [...staticPages];

if (fs.existsSync(blogDir)) {
  const files = fs.readdirSync(blogDir);
  for (const file of files) {
    if (file.endsWith('.html') && file !== 'apex-staffing-case-study.html') {
      const slug = file.replace(/\.html$/, '');
      urls.push({
        url: `https://sdrgrow.com/blog/${slug}`,
        priority: '0.7',
        changefreq: 'monthly'
      });
    }
  }
}

let xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n`;

for (const u of urls) {
  xml += `  <url>\n    <loc>${u.url}</loc>\n    <lastmod>${today}</lastmod>\n    <changefreq>${u.changefreq}</changefreq>\n    <priority>${u.priority}</priority>\n  </url>\n`;
}

xml += `</urlset>\n`;

fs.writeFileSync(sitemapPath, xml, 'utf8');
console.log(`Generated sitemap.xml with ${urls.length} URLs.`);
