import time
from threading import Lock

class APIRateLimiter:
    def __init__(self, max_requests: int, period_seconds: int):
        self.max_requests = max_requests
        self.period_seconds = period_seconds
        self.requests_made = 0
        self.lock = Lock()
        self.start_time = time.time()

    def acquire(self) -> bool:
        with self.lock:
            current_time = time.time()
            if current_time - self.start_time > self.period_seconds:
                self.requests_made = 0
                self.start_time = current_time
            if self.requests_made < self.max_requests:
                self.requests_made += 1
                return True
            return False
