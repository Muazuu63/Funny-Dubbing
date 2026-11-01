"""Single-worker FIFO queue management for AI-VPS."""
import asyncio

class TaskQueue:
    def __init__(self):
        self._queue = asyncio.Queue()
        self._running = False

    async def enqueue(self, task_data: dict):
        await self._queue.put(task_data)

    async def get_next(self):
        return await self._queue.get()
