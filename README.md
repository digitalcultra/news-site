# Digital Cultra News (MVP)
Run: `python3 server.py` → http://localhost:8795
- `sources.py`: feed list (name, lean, scope, url). Local scope = `local:<STATE>:<City|*>`. Add feeds per state/city here; any state/city without feeds falls back to a Google News local query.
- `server.py`: fetches feeds in parallel (10-min cache), parses RSS/Atom, clusters headlines by keyword overlap, computes status + underreported score with fixed rules. Serves `/api/news?state=IL&city=Chicago`. Stores headline, source, time, link only.
- Underreported score: +3 primary doc with ≤1 media pickup, +2 only one side (left or right) covering, +1 only 2–3 outlets, +1 coverage started and stopped within 12h and nothing new for 36h. Shown if score ≥2.
## Backend (pluggable)
`Store` in app.js is the only profile layer (localStorage). For real accounts, replace with Supabase: table `profiles(id uuid pk references auth.users, email, country, state, city)`, magic-link email auth (`supabase.auth.signInWithOtp`), and `get/set` calling `from('profiles').select/upsert`. Free tier is enough to start.
## Hosting
The API needs a server (feeds lack CORS): Render/Fly free web service for server.py, or port `/api/news` to a Cloudflare Worker (free) + static files on Cloudflare Pages/Netlify.

## Monetization (config.js)
- `MEMBERSHIP_LINKS` – **TODO**: paste real Payhip membership checkout URLs ($4/mo, $36/yr).
- `AFFILIATE_TAG` – **TODO**: replace `TODO-20` with your Amazon Associates tracking ID. Gear buttons are Amazon searches with that tag; no prices are shown (Amazon rules).
- Member gating is a client-side flag (`localStorage.dcn_member = '1'`) for demo only. Real gating needs a backend: verify Payhip membership (webhook / license key), issue a session, and serve the full Underreported list + digest only to verified members.
- Newsletter box stores emails in `localStorage.dcn_newsletter` (this device only). **TODO (Beehiiv)**: create a free Beehiiv publication, copy Settings > Embed (subscribe form) and replace the `<form id="nl">` in index.html with the embed `<iframe>`, or POST to Beehiiv's subscriptions API from the server (API key must stay server-side).

## Infographics (site + video)
- `infographic.js` / `infographic.css`: 6 data-driven templates (`DCNInfo.title|coverage|timeline|numbers|claims|receipts`). Empty data = card hidden; nothing is invented.
- Story page: "Infographic" panel built from the real cluster (`DCNInfo.fromCluster`): coverage, timeline (headline times), receipts. Numbers/claims only appear if added to the story JSON.
- Video: `python3 video/render.py my_story.json [--name x] [--secs 5]` -> `video/out/x.mp4` (1080x1920, ~24s, 30fps) + `video/out/x_stills/*.png`. Schema: `video/story_template.json`. Demo: `video/demo_story.json`.

## Email (Brevo): daily digest + Insider alerts
Code: `mailer.py` (stdlib only). Everything is a no-op unless `BREVO_API_KEY` is set.

Render env vars: `BREVO_API_KEY`, `SENDER_EMAIL`, `SENDER_NAME` (set), `TICK_TOKEN` (random string, recommended), optional `ORG_ADDRESS` (mailing address shown in the email footer; required by US email law; set it only in Render env, never in code).

- **Signup** (`POST /api/signup`): saved to `signups.json` (fallback, wiped on Render restarts) and upserted as a Brevo contact (attributes CITY/STATE, list **Daily Local**, created automatically). "Chicago, IL" style city input is split into CITY/STATE.
- **Daily digest**: after 7 AM America/Chicago, "Top buried stories near you" goes to Daily Local contacts (max 250/day for the free tier). Each contact gets a `DC_LAST` attribute so restarts never cause duplicates. Real feed stories only, linking to `/story/<id>` pages.
- **Insider alerts**: every 15 min, contacts in the **Insider** list get an email when a new (under 6h), high-score (>=2) story matches their state/city. Deduped per story per contact, max 3/day (tracked in the `DC_ALERTS` attribute).
- **Add an Insider member manually** (until Payhip webhooks are wired): Brevo → Contacts → find/add the member's email → set CITY and STATE (2-letter) → "Add to list" → **Insider**. The Insider list appears after the first signup or tick; you can also create it by hand with that exact name.
- **Unsubscribe**: every email links to `/api/unsubscribe?e=..&t=..` (HMAC token), which blocklists the contact in Brevo. A `List-Unsubscribe` header is sent too.
- **Keep-alive cron (required on free Render)**: the free instance sleeps, so the background thread stops. Create a free job at cron-job.org hitting `https://digitalcultra-news.onrender.com/api/tick?token=YOUR_TICK_TOKEN` every 15 minutes. `/api/tick` runs whatever is due and is safe to call often.
- Tests: `python3 -m unittest tests.test_mailer`.
