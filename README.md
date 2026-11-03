# 💬 kakao-chat-report

카카오톡 단톡방 대화를 분석해서 **"우리 단톡방 연말결산"** 리포트를 만들어 주는 프로젝트입니다.

## 주요 기능 (예정)
- 사람별 메시지 수 / 날짜별 대화량
- 시간대·요일별 활동 히트맵
- 자주 쓰는 단어 워드클라우드
- ㅋ 개수, 사진·이모티콘 수, 평균 답장 속도
- 멤버별 칭호 (수다왕, 올빼미 등)
- Streamlit 웹 대시보드

## 기술 스택
Python · pandas · matplotlib / plotly · kiwipiepy · wordcloud · Streamlit

## 실행 방법
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 프로젝트 구조
```
kakao-chat-report/
├── data/           # 개인 대화 파일 (Git 제외)
├── src/
│   └── parser.py   # 카톡 txt → DataFrame
├── app.py          # Streamlit 앱
└── requirements.txt
```

## 개인정보 보호
실제 대화 데이터는 개인정보 보호를 위해 저장소에 포함하지 않습니다.
`data/` 폴더에 직접 내보낸 대화 파일을 넣어 사용하세요.
