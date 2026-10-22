# SEO launch checklist — Digital Cultra News
1. Get a domain; host the site (Netlify/Render/Cloudflare). Set `SITE_URL` in `seo_config.py` and the canonical in `index.html` (currently https://example.com). Set `CONTACT_EMAIL` to a brand inbox.
2. Google Search Console: add the domain property, verify by DNS TXT, submit `/sitemap.xml` and `/news-sitemap.xml`. Use URL Inspection on a few `/story/...` pages.
3. Google Publisher Center: add the publication (brand name only), link the site and RSS `/feed.xml`, and fill in the About/Contact/Editorial policy links.
4. Bing Webmaster Tools: import from Search Console and submit the same sitemaps.
5. Test pages in Rich Results Test (NewsArticle) and the PageSpeed Insights mobile report.
6. Add a real 1200px-wide share image (og:image and JSON-LD image currently use a small SVG icon).

## Honest notes
- Google decides who appears in Top Stories and Google News. You can't apply or pay to get in, and you're not guaranteed a spot.
- Sites that only aggregate headlines rarely rank. Google rewards original reporting and E-E-A-T (experience, expertise, authority, trust). Our own content is just the coverage-context block. To compete, add original write-ups, local reporting and explainers.
- Pages: /about, /contact, /editorial-policy (brand name only).
- Story pages expire when they drop out of the feeds (5 days). Google will see 404s for old ones, which is normal. Keeping an archive would help ranking.
