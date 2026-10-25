"""Admin-only Telegram bot for human-reviewed outreach drafts."""
from __future__ import annotations
import asyncio
import logging
import os
import re
from pathlib import Path
from urllib.parse import urlparse

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from dotenv import load_dotenv
from . import db

load_dotenv(Path(__file__).with_name(".env"))
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("datinggrowth")
TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0") or "0")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() not in {"0", "false", "no"}

def is_public_telegram_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme == "https" and parsed.netloc in {"t.me", "www.t.me"} and bool(parsed.path.strip("/"))

def admin_only(message: Message) -> bool:
    return bool(ADMIN_ID and message.from_user and message.from_user.id == ADMIN_ID)

def review_keyboard(draft_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Одобрить черновик", callback_data=f"review:approved:{draft_id}"),
        InlineKeyboardButton(text="Отклонить", callback_data=f"review:rejected:{draft_id}"),
    ]])

async def start(message: Message, command: CommandStart) -> None:
    if not message.from_user:
        return
    payload = (command.args or "").strip()
    if payload.startswith("src_"):
        db.record_event(payload[4:], "start")
    if not admin_only(message):
        await message.answer("Служебный бот DatingGrowth AI. Доступ ограничен владельцем проекта.")
        return
    await message.answer(
        "DatingGrowth AI запущен. Режим: " + ("DRY RUN" if DRY_RUN else "ручная подготовка")
        + "\nКоманды: /addcommunity, /communities, /draft, /queue, /stats.\n"
        "Публикаций и массовых рассылок бот не выполняет."
    )

async def addcommunity(message: Message) -> None:
    if not admin_only(message):
        return
    raw = (message.text or "").partition(" ")[2].strip()
    parts = [part.strip() for part in raw.split("|", 2)]
    if len(parts) < 2 or not parts[0] or not is_public_telegram_url(parts[1]):
        await message.answer("Формат: /addcommunity Название | https://t.me/ссылка | правила/контакт (необязательно)")
        return
    try:
        cid = db.add_community(parts[0], parts[1], parts[2] if len(parts) > 2 else "")
    except Exception as exc:
        log.info("Could not add community: %s", exc)
        await message.answer("Не удалось добавить сообщество. Возможно, такая ссылка уже есть.")
        return
    await message.answer(f"Сообщество добавлено в каталог: ID {cid}. Перед предложением проверьте правила и разрешение на рекламу.")

async def communities(message: Message) -> None:
    if not admin_only(message):
        return
    rows = db.list_communities()
    if not rows:
        await message.answer("Каталог пуст. Добавьте проверенную публичную группу командой /addcommunity.")
        return
    text = "\n".join(f"#{r['id']} {r['name']} — {r['url']}\nЗаметки: {r['notes'] or '—'}" for r in rows[:30])
    await message.answer(text[:4000])

async def draft(message: Message) -> None:
    if not admin_only(message):
        return
    raw = (message.text or "").partition(" ")[2].strip()
    match = re.match(r"^(\d+)\s*\|\s*(.+)$", raw, re.S)
    if not match:
        await message.answer("Формат: /draft ID_сообщества | текст персонального предложения администратору")
        return
    cid, body = int(match.group(1)), match.group(2).strip()
    if not body or len(body) > 3500:
        await message.answer("Текст должен содержать от 1 до 3500 символов.")
        return
    if not any(c["id"] == cid for c in db.list_communities()):
        await message.answer("ID сообщества не найден. Используйте /communities.")
        return
    did = db.add_draft(cid, body)
    await message.answer(f"Черновик #{did} создан и ожидает проверки.\n\n{body}", reply_markup=review_keyboard(did))

async def queue(message: Message) -> None:
    if not admin_only(message):
        return
    rows = db.list_drafts("pending")
    if not rows:
        await message.answer("Ожидающих черновиков нет.")
        return
    for row in rows[:10]:
        await message.answer(
            f"Черновик #{row['id']} → {row['community_name']}\n{row['url']}\n\n{row['body'][:3000]}",
            reply_markup=review_keyboard(row["id"]),
        )

async def stats_command(message: Message) -> None:
    if not admin_only(message):
        return
    s = db.stats()
    await message.answer(
        "DatingGrowth AI — статистика\n"
        f"Сообщества: {s['communities']}\nОжидают проверки: {s['pending']}\n"
        f"Одобрены: {s['approved']}\nОтклонены: {s['rejected']}\n"
        f"Зафиксировано запусков по source-коду этого служебного бота: {s['tracked_starts']}\n"
        "Важно: это не аналитика целевого бота знакомств."
    )

async def review_callback(callback: CallbackQuery) -> None:
    if not callback.from_user or callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return
    try:
        _, decision, raw_id = (callback.data or "").split(":", 2)
        did = int(raw_id)
    except (ValueError, TypeError):
        await callback.answer("Некорректная команда.", show_alert=True)
        return
    changed = db.review_draft(did, decision)
    if not changed:
        await callback.answer("Черновик уже обработан или не найден.", show_alert=True)
        return
    await callback.answer("Статус обновлён.")
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            f"Черновик #{did}: {'одобрен для ручного использования' if decision == 'approved' else 'отклонён'}. Автоматической отправки нет."
        )

async def main() -> None:
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN не задан. Заполните projects/datinggrowth/.env по образцу .env.example.")
    if ADMIN_ID <= 0:
        raise RuntimeError("ADMIN_ID не задан. Укажите числовой Telegram ID владельца.")
    db.init_db()
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.message.register(start, CommandStart())
    dp.message.register(addcommunity, Command("addcommunity"))
    dp.message.register(communities, Command("communities"))
    dp.message.register(draft, Command("draft"))
    dp.message.register(queue, Command("queue"))
    dp.message.register(stats_command, Command("stats"))
    dp.callback_query.register(review_callback, F.data.startswith("review:"))
    log.info("Starting DatingGrowth AI; DRY_RUN=%s", DRY_RUN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
