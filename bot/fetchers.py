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


def fetch_cedpt_intro_notices(board_url):
    """cedpt/intro/ 게시판 — 4열(번호/제목/등록일/조회수), 날짜가 cols[2]."""
    resp = requests.get(board_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    notices = []
    for row in soup.select('table tbody tr'):
        cols = row.find_all('td')
        if len(cols) < 3:
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
        date = cols[2].get_text(strip=True)

        notices.append({'id': article_id, 'title': title, 'date': date, 'url': full_url})

    return notices


def fetch_dept5_notices(board_url):
    """5열(번호/분류/제목/등록일/조회수) 학과 게시판 — 제목 cols[2], 날짜 cols[3]."""
    resp = requests.get(board_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    notices = []
    for row in soup.select('table tbody tr'):
        cols = row.find_all('td')
        if len(cols) < 4:
            continue

        link_tag = cols[2].find('a')
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


def fetch_worldjob_notices(board_url):
    """worldjob.or.kr — a.bbs-list-item 구조, bbscttNo를 ID로 사용."""
    resp = requests.get(board_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    notices = []
    for item in soup.select('div.bbs-list-type a.bbs-list-item:not(.item-fixed)'):
        title_tag = item.select_one('h2.bbs-list--tit')
        date_tag = item.select_one('span.bbs-list--date')
        href = item.get('href', '')

        if not title_tag:
            continue

        match = re.search(r'bbscttNo=(\d+)', href)
        if not match:
            continue
        article_id = match.group(1)

        title = title_tag.get_text(strip=True)
        date = date_tag.get_text(strip=True) if date_tag else ''
        full_url = 'https://www.worldjob.or.kr' + href if href.startswith('/') else href

        notices.append({'id': article_id, 'title': title, 'date': date, 'url': full_url})

    return notices


def fetch_wevity_notices(board_url):
    """wevity.com 공모전 — ul.list li 구조, ix를 ID로 사용. 날짜 대신 D-day 표시."""
    resp = requests.get(board_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    notices = []
    base = board_url.split('?')[0]
    for li in soup.select('div.ms-list ul.list li'):
        if 'top' in li.get('class', []):
            continue

        a_tag = li.select_one('div.tit a')
        if not a_tag:
            continue

        href = a_tag.get('href', '')
        match = re.search(r'ix=(\d+)', href)
        if not match:
            continue
        article_id = match.group(1)

        title = a_tag.get_text(strip=True)
        full_url = base + href if href.startswith('?') else href

        day_tag = li.select_one('div.day')
        date = re.sub(r'\s+', ' ', day_tag.get_text(strip=True)) if day_tag else ''

        notices.append({'id': article_id, 'title': title, 'date': date, 'url': full_url})

    return notices


PARSER_MAP = {
    'pr': fetch_pr_notices,
    'ict': fetch_ict_notices,
    'niied': fetch_niied_notices,
    'cedpt_intro': fetch_cedpt_intro_notices,
    'dept5': fetch_dept5_notices,
    'worldjob': fetch_worldjob_notices,
    'wevity': fetch_wevity_notices,
}


def fetch(board):
    parser = PARSER_MAP.get(board.get('parser'), fetch_notices)
    return parser(board['url'])
