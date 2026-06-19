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
    {'name': '세종뉴스룸', 'url': 'https://pr.sejong.ac.kr/news/today/sejong-prism.do?mode=list&articleLimit=10&article.offset=0', 'emoji': '📰', 'parser': 'pr'},
    {'name': 'ICT글로벌', 'url': 'https://global.ictintern.or.kr/board/noticeList.do', 'emoji': '🌐', 'parser': 'ict', 'prefix': ''},
    {'name': '국립국제교육원', 'url': 'https://www.niied.go.kr/web/main/nid/niied_board/list?cp=1&sortOrder=BA_REGDATE&sortDirection=DESC&bcId=niied_board&baNotice=false&baCommSelec=false&baOpenDay=false&baUse=true', 'emoji': '🎓', 'parser': 'niied', 'prefix': ''},
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

        notices.append({
            'id': article_id,
            'title': title,
            'date': date,
            'url': full_url,
        })

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

        notices.append({
            'id': article_id,
            'title': title,
            'date': date,
            'url': full_url,
        })

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

        notices.append({
            'id': num_text,
            'title': title,
            'date': date,
            'url': board_url,
        })

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

        notices.append({
            'id': article_id,
            'title': title,
            'date': date,
            'url': full_url,
        })

    return notices


def send_slack(board_name, emoji, new_notices, prefix='세종대 '):
    blocks = [
        {
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': f'{emoji} {prefix}{board_name} 새 공지 {len(new_notices)}건',
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


def send_test():
    resp = requests.post(SLACK_WEBHOOK_URL, json={
        'text': '✅ 세종대 공지 봇 연결 테스트 성공!'
    }, timeout=10)
    resp.raise_for_status()
    print('Test message sent.')


def main():
    if not SLACK_WEBHOOK_URL:
        print('Error: SLACK_WEBHOOK_URL not set', file=sys.stderr)
        sys.exit(1)

    if '--test' in sys.argv:
        send_test()
        return

    state = load_state()
    is_first_run = len(state) == 0

    if is_first_run:
        print('First run — saving current state, no notifications sent')

    has_new = False

    for board in BOARDS:
        name = board['name']
        print(f'Checking {name}...', end=' ', flush=True)

        try:
            if board.get('parser') == 'pr':
                notices = fetch_pr_notices(board['url'])
            elif board.get('parser') == 'ict':
                notices = fetch_ict_notices(board['url'])
            elif board.get('parser') == 'niied':
                notices = fetch_niied_notices(board['url'])
            else:
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
                send_slack(name, board['emoji'], new_notices, board.get('prefix', '세종대 '))
                has_new = True
            else:
                print('no new')
        else:
            print(f'{len(notices)} notices saved')

        state[name] = list(seen_ids | current_ids)
        time.sleep(1)

    if not is_first_run and not has_new:
        requests.post(SLACK_WEBHOOK_URL, json={'text': '오늘은 업데이트가 없어요 🙂'}, timeout=10)

    save_state(state)
    print('Done.')


if __name__ == '__main__':
    main()
