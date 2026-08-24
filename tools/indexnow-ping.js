/**
 * IndexNow Ping Script for sdrgrow.com
 *
 * Usage:
 *   node tools/indexnow-ping.js <url1> [url2 ...]
 *   node tools/indexnow-ping.js --all
 *
 * Examples:
 *   node tools/indexnow-ping.js https://sdrgrow.com/bd-engine
 *   node tools/indexnow-ping.js /bd-engine /outbound-operating-system
 *   node tools/indexnow-ping.js --all
 */

const fs = require('fs');
const path = require('path');

const HOST = 'sdrgrow.com';
const KEY = '89b146d5103c427ab88c597b36ee6c33';
const KEY_LOCATION = 'https://sdrgrow.com/89b146d5103c427ab88c597b36ee6c33.txt';
const INDEXNOW_ENDPOINT = 'https://api.indexnow.org/indexnow';

/**
 * Normalize input URL to non-www https://sdrgrow.com/... format
 */
function normalizeUrl(input) {
  let urlStr = input.trim();
  
  if (!urlStr.startsWith('http://') && !urlStr.startsWith('https://')) {
    if (!urlStr.startsWith('/')) {
      urlStr = '/' + urlStr;
    }
    urlStr = `https://${HOST}${urlStr}`;
  }
  
  // Replace www.sdrgrow.com with sdrgrow.com
  urlStr = urlStr.replace('://www.sdrgrow.com', '://sdrgrow.com');
  urlStr = urlStr.replace('http://sdrgrow.com', 'https://sdrgrow.com');
  
  return urlStr;
}

/**
 * Extract URLs from local or remote sitemap.xml
 */
async function getSitemapUrls() {
  const rootDir = path.resolve(__dirname, '..');
  const localSitemap = path.join(rootDir, 'sitemap.xml');
  let xmlContent = '';

  if (fs.existsSync(localSitemap)) {
    console.log(`Reading local sitemap from: ${localSitemap}`);
    xmlContent = fs.readFileSync(localSitemap, 'utf-8');
  } else {
    console.log('Fetching remote sitemap from https://sdrgrow.com/sitemap.xml...');
    const res = await fetch('https://sdrgrow.com/sitemap.xml');
    if (!res.ok) {
      throw new Error(`Failed to fetch remote sitemap: HTTP ${res.status}`);
    }
    xmlContent = await res.text();
  }

  const locMatches = xmlContent.match(/<loc>(.*?)<\/loc>/gi) || [];
  const urls = locMatches.map(loc => {
    const raw = loc.replace(/<\/?loc>/gi, '').trim();
    return normalizeUrl(raw);
  });

  return Array.from(new Set(urls));
}

/**
 * Send POST request to IndexNow API
 */
async function sendIndexNowPing(urls) {
  if (!urls || urls.length === 0) {
    console.error('Error: No URLs to submit.');
    process.exit(1);
  }

  const normalizedUrls = Array.from(new Set(urls.map(normalizeUrl)));

  const payload = {
    host: HOST,
    key: KEY,
    keyLocation: KEY_LOCATION,
    urlList: normalizedUrls
  };

  console.log(`Submitting ${normalizedUrls.length} URL(s) to IndexNow (${INDEXNOW_ENDPOINT})...`);
  console.log(`Host: ${payload.host}`);
  console.log(`Key Location: ${payload.keyLocation}`);
  console.log(`URLs to ping:\n  - ${normalizedUrls.slice(0, 5).join('\n  - ')}${normalizedUrls.length > 5 ? `\n  ...and ${normalizedUrls.length - 5} more` : ''}\n`);

  try {
    const response = await fetch(INDEXNOW_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json; charset=utf-8'
      },
      body: JSON.stringify(payload)
    });

    const status = response.status;
    const bodyText = await response.text();

    console.log(`HTTP Status Code: ${status}`);
    console.log(`Response Body: ${bodyText || '(empty)'}`);

    if (status === 200 || status === 202) {
      console.log(`\nSUCCESS: ${status} ${status === 200 ? 'OK' : 'Accepted'} — IndexNow successfully received submission.`);
    } else {
      console.error(`\nFAILURE: HTTP ${status} — ${bodyText}`);
      process.exit(1);
    }
  } catch (err) {
    console.error(`Network or Request Error: ${err.message}`);
    process.exit(1);
  }
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log(`
IndexNow Ping Tool for sdrgrow.com

Usage:
  node tools/indexnow-ping.js <url1> [url2 ...]
  node tools/indexnow-ping.js --all

Examples:
  node tools/indexnow-ping.js https://sdrgrow.com/bd-engine
  node tools/indexnow-ping.js /bd-engine /outbound-operating-system
  node tools/indexnow-ping.js --all
`);
    process.exit(0);
  }

  if (args.includes('--all')) {
    const urls = await getSitemapUrls();
    await sendIndexNowPing(urls);
  } else {
    await sendIndexNowPing(args);
  }
}

main();
