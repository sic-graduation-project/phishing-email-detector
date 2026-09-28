from backend.app.rate_limit import SlidingWindowLimiter


def test_rate_limiter_rejects_requests_above_limit():
    limiter = SlidingWindowLimiter(limit=2)
    assert limiter.allow("client")
    assert limiter.allow("client")
    assert not limiter.allow("client")


def test_rate_limiter_keeps_clients_independent():
    limiter = SlidingWindowLimiter(limit=1)
    assert limiter.allow("client-a")
    assert not limiter.allow("client-a")
    assert limiter.allow("client-b")
