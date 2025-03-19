import os
import discord
import asyncio
from datetime import datetime

# GitHub Secrets에서 환경 변수 가져오기
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# 🚨 환경 변수 확인 로그 추가
print(f"🔍 DEBUG: DISCORD_TOKEN 존재 여부: {'설정됨' if TOKEN else '없음'}")
print(f"🔍 DEBUG: CHANNEL_ID 존재 여부: {'설정됨' if CHANNEL_ID else '없음'}")

if not TOKEN or not CHANNEL_ID:
    print("🚨 오류: DISCORD_TOKEN 또는 CHANNEL_ID가 설정되지 않았습니다.")
    exit(1)

CHANNEL_ID = int(CHANNEL_ID)

# 디스코드 클라이언트 설정
intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def send_notification():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print(f"🚨 오류: 채널 ID {CHANNEL_ID}을 찾을 수 없음.")
        return

    print(f"✅ 채널 확인 완료: {channel.name} (ID: {channel.id})")

    # 🚀 실행 확인 메시지 강제 전송
    try:
        debug_message = "✅ 디스코드 봇이 실행되었습니다!\n📌 채널 확인 완료"
        await channel.send(debug_message)
        print(f"✅ 실행 확인 메시지 전송 완료")
    except Exception as e:
        print(f"🚨 실행 확인 메시지 전송 실패: {e}")

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
