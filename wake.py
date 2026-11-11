import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

WAKE_BUTTON = re.compile("get this app back up", re.I)

apps = [
    line.strip()
    for line in Path("apps.txt").read_text().splitlines()
    if line.strip() and not line.strip().startswith("#")
]

failed = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    for url in apps:
        page = browser.new_page()
        try:
            page.goto(url, timeout=120000, wait_until="domcontentloaded")
            page.wait_for_timeout(10000)
            button = page.get_by_role("button", name=WAKE_BUTTON)
            if button.count() > 0:
                button.first.click()
                page.wait_for_timeout(60000)
                if page.get_by_role("button", name=WAKE_BUTTON).count() > 0:
                    print(f"STILL ASLEEP: {url}")
                    failed.append(url)
                else:
                    print(f"WOKE UP: {url}")
            else:
                print(f"ALREADY AWAKE: {url}")
        except Exception as error:
            print(f"ERROR: {url} - {error}")
            failed.append(url)
        finally:
            page.close()
    browser.close()

print(f"Checked {len(apps)} app(s), {len(failed)} problem(s).")
if failed:
    sys.exit(1)
