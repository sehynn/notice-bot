import re

import requests
from bs4 import BeautifulSoup

from .config import HEADERS


def fetch_notices(board_url):
    resp = requests.get(board_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    notices = []
    for row in soup.select('table tbody tr'):
        cols = row.find_all('td')
        if len(cols) < 4:
            continue

        link_tag = cols[1].find('a')
        if not link_tag:
            continue

        title = link_tag.get_text(strip=True)
        href = link_tag.get('href', '')

        match = re.search(r'articleNo=(\d+)', href)
        if not match:
            continue
        article_id = match.group(1)

        base = board_url.split('?')[0]
        full_url = base + href if href.startswith('?') else href
        date = cols[3].get_text(strip=True)

        notices.append({'id': article_id, 'title': title, 'date': date, 'url': full_url})

    return notices


def fetch_pr_notices(board_url):
    resp = requests.get(board_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    notices = []
    seen_ids = set()
    for tag in soup.find_all('a', href=True):
        href = tag.get('href', '')
        match = re.search(r'articleNo=(\d+)', href)
        if not match:
            continue
        article_id = match.group(1)
        if article_id in seen_ids:
            continue
        seen_ids.add(article_id)

        title = tag.get_text(strip=True)
        if not title:
            continue

        base = board_url.split('?')[0]
        full_url = base + href if href.startswith('?') else href

        parent_text = tag.parent.get_text(' ', strip=True) if tag.parent else ''
        date_match = re.search(r'(\d{4}\.\d{2}\.\d{2})', parent_text)
        date = date_match.group(1) if date_match else ''

        notices.append({'id': article_id, 'title': title, 'date': date, 'url': full_url})

    return notices


def fetch_ict_notices(board_url):
    resp = requests.get(board_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    notices = []
    for row in soup.select('table tbody tr'):
        cols = row.find_all('td')
        if len(cols) < 4:
            continue

        num_text = cols[0].get_text(strip=True)
        if not num_text.isdigit():
            continue

        title = cols[2].get_text(strip=True)
        date = cols[-1].get_text(strip=True)

        notices.append({'id': num_text, 'title': title, 'date': date, 'url': board_url})

    return notices


def fetch_niied_notices(board_url):
    resp = requests.get(board_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    notices = []
    for row in soup.select('table tbody tr'):
        cols = row.find_all('td')
        if len(cols) < 3:
            continue

        num_text = cols[0].get_text(strip=True)
        if not num_text.isdigit():
            continue

        link_tag = cols[2].find('a') or cols[1].find('a')
        if not link_tag:
            continue

        title = link_tag.get_text(strip=True)
        href = link_tag.get('href', '')

        match = re.search(r'/niied_board/(\d+)', href)
        if not match:
            continue
        article_id = match.group(1)

        full_url = f'https://www.niied.go.kr{href}' if href.startswith('/') else href
        date = cols[-2].get_text(strip=True)

        notices.append({'id': article_id, 'title': title, 'date': date, 'url': full_url})

    return notices


PARSER_MAP = {
    'pr': fetch_pr_notices,
    'ict': fetch_ict_notices,
    'niied': fetch_niied_notices,
}


def fetch(board):
    parser = PARSER_MAP.get(board.get('parser'), fetch_notices)
    return parser(board['url'])
