from dataclasses import dataclass
from datetime import datetime
import asyncio
from typing import Optional


@dataclass
class HealthStatus:
    server_name: str
    healthy: bool
    last_checked: datetime
    error_message: Optional[str] = None


class HealthCheckService:
    def __init__(self, check_interval_seconds: int = 60):
        self.check_interval_seconds = check_interval_seconds if check_interval_seconds > 0 else 60
        self.server_health: dict[str, HealthStatus | None] = {}
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def _check_loop(self):
        while self._running:
            await self._perform_checks()
            await asyncio.sleep(self.check_interval_seconds)

    async def _perform_checks(self):
        for server_name in list(self.server_health.keys()):
            try:
                await self._check_server(server_name)
            except Exception as e:
                self.server_health[server_name] = HealthStatus(
                    server_name=server_name, healthy=False, last_checked=datetime.now(), error_message=str(e)
                )

    async def _check_server(self, server_name: str):
        self.server_health[server_name] = HealthStatus(
            server_name=server_name, healthy=True, last_checked=datetime.now(), error_message=None
        )

    def start(self):
        if self._task is not None:
            return
        self._running = True
        self._task = asyncio.create_task(self._check_loop())

    def stop(self):
        self._running = False
        if self._task is not None:
            self._task.cancel()
            self._task = None

    def get_overall_health(self) -> bool:
        if not self.server_health:
            return True
        return all(status.healthy for status in self.server_health.values())
