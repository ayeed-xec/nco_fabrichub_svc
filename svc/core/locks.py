from contextlib import contextmanager
from threading import Lock


class LockUnavailableError(Exception):
    """Raised when a named lock is already held."""


class LockManager:
    _guard = Lock()
    _held_keys: set[str] = set()

    @contextmanager
    def acquire(self, key: str):
        with self._guard:
            if key in self._held_keys:
                raise LockUnavailableError(f"Lock key '{key}' is already held")
            self._held_keys.add(key)
        try:
            yield
        finally:
            with self._guard:
                self._held_keys.discard(key)
