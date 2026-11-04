"""카카오톡 대화 내보내기(Mac CSV) 파일을 pandas DataFrame으로 변환하는 모듈.

Mac 카톡 CSV 형식: Date,User,Message (UTF-8 BOM)
  - 사진/동영상/이모티콘 등은 "사진", "사진 3장", "이모티콘" 같은 고정 문자열로 기록됨
  - "메시지가 삭제되었습니다." 행은 Date/User가 비어 있음
  - 그 외 User가 빈 행은 시스템 메시지 ("Chat Loss", 초대 알림 등)
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]

_PHOTO = re.compile(r"^사진(?: (\d+)장)?$")
_SYSTEM = re.compile(r"(초대했습니다|나갔습니다|내보냈습니다|들어왔습니다)\.?$")


def classify(message: str, user: str) -> str:
    """메시지 종류를 분류한다."""
    if message == "메시지가 삭제되었습니다.":
        return "deleted"
    if not user or _SYSTEM.search(message):
        return "system"
    if _PHOTO.match(message):
        return "photo"
    if message == "동영상":
        return "video"
    if message == "이모티콘":
        return "emoticon"
    if message.startswith("파일: "):
        return "file"
    if message in ("보이스톡", "페이스톡") or message.startswith(("보이스톡 ", "페이스톡 ")):
        return "call"
    if message.startswith("샵검색 : "):
        return "search"
    if re.match(r"^https?://\S+$", message):
        return "link"
    return "text"


def photo_count(message: str) -> int:
    m = _PHOTO.match(message)
    if not m:
        return 0
    return int(m.group(1) or 1)


def parse_chat(path: str | Path) -> pd.DataFrame:
    """카톡 CSV를 읽어 분석용 DataFrame을 반환한다.

    컬럼: datetime, date, hour, weekday, user, message, type, photos, length, kk
    """
    df = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    df = df.rename(columns={"Date": "datetime", "User": "user", "Message": "message"})

    # "메시지가 삭제되었습니다." 행은 날짜가 비어 있어서 바로 앞 메시지 시간으로 채운다
    df["datetime"] = pd.to_datetime(
        df["datetime"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
    ).ffill()
    df["date"] = df["datetime"].dt.date
    df["hour"] = df["datetime"].dt.hour
    df["weekday"] = pd.Categorical(
        df["datetime"].dt.dayofweek.map(lambda i: WEEKDAYS[i]),
        categories=WEEKDAYS, ordered=True,
    )
    df["type"] = [classify(m, u) for m, u in zip(df["message"], df["user"])]
    df["photos"] = df["message"].map(photo_count)
    is_text = df["type"] == "text"
    df["length"] = df["message"].str.len().where(is_text, 0)
    df["kk"] = df["message"].str.count("ㅋ").where(is_text, 0)
    return df


def load_latest(data_dir: str | Path = "data") -> pd.DataFrame:
    """data/ 폴더에서 가장 최근 카톡 CSV를 불러온다."""
    files = sorted(Path(data_dir).glob("KakaoTalk_Chat_*.csv"))
    if not files:
        raise FileNotFoundError(f"{data_dir}/ 에 KakaoTalk_Chat_*.csv 파일이 없어요.")
    return parse_chat(files[-1])


def basic_stats(df: pd.DataFrame) -> pd.DataFrame:
    """사람별 기본 통계표."""
    people = df[~df["type"].isin(["system", "deleted"])]
    stats = people.groupby("user").agg(
        messages=("message", "size"),
        photos=("photos", "sum"),
        emoticons=("type", lambda s: (s == "emoticon").sum()),
        kk=("kk", "sum"),
        avg_length=("length", lambda s: s[s > 0].mean()),
    )
    stats["share_%"] = (stats["messages"] / stats["messages"].sum() * 100).round(1)
    stats["avg_length"] = stats["avg_length"].round(1)
    return stats.sort_values("messages", ascending=False)


if __name__ == "__main__":
    df = load_latest()
    print(f"기간: {df['datetime'].min():%Y-%m-%d} ~ {df['datetime'].max():%Y-%m-%d}")
    print(f"전체 메시지: {len(df):,}개\n")
    print("메시지 종류:\n", df["type"].value_counts().to_string(), "\n")
    print("사람별 통계:\n", basic_stats(df).to_string())
