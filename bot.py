import os
import discord
import asyncio
from datetime import datetime, timedelta

# 테스트 모드
TEST_MODE = True  # True: 테스트, False: 운영

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not TOKEN or not CHANNEL_ID:
    print(" [JoonHee-System]  오류: DISCORD_TOKEN 또는 CHANNEL_ID 설정 오류")
    exit(1)

CHANNEL_ID = int(CHANNEL_ID)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

ALARM_HOURS = list(range(7, 24)) + [0, 1]
ALARM_MINUTES = {
    0: "⏰ {time} - 집중 시작!",
    25: "⏰ {time} - 조금만 더 파이팅!",
    50: "⏳ {time} - 이제 쉬자! 스트레칭하고 물 마시기!"
}

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

async def send_message(channel, message):
    try:
        await channel.send(message)
        print(f" [JoonHee-System] 메시지 전송 완료: {message[:50]}...")
    except Exception as e:
        print(f" [JoonHee-System] 메시지 전송 오류: {e}")

# 테스트 모드 실행: 요일별 메시지를 시간 순서로 정리해서 한 번에 전송
async def run_test_mode(channel):
    await send_message(channel, "🔧 Test Mode Started - Sending all weekly alarms...")

    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    for day in weekdays:
        events = []

        # 헤더 먼저
        events.append(((0, 0), f"**===== test mode : {day} =====**"))

        # 기본 알람 시간
        for hour in ALARM_HOURS:
            for minute, template in ALARM_MINUTES.items():
                dt = datetime(2024, 1, 1, hour, minute)
                formatted_time = dt.strftime("%I:%M %p").lstrip("0")
                message = template.format(time=formatted_time)
                events.append(((hour, minute), message))

        # 5시 45분: Today is 요일
        events.append(((5, 45), f"🕒 5:45 AM - Today is {day}!!"))

        # 추가 스케줄 알람 (5시 제외)
        if day in EXTRA_SCHEDULES:
            for hour, message in EXTRA_SCHEDULES[day].items():
                if hour == 5:
                    continue
                events.append(((hour, 45), f"🕒 {day} {hour}:45 - {message}"))

        # 시간 기준 정렬
        events.sort(key=lambda x: (x[0][0], x[0][1]))

        # 메시지 묶음 전송
        full_message = "\n".join([msg for _, msg in events])
        await send_message(channel, full_message)
        await asyncio.sleep(1)

# 운영 모드: 실시간 알림 감지
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
        now = now_utc + timedelta(hours=9)  # 한국 시간
        weekday = now.strftime("%A")
        formatted_time = now.strftime("%I:%M %p").lstrip("0")

        if now.minute != last_sent_minute:
            if now.hour in ALARM_HOURS and now.minute in ALARM_MINUTES:
                msg = ALARM_MINUTES[now.minute].format(time=formatted_time)
                await send_message(channel, msg)

            if weekday in EXTRA_SCHEDULES and now.hour in EXTRA_SCHEDULES[weekday]:
                if now.minute == 45:
                    if now.hour == 5:
                        await send_message(channel, f"🕒 5:45 AM - Today is {weekday}!!")
                    else:
                        await send_message(channel, EXTRA_SCHEDULES[weekday][now.hour])

            last_sent_minute = now.minute

        await asyncio.sleep(60)

@client.event
async def on_ready():
    print(f" [JoonHee-System] 봇 로그인 완료: {client.user}")
    channel = client.get_channel(CHANNEL_ID)

    if TEST_MODE:
        await run_test_mode(channel)
        await client.close()
    else:
        client.loop.create_task(send_notification())

if __name__ == "__main__":
    print(" [JoonHee-System]  봇 실행 시작")
    client.run(TOKEN)
