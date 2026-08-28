# 세종대 공지 봇 — Claude 작업 규칙

## 브랜치 전략

```
production   ← 실제 서비스. 절대 직접 푸시 금지.
└── test     ← 검증용. push 시 GitHub Actions 즉시 실행 → 테스트 슬랙 채널
    └── feature/xxx  ← 기능 개발 단위 브랜치
```

**흐름:** `feature/xxx` → `test` (검증) → `production` (배포)

### 절대 하면 안 되는 것
- `production`에 직접 커밋/푸시
- `feature` 브랜치를 `test` 검증 없이 `production`에 머지
- `state.json`을 수동으로 커밋 (GitHub Actions가 자동 관리)

---

## 슬랙 채널

| 브랜치 | Secret | 채널 |
|--------|--------|------|
| `production` | `SLACK_WEBHOOK_URL` | 실제 사용자 채널 |
| `test` | `SLACK_WEBHOOK_URL_TEST` | 비공개 테스트 채널 |

---

## 프로젝트 구조

```
bot/
├── config.py     # BOARDS, HEADERS 상수
├── fetchers.py   # 파서 4개 + fetch() 진입점
├── slack.py      # 슬랙 전송
└── state.py      # state.json 로드/저장
main.py           # 오케스트레이션 진입점
state.json        # GitHub Actions가 자동 커밋 — 수동 수정 시 주의
```

---

## 커밋 컨벤션

```
feat:  새 기능
fix:   버그 수정
chore: 설정, 구조, 의존성 변경
```

---

## PR 작성

이 프로젝트는 전 과정을 Claude가 구현한다. PR 제목·본문을 올리거나 수정하기 전에 `humanize-korean` 스킬(`/humanize-korean` 또는 `/humanize`)로 한 번 윤문한다.

- 설치: `~/projects/im-not-ai` 클론 + `./install.sh --claude-only` (심링크, 새 세션부터 슬래시 커맨드 인식)
- 이 저장소의 PR은 버그 리포트 성격이라 라이트 경로가 기본. 코드·수치·커밋 해시·검증 결과 등 내용은 절대 건드리지 않고, 볼드·이모지 남발 같은 장식만 정리한다.
- 이미 자연스럽게 쓴 글이면 스킵해도 됨 — 강제 규칙이 아니라 기본값.

---

## GitHub Actions 스케줄

- `production` 브랜치 기준 매일 **오후 1시, 오후 6시 KST** 실행
- `test` 브랜치는 **push 즉시** 실행
