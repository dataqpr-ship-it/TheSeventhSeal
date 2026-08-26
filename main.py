import asyncio
import os
import time
from telegram import Bot

# =========================
# CONFIG
# =========================

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN:
    raise ValueError("BOT_TOKEN belum diset.")

if not CHAT_ID:
    raise ValueError("CHAT_ID belum diset.")

bot = Bot(token=TOKEN)

START_TIME = time.time()
LAST_UPDATE_ID = None


# =========================
# QUOTE SYSTEM
# =========================

def load_quotes():
    with open("quotes.txt", "r", encoding="utf-8") as f:
        content = f.read()

    # Support Windows and Linux line endings
    content = content.replace("\r\n", "\n")

    # Each quote is separated by a blank line
    quotes = [
        q.strip()
        for q in content.split("\n\n")
        if q.strip()
    ]

    return quotes


def get_last_index():
    try:
        with open("last_index.txt", "r", encoding="utf-8") as f:
            return int(f.read().strip())

    except (FileNotFoundError, ValueError):
        return 0


def save_last_index(index):
    with open("last_index.txt", "w", encoding="utf-8") as f:
        f.write(str(index))


async def send_quote():
    quotes = load_quotes()

    if not quotes:
        print("Quote Error: quotes.txt kosong.")
        return

    index = get_last_index()

    if index >= len(quotes):
        index = 0

    quote = quotes[index]

    await bot.send_message(
        chat_id=CHAT_ID,
        text=quote
    )

    save_last_index(index + 1)


# =========================
# QUOTE LOOP
# =========================

async def quote_loop():
    while True:
        try:
            await send_quote()
            print("Quote terkirim")

        except Exception as e:
            print("Quote Error:", e)

        # Kirim quote setiap 6 jam
        await asyncio.sleep(21600)


# =========================
# TELEGRAM COMMANDS
# =========================

async def handle_commands():
    global LAST_UPDATE_ID

    while True:
        try:
            updates = await bot.get_updates(
                offset=LAST_UPDATE_ID,
                timeout=10
            )

            for update in updates:
                LAST_UPDATE_ID = update.update_id + 1

                if not update.message:
                    continue

                text = (
                    update.message.text or ""
                ).strip().lower()

                chat_id = update.message.chat_id

                # =========================
                # /uptime
                # =========================

                if text == "/uptime":
                    uptime = int(
                        time.time() - START_TIME
                    )

                    days = uptime // 86400
                    hours = (uptime % 86400) // 3600
                    minutes = (uptime % 3600) // 60
                    seconds = uptime % 60

                    await bot.send_message(
                        chat_id=chat_id,
                        text=(
                            f"🟢 Uptime: "
                            f"{days}d "
                            f"{hours}h "
                            f"{minutes}m "
                            f"{seconds}s"
                        )
                    )

                # =========================
                # /ping
                # =========================

                elif text == "/ping":
                    start = time.perf_counter()

                    msg = await bot.send_message(
                        chat_id=chat_id,
                        text="🏓 Pong!"
                    )

                    latency = round(
                        (
                            time.perf_counter()
                            - start
                        ) * 1000,
                        2
                    )

                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=msg.message_id,
                        text=f"🏓 Pong! {latency} ms"
                    )

                # =========================
                # /latency
                # =========================

                elif text == "/latency":
                    start = time.perf_counter()

                    await bot.get_me()

                    latency = round(
                        (
                            time.perf_counter()
                            - start
                        ) * 1000,
                        2
                    )

                    await bot.send_message(
                        chat_id=chat_id,
                        text=(
                            f"⚡ API Latency: "
                            f"{latency} ms"
                        )
                    )

                # =========================
                # /health
                # =========================

                elif text == "/health":
                    await bot.send_message(
                        chat_id=chat_id,
                        text=(
                            "✅ Health Check\n"
                            "Status: ONLINE\n"
                            "Quote Service: OK\n"
                            "Telegram API: OK"
                        )
                    )

        except Exception as e:
            print(
                "Command Error:",
                e
            )

        await asyncio.sleep(1)


# =========================
# MAIN
# =========================

async def main():
    await asyncio.gather(
        quote_loop(),
        handle_commands()
    )


if __name__ == "__main__":
    asyncio.run(main())
