import httpx


def build_session(settings):
    return httpx.Client(
        base_url=settings.ndfc_base_url,
        timeout=settings.ndfc_timeout_seconds,
        verify=settings.ndfc_verify_tls,
    )
