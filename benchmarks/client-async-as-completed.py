from aiohttp import ClientSession
import asyncio
from itertools import islice
import sys

def limited_as_completed(coros, limit):
    futures = [
        asyncio.ensure_future(c)
        for c in islice(coros, 0, limit)
    ]
    async def first_to_finish():
        while True:
            await asyncio.sleep(0)
            for f in futures:
                if f.done():
                    futures.remove(f)
                    try:
                        newf = next(coros)
                        futures.append(
                            asyncio.ensure_future(newf))
                    except StopIteration as e:
                        pass
                    return f.result()
    while len(futures) > 0:
        yield first_to_finish()

async def fetch(url, session):
    async with session.get(url) as response:
        return await response.read()

limit = 1000

async def print_when_done(tasks, session):
    for res in limited_as_completed(tasks, limit):
        await res

    await session.close()

r = int(sys.argv[1])
url = "http://localhost:8080/{}"
loop = asyncio.get_event_loop()
session = ClientSession()
coros = (fetch(url.format(i), session) for i in range(r))
loop.run_until_complete(print_when_done(coros, session))
loop.close()