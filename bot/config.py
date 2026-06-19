import os

SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

STATE_FILE = 'state.json'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
}

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
