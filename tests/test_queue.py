"""
Unit tests for Resource-Aware Non-Blocking Sequential Queue & Worker Lifecycle (Phase 4).
Tests: Duplicate Prevention, Cancellation, Timeout, OOM Zero-Retry, and Process Cleanup.
"""
import pytest
import asyncio
import sys
from app.core.queue import (
    TaskQueue,
    TaskItem,
    DuplicateTaskError,
)
from app.core.memory_manager import (
    memory_manager,
    ResourceExhaustionError,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_duplicate_task_prevention():
    """Verify duplicate tasks with identical project_id, task_type and params are rejected."""
    q = TaskQueue()

    task1 = TaskItem(
        task_id="t1",
        project_id="p1",
        task_type="separation",
        command=[sys.executable, "-c", "import time; time.sleep(1)"],
        params={"model": "htdemucs"},
    )
    task2 = TaskItem(
        task_id="t2",
        project_id="p1",
        task_type="separation",
        command=[sys.executable, "-c", "import time; time.sleep(1)"],
        params={"model": "htdemucs"},
    )

    await q.enqueue(task1)
    with pytest.raises(DuplicateTaskError, match="Duplicate task rejected"):
        await q.enqueue(task2)


@pytest.mark.anyio
async def test_worker_lifecycle_success():
    """Verify standard non-blocking execution completes with exit code 0."""
    q = TaskQueue()
    task = TaskItem(
        task_id="success_task",
        project_id="p2",
        task_type="test_step",
        command=[sys.executable, "-c", "print('Worker running'); exit(0)"],
        timeout_sec=10,
    )

    await q.execute_worker_task(task)
    assert task.status == "COMPLETED"
    assert task.exit_code == 0
    assert any("Worker running" in line for line in task.output_logs)


@pytest.mark.anyio
async def test_task_timeout_handling():
    """Verify that tasks exceeding timeout_sec raise TimeoutError and terminate."""
    q = TaskQueue()
    task = TaskItem(
        task_id="timeout_task",
        project_id="p3",
        task_type="sleep_step",
        command=[sys.executable, "-c", "import time; time.sleep(10)"],
        timeout_sec=1,  # 1 second timeout
    )

    with pytest.raises(TimeoutError, match="timeout"):
        await q.execute_worker_task(task)

    assert task.status == "FAILED"


@pytest.mark.anyio
async def test_task_cancellation():
    """Verify task cancellation terminates process and flags status CANCELLED."""
    q = TaskQueue()
    task = TaskItem(
        task_id="cancel_task",
        project_id="p4",
        task_type="long_step",
        command=[sys.executable, "-c", "import time; time.sleep(10)"],
        timeout_sec=10,
    )

    await q.enqueue(task)

    # Launch execution in background
    exec_task = asyncio.create_task(q.execute_worker_task(task))
    await asyncio.sleep(0.3)  # Let process spawn

    # Cancel task
    cancelled = await q.cancel_task("cancel_task")
    assert cancelled is True
    assert task.status == "CANCELLED"

    try:
        await exec_task
    except Exception:
        pass


@pytest.mark.anyio
async def test_oom_zero_retry_policy():
    """Verify Out-Of-Memory (ResourceExhaustionError) triggers zero retries and immediate termination."""
    q = TaskQueue()
    task = TaskItem(
        task_id="oom_task",
        project_id="p5",
        task_type="heavy_engine",
        command=[sys.executable, "-c", "exit(0)"],
        required_ram_gb=999999.0,  # Impossible amount of RAM to trigger OOM check
        max_retries=2,
    )

    with pytest.raises(ResourceExhaustionError, match="Memory Exhaustion"):
        await q.execute_worker_task(task)

    assert task.status == "FAILED"
    # Zero retry policy for OOM:
    assert task.retry_count == 0
