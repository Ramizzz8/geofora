from app.news.job import run_forever


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


async def test_waits_only_the_rest_of_the_interval():
    clock = Clock()
    slept = []

    async def cycle():
        clock.t += 600  # el ciclo tarda 10 min

    async def sleep(s):
        slept.append(s)
        clock.t += s

    await run_forever(cycle, interval_s=2700, sleep=sleep, now=clock, iterations=2)
    assert slept == [2100, 2100]


async def test_long_cycle_starts_next_immediately_and_survives_errors():
    clock = Clock()
    slept, calls = [], []

    async def cycle():
        calls.append(1)
        clock.t += 4000
        if len(calls) == 1:
            raise RuntimeError("boom")

    async def sleep(s):
        slept.append(s)

    await run_forever(cycle, interval_s=2700, sleep=sleep, now=clock, iterations=2)
    assert len(calls) == 2
    assert slept == [0, 0]
