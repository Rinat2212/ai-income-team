"""Настройки AI Income Team. Бесплатное ядро."""

PROJECT_NAME = "AI Income Team"
VERSION = "0.1.0"

# Безопасный режим: никаких публикаций, рассылок или платежей.
DRY_RUN = True

DATABASE_PATH = "data/income_team.sqlite3"
LOG_PATH = "logs/system.log"

AGENTS = [
    "researcher",
    "analyst",
    "content",
    "video",
    "affiliate",
    "freelance",
    "sales",
    "developer",
    "quality",
    "finance",
    "coordinator",
]
