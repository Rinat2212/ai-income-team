"""Минимальный координатор задач без внешних действий."""

from dataclasses import dataclass
from typing import Iterable


@dataclass
class Task:
    name: str
    status: str = "pending"


class Coordinator:
    def __init__(self, agent_names: Iterable[str]):
        self.agent_names = list(agent_names)

    def status(self) -> dict:
        return {
            "agents_total": len(self.agent_names),
            "agents": self.agent_names.copy(),
            "mode": "DRY_RUN",
        }

    def create_task(self, name: str) -> Task:
        normalized = name.strip()
        if not normalized:
            raise ValueError("Название задачи не может быть пустым")
        return Task(name=normalized)
