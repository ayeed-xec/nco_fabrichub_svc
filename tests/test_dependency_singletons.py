from svc.api.dependencies import _build_driver


def test_driver_is_singleton_from_dependency_cache():
    first = _build_driver()
    second = _build_driver()
    assert first is second
