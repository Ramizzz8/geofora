import pytest

from app.cache import cached
from app.db import connect, init_db


@pytest.fixture
def conn(tmp_path):
    c = connect(str(tmp_path / "c.db"))
    init_db(c)
    return c


class Clock:
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t


def fetcher(value=None, error=None):
    calls = []

    async def fetch():
        calls.append(1)
        if error:
            raise error
        return value

    return fetch, calls


async def test_fresh_hit_skips_fetch(conn):
    clock = Clock()
    fetch, _ = fetcher({"v": 1})
    await cached(conn, "k", 60, fetch, now=clock)
    fetch2, calls2 = fetcher({"v": 2})
    clock.t += 30
    r = await cached(conn, "k", 60, fetch2, now=clock)
    assert r.value == {"v": 1}
    assert r.stale is False
    assert calls2 == []


async def test_expired_refetches(conn):
    clock = Clock()
    fetch, _ = fetcher({"v": 1})
    await cached(conn, "k", 60, fetch, now=clock)
    clock.t += 61
    fetch2, calls2 = fetcher({"v": 2})
    r = await cached(conn, "k", 60, fetch2, now=clock)
    assert r.value == {"v": 2}
    assert r.fetched_at == clock.t
    assert calls2 == [1]


async def test_fetch_error_returns_stale(conn):
    clock = Clock()
    fetch, _ = fetcher({"v": 1})
    await cached(conn, "k", 60, fetch, now=clock)
    old = clock.t
    clock.t += 3600
    fetch2, _ = fetcher(error=TimeoutError())
    r = await cached(conn, "k", 60, fetch2, now=clock)
    assert r.stale is True
    assert r.value == {"v": 1}
    assert r.fetched_at == old


async def test_fetch_error_without_value_raises(conn):
    fetch, _ = fetcher(error=TimeoutError())
    with pytest.raises(TimeoutError):
        await cached(conn, "k", 60, fetch, now=Clock())
