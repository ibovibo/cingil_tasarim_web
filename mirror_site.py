import os
import re
import sys
from urllib.parse import urljoin, urlparse, parse_qs, unquote
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://www.cingiltasarim.com/'
OUTPUT_DIR = r'c:\Users\Asus\Desktop\cingilweb_full'
MAX_PAGES = 300

session = requests.Session()
visited = set()
queue = [BASE_URL]

os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_binary(url, local_path):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    try:
        r = session.get(url, stream=True, timeout=20)
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print('Failed to save', url, e)
        return False


def url_to_path(url):
    parsed = urlparse(url)
    path = parsed.path
    if path.endswith('/') or path == '':
        path = path + 'index.html'
    local = os.path.join(OUTPUT_DIR, parsed.netloc, path.lstrip('/'))
    if not os.path.splitext(local)[1]:
        local = local + '.html'
    return local


def sanitize_and_save_text(url, text, local_path):
    # replace original site name and phone with new ones
    text = text.replace('Cingil Tasarim', 'Cingil Tasarim')
    text = text.replace('CINGIL TASARIM', 'CINGIL TASARIM')
    text = text.replace('cingiltasarim', 'cingiltasarim')
    # phone replacements (common formats)
    text = text.replace('905434818591', '905434818591')
    text = text.replace('+905434818591', '+905434818591')
    text = text.replace('05434818591', '05434818591')
    text = text.replace('05434818591', '05434818591')
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, 'w', encoding='utf-8') as f:
        f.write(text)


def download_css_assets(css_url, local_css_path):
    try:
        r = session.get(css_url, timeout=20)
        r.raise_for_status()
        css_text = r.text
        # find url('...') or url("...") or url(...)
        for m in re.findall(r"url\(['\"]?(.*?)['\"]?\)", css_text):
            raw = m.strip()
            if raw.startswith('data:'):
                continue
            asset_url = urljoin(css_url, raw)
            local_asset = url_to_path(asset_url)
            save_binary(asset_url, local_asset)
            rel = os.path.relpath(local_asset, os.path.dirname(local_css_path)).replace('\\', '/')
            css_text = css_text.replace(m, rel)
        sanitize_and_save_text(css_url, css_text, local_css_path)
    except Exception as e:
        print('Failed css', css_url, e)


count = 0
while queue and count < MAX_PAGES:
    url = queue.pop(0)
    if url in visited:
        continue
    visited.add(url)
    print('Crawling', url)
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        content_type = r.headers.get('Content-Type','')
        if 'text/html' not in content_type:
            # save binary
            localp = url_to_path(url)
            save_binary(url, localp)
            continue
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        # rewrite and download assets
        # CSS
        for link in soup.find_all('link', href=True):
            href = link['href']
            full = urljoin(url, href)
            parsed = urlparse(full)
            if parsed.netloc and parsed.netloc != urlparse(BASE_URL).netloc:
                continue
            localp = url_to_path(full)
            download_css_assets(full, localp)
            rel = os.path.relpath(localp, os.path.dirname(url_to_path(url))).replace('\\', '/')
            link['href'] = rel
        # scripts
        for script in soup.find_all('script', src=True):
            src = script['src']
            full = urljoin(url, src)
            parsed = urlparse(full)
            if parsed.netloc and parsed.netloc != urlparse(BASE_URL).netloc:
                continue
            localp = url_to_path(full)
            save_binary(full, localp)
            rel = os.path.relpath(localp, os.path.dirname(url_to_path(url))).replace('\\', '/')
            script['src'] = rel
        # images and sources
        for img in soup.find_all(['img','source'], src=True):
            src = img['src']
            full = urljoin(url, src)
            parsed = urlparse(full)
            # handle Next.js _next/image proxy endpoints
            if parsed.path.startswith('/_next/image'):
                qs = parse_qs(parsed.query)
                if 'url' in qs:
                    orig = unquote(qs['url'][0])
                    full = urljoin(BASE_URL, orig)
                    parsed = urlparse(full)
            if parsed.netloc and parsed.netloc != urlparse(BASE_URL).netloc:
                continue
            localp = url_to_path(full)
            save_binary(full, localp)
            rel = os.path.relpath(localp, os.path.dirname(url_to_path(url))).replace('\\', '/')
            img['src'] = rel
        # inline style background images
        for tag in soup.find_all(style=True):
            style = tag['style']
            for m in re.findall(r"url\(([^)]+)\)", style):
                raw = m.strip(' \"\'')
                full = urljoin(url, raw)
                localp = url_to_path(full)
                save_binary(full, localp)
                rel = os.path.relpath(localp, os.path.dirname(url_to_path(url))).replace('\\', '/')
                style = style.replace(m, '"'+rel+'"')
            tag['style'] = style
        # find same-domain links and queue
        for a in soup.find_all('a', href=True):
            href = a['href']
            full = urljoin(url, href)
            parsed = urlparse(full)
            if parsed.netloc == urlparse(BASE_URL).netloc:
                if full not in visited and full not in queue:
                    queue.append(full)
        # write modified HTML
        local_html = url_to_path(url)
        sanitize_and_save_text(url, str(soup), local_html)
        count += 1
    except Exception as e:
        print('Error fetching', url, e)

print('Done. Saved to', OUTPUT_DIR)
