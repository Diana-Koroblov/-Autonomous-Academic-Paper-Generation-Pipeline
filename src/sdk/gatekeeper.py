import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict

logger = logging.getLogger(__name__)

class Gatekeeper:
    """
    Centralized API manager for Google Gemini API ecosystem.
    Implements a strict FIFO queue, token-bucket rate limiting, and exponential backoff.
    """
    def __init__(self, config_path: str | Path = "config/rate_limits.json"):
        self.config = self._load_config(config_path)
        self.llm_config = self.config.get("llm_api", {})

        self.max_rpm = self.llm_config.get("max_requests_per_minute", 60)
        self.timeout_seconds = self.llm_config.get("timeout_seconds", 90)
        self.max_retries = self.llm_config.get("max_retries", 5)
        self.backoff_factor = self.llm_config.get("backoff_factor", 2.0)

        self.queue: asyncio.Queue = asyncio.Queue()
        self.tokens = float(self.max_rpm)
        self.last_refill = time.monotonic()
        self._worker_task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    def _load_config(self, path: str | Path) -> Dict[str, Any]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load {path}: {e}. Using defaults.")
            return {}

    async def _refill_tokens(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        refill_amount = elapsed * (self.max_rpm / 60.0)
        if refill_amount > 0:
            self.tokens = min(float(self.max_rpm), self.tokens + refill_amount)
            self.last_refill = now

    async def _acquire_token(self) -> None:
        while True:
            async with self._lock:
                await self._refill_tokens()
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return
            await asyncio.sleep(0.1)

    async def _process_queue(self) -> None:
        while True:
            req = await self.queue.get()
            func, args, kwargs, future = req

            await self._acquire_token()

            try:
                result = await self._execute_with_retry(func, *args, **kwargs)
                if not future.done():
                    future.set_result(result)
            except Exception as e:
                if not future.done():
                    future.set_exception(e)
            finally:
                self.queue.task_done()

    async def _execute_with_retry(self, func: Callable[..., Coroutine], *args: Any, **kwargs: Any) -> Any:
        retries = 0
        while True:
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=self.timeout_seconds)
            except Exception as e:
                err_str = str(e)
                # Retry on typical transient API boundary exceptions (Rate Limit/Server Error)
                if any(err in err_str for err in ["429", "500", "502", "503", "504"]):
                    if retries >= self.max_retries:
                        raise e
                    delay = self.backoff_factor ** retries
                    logger.warning(f"API Exception {err_str}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    retries += 1
                elif isinstance(e, asyncio.TimeoutError):
                    if retries >= self.max_retries:
                        raise e
                    delay = self.backoff_factor ** retries
                    logger.warning(f"API Timeout. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    retries += 1
                else:
                    raise e

    def start(self) -> None:
        """Starts the background FIFO queue processing task."""
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._process_queue())

    async def stop(self) -> None:
        """Stops the background FIFO queue processing task."""
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
            self._worker_task = None

    async def execute(self, func: Callable[..., Coroutine], *args: Any, **kwargs: Any) -> Any:
        """Schedules a coroutine function in the FIFO queue and awaits its result."""
        future = asyncio.get_running_loop().create_future()
        await self.queue.put((func, args, kwargs, future))
        return await future

# Global singleton gatekeeper instance
gatekeeper = Gatekeeper()
