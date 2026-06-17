import requests
from bs4 import BeautifulSoup
import json
import os
import re
import sys
import time

SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

BOARDS = [
    {'name': '공지사항',  'url': 'https://www.sejong.ac.kr/kor/intro/notice1.do', 'emoji': '📢'},
    {'name': '학사공지',  'url': 'https://www.sejong.ac.kr/kor/intro/notice3.do', 'emoji': '📚'},
    {'name': '국제교류',  'url': 'https://www.sejong.ac.kr/kor/intro/notice4.do', 'emoji': '🌏'},
    {'name': '취업',     'url': 'https://www.sejong.ac.kr/kor/intro/notice6.do', 'emoji': '💼'},
    {'name': '장학',     'url': 'https://www.sejong.ac.kr/kor/intro/notice7.do', 'emoji': '💰'},
    {'name': '채용/모집', 'url': 'https://www.sejong.ac.kr/kor/intro/notice8.do', 'emoji': '📋'},
    {'name': '컴공 학부',  'url': 'https://dept.sejong.ac.kr/cedpt/board/notice.do', 'emoji': '💻'},
    {'name': 'SW중심대학', 'url': 'https://sw.sejong.ac.kr/sw/notice.do', 'emoji': '🖥️'},
]

STATE_FILE = 'state.json'
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
}


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def fetch_notices(board_url):
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
            continue  # skip pinned rows

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

        notices.append({
            'id': article_id,
            'title': title,
            'date': date,
            'url': full_url,
        })

    return notices


def send_slack(board_name, emoji, new_notices):
    blocks = [
        {
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': f'{emoji} 세종대 {board_name} 새 공지 {len(new_notices)}건',
                'emoji': True,
            },
        },
        {'type': 'divider'},
    ]

    for notice in new_notices:
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'*<{notice["url"]}|{notice["title"]}>*\n`{notice["date"]}`',
            },
        })

    resp = requests.post(SLACK_WEBHOOK_URL, json={'blocks': blocks}, timeout=10)
    resp.raise_for_status()


def main():
    if not SLACK_WEBHOOK_URL:
        print('Error: SLACK_WEBHOOK_URL not set', file=sys.stderr)
        sys.exit(1)

    state = load_state()
    is_first_run = len(state) == 0

    if is_first_run:
        print('First run — saving current state, no notifications sent')

    for board in BOARDS:
        name = board['name']
        print(f'Checking {name}...', end=' ', flush=True)

        try:
            notices = fetch_notices(board['url'])
        except Exception as e:
            print(f'ERROR: {e}')
            continue

        current_ids = {n['id'] for n in notices}
        seen_ids = set(state.get(name, []))

        if not is_first_run:
            new_notices = [n for n in notices if n['id'] not in seen_ids]
            if new_notices:
                print(f'{len(new_notices)} new')
                send_slack(name, board['emoji'], new_notices)
            else:
                print('no new')
        else:
            print(f'{len(notices)} notices saved')

        state[name] = list(seen_ids | current_ids)
        time.sleep(1)

    save_state(state)
    print('Done.')


if __name__ == '__main__':
    main()
