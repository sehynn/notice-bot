import requests

from .config import SLACK_WEBHOOK_URL


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


def send_no_updates():
    resp = requests.post(SLACK_WEBHOOK_URL, json={'text': '오늘은 업데이트가 없어요 🙂'}, timeout=10)
    resp.raise_for_status()
