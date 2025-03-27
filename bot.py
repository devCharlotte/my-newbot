import os
import discord
import asyncio
from datetime import datetime, timedelta

# GitHub Secrets에서 환경 변수 가져오기
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not TOKEN or not CHANNEL_ID:
    print(" [JoonHee-System]  오류: DISCORD_TOKEN 또는 CHANNEL_ID가 설정되지 않았음.")
    exit(1)

CHANNEL_ID = int(CHANNEL_ID)

# 디스코드 클라이언트 설정
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# ✅ 기본 알람 스케줄 (07:00 ~ 01:00 정상 작동)
ALARM_HOURS = list(range(7, 24)) + [0]  # 07:00 ~ 23:59 + 00:00 ~ 00:59 (새벽 1시 포함)
ALARM_MINUTES = {
    0: "⏰ {time} - 집중 시작!", 
    25: "⏰ {time} - 조금만 더 파이팅!", 
    50: "⏳ {time} - 이제 쉬자! 스트레칭하고 물 마시기!"
}

# ✅ 사용자 지정 알림 (요일별 특정 시간 추가 가능)
EXTRA_SCHEDULES = {
    "Monday": {
        7: "오늘은 월요일. 분산, 시스템보안, 개인정보보호법, 학원",
        8: "⏰ 분산시스템 (9시, 수203, 김규영 교수님)",
        9: "🕒 인턴십 일지 / 녹화 강의 / 랩미팅 준비",
        11: "⏰ 시스템보안 (12시, 프601, 김성민 교수님)",
        14: "⏰ 개인정보보호법 (3시, 성305, 홍준호 교수님)"
    },
    "Tuesday": {
        7: "오늘은 화요일. 산업보안법. 알찬 하루 보내기"
        8: "🕒 인턴십 일지 / 녹화 강의 / 랩미팅 준비"
    },
    "Wednesday": {
        7: "오늘은 수요일. 근무, 보안SW, 포렌식"
        8: "🕒 인턴십 일지 / 녹화 강의 / 랩미팅 준비",
        14: "⏰ 융합보안포렌식 (3시, 성211, 김학경 교수님)"
    },
    "Thursday": {
        7: "오늘은 목요일. 랩미팅, 보안개론"
        9: "🕒 인턴십 일지 / 녹화 강의 / 서구실 채점 / 랩미팅 준비",
        12: "⏰ 랩미팅 (1시)",
        14: "⏰ 융합보안개론 (3시, 성704, 김경진 교수님)"
    },
    "Friday": {
        7: "오늘은 금요일. 알찬 하루 보내기"
    }

}

# ✅ 메시지 전송 함수
async def send_message(channel, message):
    try:
        await channel.send(message)
        print(f" [JoonHee-System] 메시지 전송 완료: {message}")
    except discord.errors.Forbidden:
        print(" [JoonHee-System]  오류: 메시지 전송 권한이 없음 (Forbidden)")
    except discord.errors.HTTPException as e:
        print(f" [JoonHee-System]  오류: 메시지 전송 실패 - {e}")
    except Exception as e:
        print(f" [JoonHee-System]  알 수 없는 오류 발생: {e}")

# ✅ 알람 실행 함수 (07:00 ~ 01:00 동안 정상 작동)
async def send_notification():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print(f" [JoonHee-System]  오류: 채널 ID {CHANNEL_ID}을 찾을 수 없음.")
        return

    print(f" [JoonHee-System]  채널 확인 완료: {channel.name} (ID: {channel.id})")

    last_sent_minute = None  # 마지막으로 메시지를 보낸 분을 저장

    while True:
        now_utc = datetime.utcnow()  # 현재 UTC 시간
        now = now_utc + timedelta(hours=9)  # 한국 시간(KST) 변환
        weekday = now.strftime("%A")  # 요일 (Monday, Tuesday, ...)

        # AM/PM 형식으로 변환
        formatted_time = now.strftime("%I:%M %p").lstrip("0") 

        # 중복 전송 방지: 동일한 분(minute)에 메시지를 보낸 경우 다시 보내지 않음
        if now.minute != last_sent_minute:
            # ✅ 07:00 ~ 01:00 동안만 알림 전송
            if now.hour in ALARM_HOURS and now.minute in ALARM_MINUTES:
                alert_message = ALARM_MINUTES[now.minute].format(time=formatted_time)  # {time}을 현재 시각으로 대체
                await send_message(channel, alert_message)

            # ✅ 사용자 지정 알람 스케줄 (요일별 추가 알림) - 현재 시각 미포함
            if weekday in EXTRA_SCHEDULES and now.hour in EXTRA_SCHEDULES[weekday]:
                if now.minute == 45:  # 사용자 지정 알람은 45분에 울리도록 설정
                    class_message = EXTRA_SCHEDULES[weekday][now.hour]  # 현재 시각 생략
                    await send_message(channel, class_message)

            # 마지막 전송된 분 업데이트 (중복 방지)
            last_sent_minute = now.minute

        await asyncio.sleep(60)  # 60초마다 체크 (실제 메시지는 1분에 한 번만 전송)
  
@client.event
async def on_ready():
    print(f" [JoonHee-System] 봇 로그인 완료: {client.user}")
    print(" [JoonHee-System]  서버 및 채널 확인 중...")

    for guild in client.guilds:
        print(f" [JoonHee-System] 서버 이름: {guild.name} (ID: {guild.id})")
        for channel in guild.text_channels:
            print(f" [JoonHee-System] 채널 이름: {channel.name} (ID: {channel.id})")

    client.loop.create_task(send_notification())

if __name__ == "__main__":
    print(" [JoonHee-System]  봇 실행 시작")
    client.run(TOKEN)
