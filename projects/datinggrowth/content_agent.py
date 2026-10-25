"""Deterministic content agent for permission-first Telegram outreach.

This module intentionally drafts a request for permission to the community admin;
it does not produce unsolicited group posts or send messages.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class OutreachBrief:
    community_name: str
    bot_name: str
    purpose: str
    public_link: str


def _clean(value: str, limit: int = 240) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    return value[:limit].rstrip()


def validate_brief(brief: OutreachBrief) -> None:
    if not _clean(brief.community_name):
        raise ValueError("Название сообщества обязательно")
    if not _clean(brief.bot_name):
        raise ValueError("Название бота обязательно")
    if not _clean(brief.purpose):
        raise ValueError("Краткое описание обязательно")
    if not re.fullmatch(r"https://t\.me/[A-Za-z0-9_/?=&%-]+", _clean(brief.public_link, 300)):
        raise ValueError("Ссылка должна быть публичной ссылкой https://t.me/...")


def generate_admin_outreach(brief: OutreachBrief) -> list[str]:
    """Return three short variants asking a human admin for permission."""
    validate_brief(brief)
    community = _clean(brief.community_name, 100)
    bot = _clean(brief.bot_name, 100)
    purpose = _clean(brief.purpose, 240)
    link = _clean(brief.public_link, 300)
    return [
        (
            f"Здравствуйте! Пишу по поводу сообщества «{community}». "
            f"Мы развиваем {bot} — {purpose}. "
            f"Можно ли согласовать публикацию о проекте в вашем сообществе? "
            f"Ссылка: {link}. Если реклама не подходит правилам, публиковать не будем."
        ),
        (
            f"Добрый день! Подскажите, пожалуйста, разрешены ли у вас публикации "
            f"о тематических Telegram-ботах? Наш проект — {bot}: {purpose}. "
            f"Информация о нём: {link}. Сначала хочу получить ваше разрешение "
            f"и узнать условия размещения."
        ),
        (
            f"Здравствуйте! Хотел бы уточнить условия размещения в «{community}». "
            f"Можно ли отправить вам на согласование короткий пост о {bot} "
            f"({purpose})? Ссылка на проект: {link}. Без вашего согласия "
            f"публиковать сообщение не будем."
        ),
    ]
