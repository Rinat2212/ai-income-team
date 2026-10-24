"""Точка входа AI Income Team."""

import json
import logging
from pathlib import Path

import config
from core.coordinator import Coordinator


def main() -> None:
    root = Path(__file__).resolve().parent
    (root / "data").mkdir(exist_ok=True)
    (root / "logs").mkdir(exist_ok=True)

    logging.basicConfig(
        filename=root / config.LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    coordinator = Coordinator(config.AGENTS)
    report = coordinator.status()
    report["project"] = config.PROJECT_NAME
    report["version"] = config.VERSION
    report["external_actions_enabled"] = not config.DRY_RUN

    logging.info("Система запущена в безопасном режиме")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
