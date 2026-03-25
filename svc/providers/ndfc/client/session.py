from functools import lru_cache

import httpx


@lru_cache(maxsize=1)
def _cached_session(base_url: str, timeout_seconds: int, verify_tls: bool) -> httpx.Client:
    return httpx.Client(
        base_url=base_url,
        timeout=timeout_seconds,
        verify=verify_tls,
    )


def build_session(settings):
    return _cached_session(
        base_url=settings.ndfc_base_url,
        timeout_seconds=settings.ndfc_timeout_seconds,
        verify_tls=settings.ndfc_verify_tls,
    )
