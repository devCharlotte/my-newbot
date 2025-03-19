import os
import discord
import asyncio
from datetime import datetime

# GitHub Secrets에서 환경 변수 가져오기
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not TOKEN or not CHANNEL_ID:
    raise ValueError("🚨 DISCORD_TOKEN 또는 CHANNEL_ID가 설정되지 않았습니다. GitHub Secrets를 확인하세요.")

CHANNEL_ID = int(CHANNEL_ID)

# 테스트 모드 설정 (True = 즉시 메시지 전송, False = 일반 모드)
TEST_MODE = True  # 필요 시 False로 변경

intents = discord.Intents.default()
intents.message_content = True  # ✅ 메시지 읽기 허용
client = discord.Client(intents=intents)

# 기본 알람 스케줄 (매시간 00분, 30분, 50분)
ALARM_HOURS = range(8, 24)  # 08:00 ~ 23:59
ALARM_MINUTES = {0: "🔔 00시 00분!!", 30: "🕞 30분이야! 다시 집중해보자!", 50: "⏳ 50분! 이제 잠깐 쉬는 시간을 가져보자!"}

async def send_notification():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print(f"🚨 채널 ID {CHANNEL_ID}을 찾을 수 없음.")
        return

    print(f"✅ 채널 확인 완료: {channel.name} (ID: {channel.id})")

    # 🚀 테스트 모드 실행
    if TEST_MODE:
        test_message = f"🛠 [테스트 모드] 즉시 메시지 전송됨\n🕒 {datetime.now().strftime('%H:%M')}"
        await channel.send(test_message)
        print(f"✅ 테스트 모드 메시지 전송 완료: {test_message}")
        return  # 테스트 모드에서는 즉시 종료

    print("✅ 알림 봇 실행 중...")

    while True:
        now = datetime.now()
        if now.hour in ALARM_HOURS and now.minute in ALARM_MINUTES:
            message = f"{ALARM_MINUTES[now.minute]}\n🕒 현재 시각: {now.strftime('%H:%M')}"
            await channel.send(message)
            print(f"✅ 알림 전송: {message}")
        await asyncio.sleep(60)

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
    client.run(TOKEN)
