"""Search-engine and link-preview basics for the single-page app.

The React build ships one index.html. This module fills in, per URL, what crawlers and link previews read
without running JavaScript: a unique title, meta description, canonical link, Open Graph and Twitter tags,
JSON-LD (Organization, WebApplication, BreadcrumbList) and a small static body. It also decides which URLs
exist (HTTP 404 for the rest) and which should redirect (HTTP 301).
"""
import html
import json
import os
import re

SITE = 'PolyVote'
GITHUB = 'https://github.com/Tharakeshtj/polyvote-election-platform'
DEFAULT_DESC = ('Run ranked-choice elections for clubs and councils. Voting rules live in the database, every ballot is sealed in an audit ledger, and voters confirm by email.')

# path -> (title, description, breadcrumb trail, indexable)
PAGES = {
    '/': ('PolyVote | Ranked-choice elections with a tamper-evident ledger', DEFAULT_DESC, [('Home', '/')], True),
    '/demo': ('Demo guide: every page of PolyVote', 'A tour of every page of the PolyVote demo with links, demo logins and a three-minute walkthrough.',
              [('Home', '/'), ('Demo guide', '/demo')], True),
    '/verify': ('Check your ballot receipt | PolyVote', 'Paste your receipt token to see whether your ballot is sealed in the audit ledger and still counted.',
                [('Home', '/'), ('Check receipt', '/verify')], True),
    '/privacy': ('Privacy policy | PolyVote', 'What PolyVote stores about voters, where it is stored, who can see it and how long it is kept.',
                 [('Home', '/'), ('Privacy policy', '/privacy')], True),
    '/contact': ('Contact PolyVote', 'Send a message to the PolyVote team about the project, a bug or an election you want to run.',
                 [('Home', '/'), ('Contact', '/contact')], True),
}
SITEMAP_PATHS = ['/', '/demo', '/verify', '/privacy', '/contact']
REDIRECTS = {'/vote': '/', '/index.html': '/', '/home': '/', '/index': '/'}


def clean(path: str):
    """Return (normalised path, redirect target or None)."""
    path = '/' + path.lstrip('/')
    if path in REDIRECTS:
        return path, REDIRECTS[path]
    if len(path) > 1 and path.endswith('/'):
        return path, path.rstrip('/')
    return path, None


def lookup(path: str):
    """Return (status, title, description, crumbs, indexable) for a request path."""
    if path in PAGES:
        t, d, crumbs, idx = PAGES[path]
        return 200, t, d, crumbs, idx
    m = re.fullmatch(r'/vote/(\d+)', path)
    if m:
        return 200, f'Vote in election {m.group(1)} | PolyVote', 'Sign in, confirm with your emailed code, rank your choices and get a receipt.', [('Home', '/'), (f'Election {m.group(1)}', path)], False
    if path == '/admin' or path.startswith('/admin/'):
        return 200, 'Administrator console | PolyVote', 'Election officer console.', [], False
    return 404, 'Page not found | PolyVote', 'That page does not exist. Use the links to return to PolyVote.', [], False


def base_url(request) -> str:
    env = os.environ.get('PUBLIC_URL', '').strip().rstrip('/')
    if env:
        return env
    proto = request.headers.get('x-forwarded-proto', request.url.scheme).split(',')[0].strip()
    host = request.headers.get('x-forwarded-host', request.headers.get('host', request.url.netloc)).split(',')[0].strip()
    return f'{proto}://{host}'


def head_tags(base: str, path: str, title: str, desc: str, crumbs, indexable: bool) -> str:
    e = html.escape
    url = base + (path if path != '/' else '/')
    img = f'{base}/og.png'
    tags = [
        f'<meta name="description" content="{e(desc)}" />',
        f'<link rel="canonical" href="{e(url)}" />',
        f'<meta name="robots" content="{"index, follow" if indexable else "noindex, nofollow"}" />',
        f'<meta property="og:type" content="website" />',
        f'<meta property="og:site_name" content="{SITE}" />',
        f'<meta property="og:title" content="{e(title)}" />',
        f'<meta property="og:description" content="{e(desc)}" />',
        f'<meta property="og:url" content="{e(url)}" />',
        f'<meta property="og:image" content="{e(img)}" />',
        '<meta property="og:image:width" content="1200" />',
        '<meta property="og:image:height" content="630" />',
        f'<meta property="og:image:alt" content="PolyVote: ranked-choice elections with a tamper-evident ledger" />',
        '<meta name="twitter:card" content="summary_large_image" />',
        f'<meta name="twitter:title" content="{e(title)}" />',
        f'<meta name="twitter:description" content="{e(desc)}" />',
        f'<meta name="twitter:image" content="{e(img)}" />',
    ]
    gsv = os.environ.get('GOOGLE_SITE_VERIFICATION', '').strip()
    if gsv:
        tags.append(f'<meta name="google-site-verification" content="{e(gsv)}" />')
    graph = [
        {'@type': 'Organization', 'name': SITE, 'url': base + '/', 'logo': img, 'sameAs': [GITHUB]},
        {'@type': 'WebApplication', 'name': SITE, 'url': base + '/', 'applicationCategory': 'BusinessApplication', 'operatingSystem': 'Any',
         'description': DEFAULT_DESC, 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'}},
    ]
    if crumbs:
        graph.append({'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'name': n, 'item': base + p} for i, (n, p) in enumerate(crumbs, start=1)]})
    tags.append('<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': graph}).replace('</', '<\\/') + '</script>')
    ga = os.environ.get('GA_MEASUREMENT_ID', '').strip()
    if re.fullmatch(r'G-[A-Z0-9]{4,}', ga):
        tags.append(f'<script async src="https://www.googletagmanager.com/gtag/js?id={ga}"></script>'
                    f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());gtag("config","{ga}");</script>')
    return '\n    '.join(tags)


def static_body(title: str, desc: str, status: int) -> str:
    """Readable content inside #root for crawlers and no-JavaScript browsers; React replaces it when it loads."""
    e = html.escape
    links = ''.join(f'<li><a href="{p}">{n}</a></li>' for n, p in [('Home', '/'), ('Demo guide', '/demo'), ('Check a receipt', '/verify'), ('Privacy policy', '/privacy'), ('Contact', '/contact')])
    h1 = 'Page not found' if status == 404 else title.split('|')[0].strip()
    return (f'<main style="font-family:system-ui,sans-serif;max-width:640px;margin:48px auto;padding:0 16px;line-height:1.5">'
            f'<h1>{e(h1)}</h1><p>{e(desc)}</p><nav aria-label="Site"><ul>{links}</ul></nav>'
            f'<noscript><p>PolyVote needs JavaScript to run an election.</p></noscript></main>')


def render(index_html: str, base: str, path: str) -> tuple[int, str]:
    status, title, desc, crumbs, idx = lookup(path)
    out = re.sub(r'<title>[^<]*</title>', f'<title>{html.escape(title)}</title>', index_html, count=1)
    out = out.replace('</head>', '    ' + head_tags(base, path, title, desc, crumbs, idx) + '\n  </head>', 1)
    out = out.replace('<div id="root"></div>', f'<div id="root">{static_body(title, desc, status)}</div>', 1)
    return status, out


def robots(base: str) -> str:
    return f'User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /api/\nDisallow: /vote/\n\nSitemap: {base}/sitemap.xml\n'


def sitemap(base: str) -> str:
    urls = ''.join(f'<url><loc>{html.escape(base + p)}</loc></url>' for p in SITEMAP_PATHS)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'
