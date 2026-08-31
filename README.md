# 📢 공지 다모아 알리미

- 여러 사이트에 흩어진 학사·학과·장학·취업·공모전·인턴십 공지를 일일이 확인하기 번거로우셨나요?
- 관심 있는 공지를 마감 기한이 지난 뒤에야 발견한 적이 있으신가요?


공지 알리미는 여러 공지 게시판을 매일 두 번 확인하고, 새로운 글이 등록되면 슬랙으로 알려주는 봇입니다.

이제 슬랙 채널 하나만 확인하세요! 



[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Notice Checker](https://github.com/sehynn/notice-bot/actions/workflows/check-notices.yml/badge.svg)](https://github.com/sehynn/notice-bot/actions/workflows/check-notices.yml)


</br>
</br> 
</br>
 
## 어떻게 동작하나요?

별도의 서버나 데이터베이스 없이, **GitHub Actions 크론과 Git 커밋만으로 상태를 관리합니다.**

```text
GitHub Actions 실행 (매일 오후 1시·6시 KST)
        │
        ▼
게시판 19곳 크롤링
(requests + BeautifulSoup)
        │
        ▼
이전에 확인한 글 ID(state.json)와 비교
        │
        ├─ 새 글 있음 → Slack Webhook으로 알림 전송
        │
        ▼
state.json 갱신 → 저장소에 커밋 및 푸시
```

</br>
</br> 
</br>


### 왜 서버 없이 만들었나요?

해당 레포지토리의 크롤링 작업은 하루 두 번, 몇 초 동안 실행됩니다. 
이 작업을 위해 별도의 VPS나 클라우드 인스턴스를 구축하고 관리하는 것은 낭비라고 생각했습니다.

Github Actions를 통해 확인한 게시글의 ID만 관리하면 별도의 DB 없이 구축이 가능하다고 판단했습니다. state.json에 상태를 저장하고 실행이 끝날 때마다 파일을 저장소에 커밋하도록 하여, 서버 비용과 유지보수 부담을 최소화하면서 지속적으로 동작하게끔 만들었습니다. 

</br>
</br> 
</br>

## 지원하는 게시판

현재 총 **19개 게시판**을 확인합니다.

| 분류      | 게시판                                                   |
| ------- | ----------------------------------------------------- |
| 학교 공지   | 공지사항, 학사공지, 취업, 장학, 채용·모집, 국제교류                       |
| 학과 공지   | 컴퓨터공학과(학부·취업뉴스·공모전), AI·데이터사이언스학과, 소프트웨어학과, SW중심대학사업단 |
| 학교 소식   | 세종뉴스룸                                                 |
| 외부 프로그램 | ICT 글로벌 인턴십, 국립국제교육원, 월드잡(해외인턴십·공모전), 위비티, 한국장학재단     |

- 사이트마다 게시판의 HTML 구조가 다르기 때문에 구조별로 파서를 분리해 관리합니다. 게시판별 파서 연결 정보는 `bot/fetchers.py`의 `PARSER_MAP`에서 확인할 수 있습니다.

- 새로운 사이트를 연동하려면 해당 구조에 맞는 파서 함수와 게시판 설정을 추가하면 됩니다.


</br>
</br> 
</br>
  

## 트러블슈팅

<details>
<summary><strong>1. 구형 서버와 Python 간 SSL Handshake 실패</strong></summary>

<br>

### 문제

`sw.sejong.ac.kr`, `dept.sejong.ac.kr`, `pr.sejong.ac.kr`에서 `SSLV3_ALERT_HANDSHAKE_FAILURE`가 발생했습니다. 로컬 macOS와 GitHub Actions Ubuntu에서 동일하게 재현돼, 특정 실행 환경의 문제가 아님을 확인했습니다.

### 원인

`curl -v`로 확인한 결과 세 서버는 구형 Cipher Suite인 `AES256-SHA`를 사용하고 있었습니다. 반면 Python 기본 SSL Context의 Cipher Suite 목록에는 `AES256-SHA`가 없어, 서버와 클라이언트가 공통으로 사용할 수 있는 Cipher Suite가 없었습니다.

### 해결

다음 세 가지 방법을 비교했습니다.

| 방법                        | 결과                        |
| ------------------------- | ------------------------- |
| `SECLEVEL=1`로 보안 수준 하향    | 연결은 성공하지만 불필요한 구형 설정까지 허용 |
| `ECDHE-RSA-AES256-SHA` 사용 | 서버가 ECDHE를 지원하지 않아 실패     |
| 기본 목록에 `AES256-SHA`만 추가   | 연결 성공, 최종 채택              |

전체 보안 수준을 낮추는 대신 Python 기본 Cipher Suite 목록에 `AES256-SHA`만 추가했습니다.

```python
context = ssl.create_default_context()
context.set_ciphers("DEFAULT:AES256-SHA")
```

다만 현재 Adapter가 `https://` 단위로 마운트돼 공유 세션의 모든 HTTPS 요청에 적용됩니다. 허용하는 Cipher Suite의 범위는 최소화했지만, 적용 대상을 세 호스트로 제한하는 작업은 후속 과제로 남아 있습니다.

</details>

<details>
<summary><strong>2. 신규 게시판 추가 시 과거 공지가 모두 발송되는 문제</strong></summary>

<br>

### 문제

운영 중 새로운 게시판을 추가하자, 해당 게시판의 과거 공지 수십 건이 모두 새 글로 인식돼 Slack으로 발송됐습니다.

### 원인

기존에는 `state.json` 전체가 비어 있는지를 기준으로 첫 실행 여부를 판단했습니다.

```python
is_first_run = not bool(state)
```

하지만 실제 상태는 게시판별로 독립적으로 존재합니다. 봇 전체가 처음 실행되는 경우와 운영 중 특정 게시판을 처음 수집하는 경우를 전역 플래그 하나로 구분할 수 없었던 것이 원인이었습니다.

### 해결

최초 수집 여부의 판단 단위를 애플리케이션 전체에서 게시판 단위로 변경했습니다.

```python
is_first_fetch = board_key not in state
```

처음 수집하는 게시판은 기존 글 ID를 baseline으로 저장하고 알림을 보내지 않습니다. 이후 실행부터 이전 상태와 비교해 새롭게 추가된 글만 전송합니다.

이를 통해 운영 중 게시판을 추가하더라도 기존 공지가 한꺼번에 발송되지 않고, 추가 이후 등록된 글부터 알림이 전송되도록 변경했습니다.

</details>




</br>
</br> 
</br>



## Slack 알림 예시

```text
📢 세종대 공지사항 새 공지 2건
──────────────────
[2026학년도 2학기 수강신청 안내]
2026.08.30

[중앙도서관 하계 휴관 안내]
2026.08.29
```

새로운 글이 없는 날에는 다음과 같이 알려줍니다.

```text
오늘은 업데이트가 없어요 🙂
```



</br>
</br> 
</br>

## 직접 사용해보기

### 알림만 받고 싶다면

[Slack 채널 참여하기](https://join.slack.com/t/w1781685939-hgd391754/shared_invite/zt-418rd8vxt-OJMWh8PpRJYBQh14UtppFw)

### 다른 학교나 조직에 적용하고 싶다면

```bash
git clone https://github.com/sehynn/notice-bot.git
cd notice-bot
pip install -r requirements.txt
```

1. `bot/config.py`의 `BOARDS`에 게시판을 추가합니다.
2. 게시판 구조가 기존과 다르면 `bot/fetchers.py`에 새로운 파서를 추가합니다.
3. Slack Incoming Webhook을 생성하고 `SLACK_WEBHOOK_URL` 환경변수를 등록합니다.
4. `python main.py --test`를 실행해 연결 상태를 확인합니다.
5. GitHub Actions를 사용하려면 저장소 Secrets에 `SLACK_WEBHOOK_URL`을 등록하고, `.github/workflows/check-notices.yml`에서 실행 시간을 조정합니다.

