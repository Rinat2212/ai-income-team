"""Deterministic safety and quality checks for DatingGrowth outreach drafts."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class QualityReport:
    approved_for_human_review: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


_BLOCKED_PATTERNS = (
    (r"массов(?:ая|ые|ую)\s+(?:рассылк|личн(?:ые|ых) сообщ)", "Похоже на массовую рассылку."),
    (r"обход(?:ить|а|им)\s+(?:ограничени|бан|правил)", "Нельзя предлагать обход ограничений или правил."),
    (r"спам(?:ить|а|ом)?", "Текст содержит упоминание спама."),
    (r"без\s+разрешени", "Текст упоминает действия без разрешения."),
)
_PERMISSION_PHRASES = (
    "разреш", "можно ли", "соглас", "правила размещения", "если это допустимо",
)
_LINK_RE = re.compile(r"https?://\S+", re.IGNORECASE)


def check_outreach_text(body: str) -> QualityReport:
    """Check a draft before a person reviews it; this never sends anything."""
    text = " ".join((body or "").split())
    blockers: list[str] = []
    warnings: list[str] = []

    if not text:
        blockers.append("Текст пустой.")
    if len(text) > 3500:
        blockers.append("Текст превышает лимит 3500 символов.")

    lowered = text.casefold()
    for pattern, message in _BLOCKED_PATTERNS:
        if re.search(pattern, lowered):
            blockers.append(message)

    if not any(phrase in lowered for phrase in _PERMISSION_PHRASES):
        warnings.append("Не найден явный запрос разрешения; проверьте, что текст не предполагает публикацию без согласования.")
    if len(_LINK_RE.findall(text)) > 2:
        warnings.append("В тексте больше двух ссылок; проверьте их необходимость и релевантность.")
    if text.count("!") > 4:
        warnings.append("Слишком много восклицательных знаков; тон может выглядеть как спам.")

    return QualityReport(
        approved_for_human_review=not blockers,
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )
