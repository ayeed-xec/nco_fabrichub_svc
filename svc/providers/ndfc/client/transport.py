from svc.providers.ndfc.exceptions import NdfcProviderError


def _request(session, method: str, path: str, endpoint: str, *, payload=None, critical: bool = True):
    try:
        response = session.request(method, path, json=payload)
        response.raise_for_status()
        if not response.content:
            return {}
        return response.json()
    except Exception as error:  # pragma: no cover - exercised by adapter tests via fake exceptions
        raise NdfcProviderError(str(error), endpoint=endpoint, critical=critical) from error


def get_json(session, path: str, endpoint: str, *, critical: bool = True):
    return _request(session, "GET", path, endpoint, critical=critical)


def post_json(session, path: str, endpoint: str, payload: dict, *, critical: bool = True):
    return _request(session, "POST", path, endpoint, payload=payload, critical=critical)
