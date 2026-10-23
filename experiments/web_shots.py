"""Screenshots of the public pages and the contact flow, used as evidence in the report and slides.

    python experiments/web_shots.py http://localhost:8030
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

base = sys.argv[1].rstrip('/')
out = Path(__file__).resolve().parent.parent / 'docs' / 'review3_assets' / 'screens'
out.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge')
    ctx = b.new_context(viewport={'width': 1280, 'height': 800}, device_scale_factor=2, color_scheme='light')
    pg = ctx.new_page()

    def shot(path, name, wait=700, full=False):
        pg.goto(base + path, wait_until='networkidle')
        pg.wait_for_timeout(wait)
        pg.screenshot(path=str(out / name), full_page=full)
        print('saved', name)

    shot('/', 'web_home.png')
    shot('/demo', 'web_demo.png', full=False)
    shot('/privacy', 'web_privacy.png', full=True)
    shot('/this-page-does-not-exist', 'web_404.png')
    pg.goto(base + '/contact', wait_until='networkidle')
    pg.fill('#c-name', 'Class Visitor')
    pg.fill('#c-email', 'visitor@example.com')
    pg.fill('#c-msg', 'Hello team, I tried the demo and the one-time code step worked well.')
    pg.screenshot(path=str(out / 'web_contact.png'))
    pg.click('button.btn-primary')
    pg.wait_for_selector('.callout-ok')
    pg.wait_for_timeout(300)
    pg.screenshot(path=str(out / 'web_contact_sent.png'))
    print('saved web_contact*.png')

    # admin sees the message
    pg.goto(base + '/admin/login', wait_until='networkidle')
    pg.fill('input[autocomplete="username"], #username, input[type="text"]', 'admin')
    pg.fill('input[type="password"]', 'admin123')
    pg.keyboard.press('Enter')
    pg.wait_for_url('**/admin')
    pg.goto(base + '/admin/messages', wait_until='networkidle')
    pg.wait_for_timeout(800)
    pg.screenshot(path=str(out / 'admin_messages.png'))
    print('saved admin_messages.png')

    # mobile
    mctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, color_scheme='light', is_mobile=True)
    mp = mctx.new_page()
    mp.goto(base + '/', wait_until='networkidle')
    mp.wait_for_timeout(600)
    mp.screenshot(path=str(out / 'web_home_mobile.png'))
    print('saved web_home_mobile.png')
    b.close()
