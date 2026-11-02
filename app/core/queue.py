"""
Resource-Aware Non-Blocking Sequential Queue & Worker Lifecycle Supervisor for AI-VPS.
Master Architecture v2.2 & PRD v2.2 Aligned.

Enforces:
1. Non-blocking asyncio.create_subprocess_exec (never block FastAPI event loop).
2. 10-Step Production Worker Lifecycle with Windows Child Process Tree Cleanup.
3. Idempotent Duplicate Task Prevention (Idempotency Key).
4. Zero-Retry policy on ResourceExhaustionError (OOM avoidance); max 2 retries on recoverable errors.
5. Task cancellation support.
"""
import asyncio
import hashlib
import json
import logging
from typing import Dict, Any, List, Optional, Callable, Awaitable
import psutil

from app.config import settings
from app.core.memory_manager import memory_manager, ResourceExhaustionError

logger = logging.getLogger("ai_vps.queue")


class DuplicateTaskError(Exception):
    """Raised when an identical task is already active or queued."""
    pass


class TaskCancelledError(Exception):
    """Raised when a running or queued task is cancelled by user."""
    pass


class TaskItem:
    def __init__(
        self,
        task_id: str,
        project_id: str,
        task_type: str,
        command: List[str],
        params: Optional[Dict[str, Any]] = None,
        required_ram_gb: float = 0.1,
        timeout_sec: int = 600,
        max_retries: int = 2,
    ):
        self.task_id = task_id
        self.project_id = project_id
        self.task_type = task_type
        self.command = command
        self.params = params or {}
        self.required_ram_gb = required_ram_gb
        self.timeout_sec = timeout_sec
        self.max_retries = max_retries
        self.retry_count = 0
        self.status = "QUEUED"  # QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
        self.error_message: Optional[str] = None
        self.exit_code: Optional[int] = None
        self.output_logs: List[str] = []
        self.idempotency_key = self._generate_idempotency_key()

    def _generate_idempotency_key(self) -> str:
        payload = f"{self.project_id}:{self.task_type}:{json.dumps(self.params, sort_keys=True)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class TaskQueue:
    def __init__(self):
        self._queue: asyncio.Queue[TaskItem] = asyncio.Queue()
        self._active_tasks: Dict[str, TaskItem] = {}
        self._running_processes: Dict[str, asyncio.subprocess.Process] = {}
        self._is_running = False
        self._worker_loop_task: Optional[asyncio.Task] = None

    def start(self) -> None:
        """Starts the sequential background queue consumer."""
        if not self._is_running:
            self._is_running = True
            self._worker_loop_task = asyncio.create_task(self._process_queue_loop())

    async def stop(self) -> None:
        """Stops the queue and terminates running processes gracefully."""
        self._is_running = False
        # Cancel all running processes
        for task_id in list(self._running_processes.keys()):
            await self.cancel_task(task_id)
        if self._worker_loop_task:
            self._worker_loop_task.cancel()
            try:
                await self._worker_loop_task
            except asyncio.CancelledError:
                pass

    async def enqueue(self, task: TaskItem) -> str:
        """
        Enqueues task after verifying duplicate prevention (Idempotency Key).
        """
        # Check active and queued tasks for duplicate idempotency key
        for existing in self._active_tasks.values():
            if existing.idempotency_key == task.idempotency_key and existing.status in ("QUEUED", "RUNNING"):
                raise DuplicateTaskError(
                    f"Duplicate task rejected: Task with idempotency key '{task.idempotency_key}' is already {existing.status}."
                )

        self._active_tasks[task.task_id] = task
        await self._queue.put(task)
        return task.task_id

    async def cancel_task(self, task_id: str) -> bool:
        """
        Step 5: Cancels a queued or actively running worker task.
        Sends SIGTERM and forces cleanup of Windows Child Process Tree.
        """
        task = self._active_tasks.get(task_id)
        if not task:
            return False

        proc = self._running_processes.get(task_id)
        if proc and proc.returncode is None:
            # Step 6: Cleanup Windows Child Process Tree
            self._terminate_process_tree(proc.pid)
            try:
                proc.terminate()
            except Exception:
                pass

        task.status = "CANCELLED"
        task.error_message = "Task cancelled by user request."
        if task_id in self._running_processes:
            del self._running_processes[task_id]
        return True

    def _terminate_process_tree(self, pid: int) -> None:
        """
        Step 6: Safely kills all descendant processes of pid on Windows.
        """
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                try:
                    child.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            # Allow short grace period then kill if still alive
            _, alive = psutil.wait_procs(children, timeout=1.0)
            for p in alive:
                try:
                    p.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            try:
                parent.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    async def _process_queue_loop(self) -> None:
        """Sequential single-worker FIFO loop."""
        while self._is_running:
            try:
                task = await self._queue.get()
                if task.status == "CANCELLED":
                    self._queue.task_done()
                    continue

                await self.execute_worker_task(task)
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in queue loop: {e}", exc_info=True)

    async def execute_worker_task(self, task: TaskItem) -> None:
        """
        10-Step Production Worker Lifecycle Implementation:
        1. Resource Readiness Check (RAM preflight)
        2. Worker Process Start (asyncio.create_subprocess_exec)
        3. Async Process Monitoring (bounded streaming)
        4. Timeout Monitoring (TimeoutError)
        5. Cancellation Handling
        6. Windows Child Process Tree Cleanup
        7. Process Exit Verification
        8. RAM/VRAM Re-measurement
        9. Resource Readiness Gate
        10. Next Heavy Task Approval
        """
        task.status = "RUNNING"
        proc = None
        original_error: Optional[Exception] = None

        try:
            # Step 1: Resource Readiness Check
            memory_manager.check_resource_readiness(task.required_ram_gb)

            # Step 2: Worker Process Start (Non-blocking!)
            proc = await asyncio.create_subprocess_exec(
                *task.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            self._running_processes[task.task_id] = proc

            # Step 3 & 4: Stream logs with bounded memory and timeout
            async def monitor_output():
                bounded_logs: List[str] = []
                max_buffer_lines = 500

                async def read_stream(stream, prefix):
                    while line := await stream.readline():
                        decoded = line.decode("utf-8", errors="replace").strip()
                        if len(bounded_logs) >= max_buffer_lines:
                            bounded_logs.pop(0)
                        bounded_logs.append(f"{prefix}: {decoded}")

                await asyncio.gather(
                    read_stream(proc.stdout, "OUT"),
                    read_stream(proc.stderr, "ERR"),
                )
                await proc.wait()
                task.output_logs = bounded_logs

            # Monitor with Step 4 Timeout
            await asyncio.wait_for(monitor_output(), timeout=task.timeout_sec)

            # Step 7: Process Exit Verification
            task.exit_code = proc.returncode
            if task.exit_code == 0:
                task.status = "COMPLETED"
            else:
                raise RuntimeError(f"Process exited with non-zero code {task.exit_code}")

        except asyncio.TimeoutError as te:
            original_error = TimeoutError(f"Task exceeded execution timeout of {task.timeout_sec}s.")
            task.status = "FAILED"
            task.error_message = str(original_error)
            if proc and proc.pid:
                self._terminate_process_tree(proc.pid)
            raise original_error from te

        except ResourceExhaustionError as ree:
            # OOM Policy: Zero Retries! Immediate Failure
            original_error = ree
            task.status = "FAILED"
            task.error_message = f"Out of Memory (OOM): {ree}"
            raise ree

        except Exception as exc:
            original_error = exc
            # Handle recoverable errors with retries
            if task.retry_count < task.max_retries and task.status != "CANCELLED":
                task.retry_count += 1
                task.status = "QUEUED"
                logger.warning(f"Task {task.task_id} failed ({exc}). Retrying {task.retry_count}/{task.max_retries}...")
                await self._queue.put(task)
            else:
                task.status = "FAILED"
                task.error_message = str(exc)
            raise exc

        finally:
            # Step 6: Ensure process is completely killed
            if proc and proc.pid:
                self._terminate_process_tree(proc.pid)

            if task.task_id in self._running_processes:
                del self._running_processes[task.task_id]

            # Step 8: RAM/VRAM Re-measurement (Exceptions here must not mask original_error)
            try:
                memory_manager.release_memory()
            except Exception as cleanup_err:
                logger.error(f"Error during memory release cleanup: {cleanup_err}")
                if original_error:
                    # Preserve original error context
                    pass

            # Step 9 & 10: Resource Readiness Gate for subsequent tasks
            try:
                memory_manager.check_resource_readiness(0.1)
            except Exception as gate_err:
                logger.warning(f"Resource gate warning before next task: {gate_err}")


# Global Task Queue Instance
task_queue = TaskQueue()
