import asyncio


async def run_jobs(client_factory, jobs):
    client = client_factory()
    for job in jobs:
        asyncio.create_task(client.send(job))
    await asyncio.Event().wait()
