#!/usr/bin/env python3
"""Optional browser QA (requires Playwright and an installed Chromium).

Not required to install/use the skill. No automatic downloads. HTML is loaded
with set_content to avoid managed file:// navigation restrictions.
"""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chromium', required=True, help='Existing Chromium executable')
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[1]
    html = (root / 'examples/venture-report-sample.html').read_text(encoding='utf-8')
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.chromium, headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':1440,'height':1060},device_scale_factor=1, reduced_motion='reduce')
        errors, console_errors, requests = [], [], []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: console_errors.append(m.text) if m.type == 'error' else None)
        page.on('request', lambda r: requests.append(r.url))
        page.set_content(html, wait_until='load')
        assert page.locator('html').evaluate('(el)=>el.classList.contains("js")')
        assert page.locator('h1').inner_text().startswith('사업 포트폴리오')
        results.append('Initial document and progressive enhancement')
        page.screenshot(path=str(args.output_dir/'cover-desktop.png'))
        page.locator('a[href="#scorecard"]').first.click()
        page.wait_for_timeout(100)
        assert page.locator('.toc a[href="#scorecard"]').get_attribute('aria-current') == 'location'
        page.screenshot(path=str(args.output_dir/'scorecard-desktop.png'))
        results.append('Table-of-contents navigation and active section')
        page.locator('[data-rating-view="current"]').click()
        assert page.locator('.scorecard').get_attribute('data-view') == 'current'
        assert not page.locator('.scorecard .conditional').first.is_visible()
        page.locator('[data-rating-view="conditional"]').click()
        assert page.locator('.scorecard .conditional').first.is_visible()
        results.append('Current / conditional rating toggle')
        assert not page.locator('details').first.get_attribute('open')
        page.locator('a[href="#criterion-workflow-a-sustainable"]').click()
        page.wait_for_timeout(150)
        assert page.locator('details').first.evaluate('(el)=>el.open')
        target = page.locator('#criterion-workflow-a-sustainable')
        assert target.is_visible()
        rect = target.bounding_box()
        assert rect and 0 <= rect['y'] < 1060, str(rect)
        results.append('Rating link reveals and scrolls to collapsed detailed evidence')
        page.locator('#expand-details').click()
        assert page.locator('details').evaluate_all('(els)=>els.every(e=>e.open)')
        page.locator('#expand-details').click()
        assert page.locator('details').evaluate_all('(els)=>els.every(e=>!e.open)')
        results.append('Expand and collapse every detailed scorecard')
        page.locator('.source-ref[href="#source-E1"]').first.click()
        page.wait_for_timeout(100)
        rect=page.locator('#source-E1').bounding_box()
        assert rect and 0 <= rect['y'] < 1060
        results.append('Source references navigate to the correct evidence')
        for section in ('analysis','redesign','budget'):
            page.locator(f'.toc a[href="#{section}"]').click()
            page.screenshot(path=str(args.output_dir/f'{section}-desktop.png'))
        for width in (1440,1024,768,390,320):
            page.set_viewport_size({'width':width,'height':844})
            page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
            assert page.evaluate('document.body.scrollWidth <= window.innerWidth'), f'body overflow at {width}'
            if width==390:
                page.screenshot(path=str(args.output_dir/'cover-mobile.png'))
            if width<=390:
                wrap=page.locator('#scorecard .table-wrap')
                assert wrap.evaluate('(el)=>el.scrollWidth>el.clientWidth')
        results.append('Responsive layout at 1440 / 1024 / 768 / 390 / 320 px, tables scroll internally')
        page.set_viewport_size({'width':794,'height':1123})
        page.evaluate('window.dispatchEvent(new Event("beforeprint"))')
        page.emulate_media(media='print')
        assert page.locator('.topbar').evaluate('(el)=>getComputedStyle(el).display') == 'none'
        assert page.locator('details').evaluate_all('(els)=>els.every(e=>e.open)')
        assert page.evaluate('document.body.scrollWidth <= window.innerWidth')
        page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
        page.screenshot(path=str(args.output_dir/'print-css-cover.png'))
        results.append('Print CSS hides controls, opens evidence, and fits the emulated width')
        page.emulate_media(media='screen')
        page.evaluate('window.dispatchEvent(new Event("afterprint"))')
        assert page.locator('details').evaluate_all('(els)=>els.every(e=>!e.open)')
        results.append('After-print detail state restored')
        nojs=browser.new_page(java_script_enabled=False,viewport={'width':1440,'height':1060})
        nojs.set_content(html)
        assert nojs.locator('h1').is_visible()
        assert nojs.locator('details').count()==3
        nojs.locator('details summary').first.click()
        assert nojs.locator('details').first.get_attribute('open') is not None
        assert nojs.locator('.scorecard .conditional').first.is_visible()
        results.append('No-JavaScript reading, rating arrows, and native details')
        assert not errors, errors
        assert not console_errors, console_errors
        assert not requests, requests
        results.append('Zero page errors, console errors, and external requests')
        version=browser.version
        browser.close()
    report={'browser':version,'loader':'Playwright set_content (managed file URL navigation is restricted)',
            'checks_passed':len(results),'checks':results,'errors':errors,'console_errors':console_errors,'requests':requests,
            'not_tested':['Actual Claude/Codex model execution','Safari/Firefox/Windows host behavior','Physical PDF pagination/export','Hosted deployment and remote access']}
    (args.output_dir/'browser-test-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
