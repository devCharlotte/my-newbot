import os
import discord
import asyncio
from datetime import datetime

# GitHub Secrets에서 환경 변수 가져오기
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not TOKEN or not CHANNEL_ID:
    print("🚨 오류: DISCORD_TOKEN 또는 CHANNEL_ID가 설정되지 않았습니다.")
    exit(1)

CHANNEL_ID = int(CHANNEL_ID)

# 디스코드 클라이언트 설정
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# 기본 알람 스케줄 (매일 07:00 ~ 23:59)
ALARM_HOURS = range(7, 24)  # 07:00 ~ 23:59
ALARM_MINUTES = {0: "⏰ 정각입니다!", 25: "🕒 25분이 되었습니다!", 50: "⏳ 50분이 되었습니다!"}

# 사용자 지정 알림 (요일별 특정 시간 추가 가능)
EXTRA_SCHEDULES = {
    "Monday": {10: "📢 월요일 오전 10시입니다. 새로운 한 주를 시작해보세요!"},
    "Wednesday": {15: "📢 수요일 오후 3시입니다. 벌써 주중 절반을 지나고 있어요!"},
    "Friday": {20: "📢 금요일 밤 8시입니다! 주말이 얼마 남지 않았어요!"}
}

# ✅ 메시지 전송 함수
async def send_message(channel, message):
    try:
        await channel.send(message)
        print(f"✅ 메시지 전송 완료: {message}")
    except discord.errors.Forbidden:
        print("🚨 오류: 메시지 전송 권한이 없음 (Forbidden)")
    except discord.errors.HTTPException as e:
        print(f"🚨 오류: 메시지 전송 실패 - {e}")
    except Exception as e:
        print(f"🚨 알 수 없는 오류 발생: {e}")

# ✅ 알람 실행 함수
async def send_notification():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print(f"🚨 오류: 채널 ID {CHANNEL_ID}을 찾을 수 없음.")
        return

    print(f"✅ 채널 확인 완료: {channel.name} (ID: {channel.id})")

    while True:
        now = datetime.now()
        weekday = now.strftime("%A")  # 요일 (Monday, Tuesday, ...)

        # 기본 알람 스케줄 (정각, 25분, 50분)
        if now.hour in ALARM_HOURS and now.minute in ALARM_MINUTES:
            message = f"{ALARM_MINUTES[now.minute]}\n🕒 현재 시각: {now.strftime('%H:%M')}"
            await send_message(channel, message)

        # 사용자 지정 알람 스케줄 (요일별 추가 알림)
        if weekday in EXTRA_SCHEDULES and now.hour in EXTRA_SCHEDULES[weekday] and now.minute == 0:
            message = f"{EXTRA_SCHEDULES[weekday][now.hour]}\n🕒 현재 시각: {now.strftime('%H:%M')}"
            await send_message(channel, message)

        await asyncio.sleep(60)  # 1분 대기 후 다시 확인

@client.event
async def on_ready():
    print(f"✅ 봇 로그인 완료: {client.user}")
    print("✅ 서버 및 채널 확인 중...")

    for guild in client.guilds:
        print(f"📌 서버 이름: {guild.name} (ID: {guild.id})")
        for channel in guild.text_channels:
            print(f"📌 채널 이름: {channel.name} (ID: {channel.id})")

    client.loop.create_task(send_notification())

if __name__ == "__main__":
    print("🚀 봇 실행 시작")
    client.run(TOKEN)
