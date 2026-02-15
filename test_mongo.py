import asyncio
from mongo import get_client

async def main():
    info = await get_client().server_info()
    print("Mongo version:", info["version"])

asyncio.run(main())
