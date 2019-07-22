#!/usr/bin/env python3
import asyncio
import time

import aiohttp


async def look_up():
    async with aiohttp.request('GET', 'https://dictionary.cambridge.org/dictionary/english/get') as resp:
        text = await resp.text()
        print(text)


def main():
    loop = asyncio.get_event_loop()
    task = look_up()
    loop.run_until_complete(task)


if __name__ == '__main__':
    now = time.time()
    main()
    end = time.time()
    print('using time ' + str(end - now))
