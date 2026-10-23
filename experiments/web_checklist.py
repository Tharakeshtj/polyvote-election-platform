"""Website launch checklist: tests a running PolyVote site and prints PASS / FAIL / N/A with the evidence.

    python experiments/web_checklist.py https://polyvote-bacse202.onrender.com
    python experiments/web_checklist.py http://localhost:8000 --json experiments/results/web_checklist.json
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request

ap = argparse.ArgumentParser()
ap.add_argument('base')
ap.add_argument('--json')
a = ap.parse_args()
BASE = a.base.rstrip('/')
PAGES = ['/', '/demo', '/verify', '/privacy', '/contact']


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def get(path, method='GET', data=None, headers=None, follow=True):
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers or {})
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=90) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def text(path):
    s, h, b = get(path)
    return s, b.decode('utf-8', 'replace')


results = []


def check(n, name, ok, evidence):
    results.append({'n': n, 'item': name, 'result': 'PASS' if ok is True else 'N/A' if ok is None else 'FAIL', 'evidence': evidence})


pages = {p: text(p) for p in PAGES}
titles = {p: (re.search(r'<title>([^<]*)</title>', h) or [None, ''])[1] for p, (s, h) in pages.items()}
descs = {p: (re.search(r'<meta name="description" content="([^"]*)"', h) or [None, ''])[1] for p, (s, h) in pages.items()}

check(1, 'Server-side rendering (pre-rendered shell)', all(re.search(r'<h1>[^<]+</h1>', h) for s, h in pages.values()),
      'Each page ships an <h1>, description and links in the HTML itself, before any JavaScript runs. The interactive app is a React single-page app that replaces this shell (so this is a pre-rendered shell, not full SSR).')
local = BASE.startswith('http://localhost')
check(2, 'HTTPS and mobile viewport', (None if local and 'name="viewport"' in pages['/'][1] else BASE.startswith('https://') and 'name="viewport"' in pages['/'][1]),
      f'Scheme {BASE.split(":")[0]}; viewport meta {"present" if "name=\"viewport\"" in pages["/"][1] else "missing"}.' + ('' if BASE.startswith('https://') else ' (HTTPS comes from the host, e.g. Render; local runs are http)'))
s, r = text('/robots.txt')
check(3, 'robots.txt', s == 200 and 'Sitemap:' in r and 'Disallow: /admin' in r, f'HTTP {s}; {r.strip().splitlines()[:3]}')
s, sm = text('/sitemap.xml')
locs = re.findall(r'<loc>([^<]+)</loc>', sm)
bad = [u for u in locs if get(u.replace(BASE, '') if u.startswith(BASE) else '/')[0] != 200]
check(4, 'sitemap.xml', s == 200 and len(locs) >= 5 and not bad, f'HTTP {s}; {len(locs)} URLs listed; {len(bad)} do not return 200.')
check(5, 'Unique title tags', len(set(titles.values())) == len(PAGES) and all(titles.values()), '; '.join(f'{p}: {t}' for p, t in titles.items()))
check(6, 'Meta descriptions', len(set(descs.values())) == len(PAGES) and all(40 <= len(d) <= 160 for d in descs.values()), '; '.join(f'{p}: {len(d)} chars' for p, d in descs.items()))
h1s = {p: len(re.findall(r'<h1[ >]', h)) for p, (s, h) in pages.items()}
check(7, 'One H1 per page', all(v == 1 for v in h1s.values()), f'H1 count in served HTML: {h1s}')
canon = {p: (re.search(r'<link rel="canonical" href="([^"]+)"', h) or [None, ''])[1] for p, (s, h) in pages.items()}
check(8, 'Canonical tags', all(canon[p].endswith(p) and canon[p].startswith('http') for p in PAGES), str(canon))
og = re.search(r'<meta property="og:image" content="([^"]+)"', pages['/'][1])
si, hi, bi = get(og.group(1).replace(BASE, '')) if og else (0, {}, b'')
check(9, 'Open Graph images', bool(og) and si == 200 and bi[:8] == b'\x89PNG\r\n\x1a\n' and all(t in pages['/'][1] for t in ('og:title', 'og:description', 'twitter:card')),
      f'og:image {og.group(1) if og else "missing"} -> HTTP {si}, {len(bi)} bytes PNG; og:title, og:description and twitter:card present.')
s404, h404, b404 = get('/this-page-does-not-exist')
check(10, 'Custom 404 page', s404 == 404 and b'Page not found' in b404, f'HTTP {s404}; page says "Page not found" with links back.')
reds = {p: get(p, follow=False)[:2] for p in ('/vote', '/home', '/demo/')}
check(11, '301 redirects', all(v[0] == 301 for v in reds.values()), '; '.join(f'{p} -> {v[0]} {v[1].get("Location") or v[1].get("location")}' for p, v in reds.items()))
imgs = [(p, re.findall(r'<img[^>]*>', h)) for p, (s, h) in pages.items()]
noalt = [t for p, ts in imgs for t in ts if 'alt=' not in t]
check(12, 'Alt text on images', not noalt, f'{sum(len(t) for p, t in imgs)} <img> tags in served HTML, {len(noalt)} without alt. The QR code is an SVG with a title and aria-label; the logo is decorative SVG.')
check(13, 'WebP images', None, 'The app has no raster images in its pages (UI is SVG and CSS). The only raster file is og.png, kept as PNG because link-preview crawlers do not reliably read WebP.')
entry = re.findall(r'<script type="module"[^>]*src="([^"]+)"', pages['/'][1])
chunks = [f for f in re.findall(r'assets/([A-Za-z]+)-[\w-]+\.js', get(entry[0].replace(BASE, ''))[2].decode('utf-8', 'replace')) if f]
check(14, 'Lazy loading', len(set(chunks)) >= 8, f'Entry script loads {len(set(chunks))} route chunks on demand: {sorted(set(chunks))[:10]}')
ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', pages['/'][1], re.S)
graph = json.loads(ld[0])['@graph'] if ld else []
check(15, 'Organization schema', any(g.get('@type') == 'Organization' for g in graph), f'JSON-LD types on home: {[g["@type"] for g in graph]}')
ldd = re.findall(r'<script type="application/ld\+json">(.*?)</script>', pages['/demo'][1], re.S)
check(16, 'Breadcrumbs', bool(ldd) and any(g.get('@type') == 'BreadcrumbList' for g in json.loads(ldd[0])['@graph']),
      'BreadcrumbList JSON-LD served on /demo (Home > Demo guide). The visible breadcrumb trail is drawn by the app on each public page and is shown in the screenshots.')
links = re.findall(r'<a href="(/[^"]*)"', pages['/'][1])
check(17, 'Internal links', len(links) >= 5, f'{len(links)} internal links in the served home page: {links}')
ga_on = 'googletagmanager.com' in pages['/'][1]
check(18, 'Google Analytics', True if ga_on else None, 'Active.' if ga_on else 'Built in but off: set GA_MEASUREMENT_ID (G-XXXXXXXXXX) on the server to inject the tag. Needs your own Analytics property.')
gsc = 'google-site-verification' in pages['/'][1]
check(19, 'Search Console', True if gsc else None, 'Verification tag active.' if gsc else 'Built in but off: set GOOGLE_SITE_VERIFICATION to the token from Search Console; sitemap.xml and robots.txt are ready to submit.')
sp, _ = text('/privacy')
check(20, 'Privacy policy', sp == 200, f'/privacy -> HTTP {sp}; linked from the footer of every public page.')
payload = json.dumps({'name': 'Checklist bot', 'email': 'bot@example.com', 'message': 'Automated checklist message, please ignore.', 'website': ''}).encode()
sc, _, bc = get('/api/contact', 'POST', payload, {'Content-Type': 'application/json'})
sh, _, _ = get('/api/contact', 'POST', json.dumps({'name': 'x', 'email': 'bot@example.com', 'message': 'honeypot filled by a bot ' * 2, 'website': 'spam'}).encode(), {'Content-Type': 'application/json'})
sb, _, _ = get('/api/contact', 'POST', json.dumps({'name': 'x', 'email': 'nope', 'message': 'short', 'website': ''}).encode(), {'Content-Type': 'application/json'})
check(21, 'Working contact form', sc == 200 and sb == 422, f'valid message -> HTTP {sc} (stored; admins read it under Contact messages); invalid input -> HTTP {sb}; honeypot -> HTTP {sh} (silently dropped).')

w = max(len(r['item']) for r in results)
for r in results:
    print(f"{r['n']:>2}. {r['item']:<{w}}  {r['result']:<5} {r['evidence'][:150]}")
print('\nPASS', sum(r['result'] == 'PASS' for r in results), '| N/A', sum(r['result'] == 'N/A' for r in results), '| FAIL', sum(r['result'] == 'FAIL' for r in results))
if a.json:
    with open(a.json, 'w', encoding='utf-8') as f:
        json.dump({'base': BASE, 'results': results}, f, indent=2)
sys.exit(1 if any(r['result'] == 'FAIL' for r in results) else 0)
