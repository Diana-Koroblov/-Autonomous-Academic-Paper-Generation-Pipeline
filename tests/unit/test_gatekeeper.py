import sys
import os
import asyncio
import pytest
import pytest_asyncio

# Add src to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from sdk.gatekeeper import Gatekeeper

@pytest_asyncio.fixture
async def gatekeeper():
    gk = Gatekeeper()
    # Speed up tests by overriding defaults
    gk.timeout_seconds = 2
    gk.max_retries = 2
    gk.backoff_factor = 0.1
    gk.max_rpm = 6000 # ensure tokens are available
    gk.tokens = 6000.0
    gk.start()
    yield gk
    await gk.stop()

@pytest.mark.asyncio
async def test_fifo_execution(gatekeeper):
    """Test that the Gatekeeper executes tasks sequentially in a FIFO manner."""
    results = []
    
    async def dummy_task(task_id, delay):
        await asyncio.sleep(delay)
        results.append(task_id)
        return task_id
        
    # t1 takes longer but is queued first.
    t1 = gatekeeper.execute(dummy_task, 1, 0.2)
    t2 = gatekeeper.execute(dummy_task, 2, 0.1)
    
    await asyncio.gather(t1, t2)
    
    # Because process_queue awaits the task, they execute strictly sequentially
    assert results == [1, 2]

@pytest.mark.asyncio
async def test_exponential_backoff_success(gatekeeper):
    """Test that the Gatekeeper successfully retries on transient 429 errors."""
    attempts = 0
    
    async def failing_task():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise Exception("API Error 429 Too Many Requests")
        return "success"
        
    result = await gatekeeper.execute(failing_task)
    assert result == "success"
    assert attempts == 2

@pytest.mark.asyncio
async def test_exponential_backoff_failure(gatekeeper):
    """Test that the Gatekeeper eventually fails after max_retries on 500 errors."""
    attempts = 0
    
    async def failing_task():
        nonlocal attempts
        attempts += 1
        raise Exception("API Error 500 Internal Server Error")
        
    with pytest.raises(Exception, match="500"):
        await gatekeeper.execute(failing_task)
        
    # 1 initial attempt + 2 max retries = 3 total attempts
    assert attempts == 3
