#!/usr/bin/env python3
"""Check external course links conservatively; a live URL is not source validation.

This checks the external HTTP(S) links in course.html and generated source pages.
It classifies access restrictions separately from missing resources so that a
publisher's bot policy is not reported as a broken citation. The checker never
follows a link's content or judges whether it supports the surrounding claim.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen
import argparse
import socket


ROOT = Path(__file__).resolve().parent.parent
USER_AGENT = 'ConferenceCourseLinkCheck/1.0 (+local static-course audit)'
RESTRICTED = {401, 403, 405, 429}
MISSING = {404, 410}


class ExternalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        href = attrs.get('href') if tag == 'a' else None
        if href and urlsplit(href).scheme in {'http', 'https'}:
            self.links.append(href)


def canonical_url(url):
    split = urlsplit(url)
    return urlunsplit((split.scheme, split.netloc, split.path, split.query, ''))


def collect_urls(course_only):
    files = [ROOT / 'course.html']
    if not course_only:
        files.extend(sorted((ROOT / 'course-sources').rglob('*.html')))
    occurrences = 0
    urls = set()
    for path in files:
        parser = ExternalLinks()
        parser.feed(path.read_text())
        occurrences += len(parser.links)
        urls.update(canonical_url(url) for url in parser.links)
    return files, occurrences, sorted(urls)


def fetch(url, timeout):
    request = Request(url, method='HEAD', headers={'User-Agent': USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            return 'ok', response.status, response.geturl()
    except HTTPError as error:
        if error.code == 405:
            # A range request avoids downloading a large paper merely to test it.
            request = Request(url, headers={'User-Agent': USER_AGENT, 'Range': 'bytes=0-0'})
            try:
                with urlopen(request, timeout=timeout) as response:
                    return 'ok', response.status, response.geturl()
            except HTTPError as retry_error:
                error = retry_error
            except (URLError, TimeoutError, socket.timeout) as retry_error:
                return 'error', str(retry_error), url
        if error.code in RESTRICTED:
            return 'restricted', error.code, url
        if error.code in MISSING:
            return 'missing', error.code, url
        return 'http-error', error.code, url
    except (URLError, TimeoutError, socket.timeout) as error:
        return 'error', str(error), url


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--course-only', action='store_true', help='Skip generated source pages.')
    parser.add_argument('--timeout', type=float, default=15, help='Per-request timeout in seconds.')
    parser.add_argument('--workers', type=int, default=6, help='Concurrent requests (default: 6).')
    parser.add_argument('--allow-restricted', action='store_true', help='Do not fail for 401/403/405/429 responses.')
    args = parser.parse_args()
    if args.timeout <= 0 or args.workers <= 0:
        parser.error('--timeout and --workers must be positive')

    files, occurrences, urls = collect_urls(args.course_only)
    print(f'Checking {len(urls)} unique external URLs from {len(files)} files ({occurrences} link occurrences).')
    outcomes = {}
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(fetch, url, args.timeout): url for url in urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                outcomes[url] = future.result()
            except Exception as error:  # A checker failure should name the URL.
                outcomes[url] = ('error', repr(error), url)

    grouped = {}
    for url, outcome in outcomes.items():
        grouped.setdefault(outcome[0], []).append((url, outcome[1], outcome[2]))
    for status in ('ok', 'restricted', 'missing', 'http-error', 'error'):
        entries = sorted(grouped.get(status, []))
        print(f'{status}: {len(entries)}')
        for url, detail, final_url in entries:
            if status != 'ok':
                print(f'  {detail}: {url}')

    failures = grouped.get('missing', []) + grouped.get('http-error', []) + grouped.get('error', [])
    if failures or (grouped.get('restricted') and not args.allow_restricted):
        raise SystemExit(1)
    print('No missing, other HTTP-error, or network-error external links detected.')


if __name__ == '__main__':
    main()
