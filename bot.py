import os
import discord
import asyncio
from datetime import datetime, timedelta

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not TOKEN or not CHANNEL_ID:
    print(" [JoonHee-System]  오류: DISCORD_TOKEN 또는 CHANNEL_ID 설정 오류")
    exit(1)

CHANNEL_ID = int(CHANNEL_ID)

# 디스코드 클라이언트
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# 기본 알람
ALARM_HOURS = list(range(7, 24)) + [0, 1]  # 07:00 ~ 23:59 + 다음날 새벽 00:00 ~ 01:59
ALARM_MINUTES = {
    0: "⏰ {time} - 집중 시작!", 
    25: "⏰ {time} - 조금만 더 파이팅!", 
    50: "⏳ {time} - 이제 쉬자! 스트레칭하고 물 마시기!"
}

# 추가 알람
EXTRA_SCHEDULES = {
    "Monday": {
        5: "Monday!! \n- 9 : Distributed Systems\n- 12 : System Security \n- 3 : Information Security Law \n- 7 : 학원",
        8: "⏰ 분산시스템 (9시, 수203, 김규영 교수님)",
        9: "🕒 인턴십 일지 / 개정법 preclass / 분산 스터디 / 랩미팅 준비",
        11: "⏰ 시스템보안 (12시, 프601, 김성민 교수님)",
        14: "⏰ 개인정보보호법 (3시, 성305, 홍준호 교수님)"
    },
    "Tuesday": {
        5: "Tuesday!! \n- 3 : Industrial Security and Legal System",
        8: "🕒 인턴십 일지 / 산업보안법 preclass / 분산 스터디 / 랩미팅 준비"
    },
    "Wednesday": {
        5: "Wednesday!! \n- 9 : Work in Magok\n- 12 : Security SW Analysis and Development \n- 3 : Convergence Security Forensic",
        8: "🕒 인턴십 일지 / 보안sw preclass / 랩미팅 준비",
        14: "⏰ 융합보안포렌식 (3시, 성211, 김학경 교수님)"
    },
    "Thursday": {
        5: "Thursday!! \n- 9 : TA work \n- 1 : Lab meeting \n- 3 : Introduction to Information Technology",
        9: "🕒 인턴십 일지 / 보안 sw preclass / 조교 업무 / 랩미팅 준비",
        12: "⏰ 랩미팅 (1시)",
        14: "⏰ 융합보안개론 (3시, 성704, 김경진 교수님)"
    },
    "Friday": {
        5: "Friday!! \n- 9 : Work in Yongsan "
    }
}

# 메시지 전송
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

# 알람 실행 (07:00 ~ 다음날 01:00)
async def send_notification():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print(f" [JoonHee-System]  오류: 채널 ID {CHANNEL_ID}을 찾을 수 없음.")
        return

    print(f" [JoonHee-System]  채널 확인 완료: {channel.name} (ID: {channel.id})")

    last_sent_minute = None

    while True:
        now_utc = datetime.utcnow()
        now = now_utc + timedelta(hours=9)  # KST 변환
        weekday = now.strftime("%A")
        formatted_time = now.strftime("%I:%M %p").lstrip("0")

        if now.minute != last_sent_minute:
            if now.hour in ALARM_HOURS and now.minute in ALARM_MINUTES:
                alert_message = ALARM_MINUTES[now.minute].format(time=formatted_time)
                await send_message(channel, alert_message)

            if weekday in EXTRA_SCHEDULES and now.hour in EXTRA_SCHEDULES[weekday]:
                if now.minute == 45:
                    class_message = EXTRA_SCHEDULES[weekday][now.hour]
                    await send_message(channel, class_message)

            last_sent_minute = now.minute

        await asyncio.sleep(60)

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
