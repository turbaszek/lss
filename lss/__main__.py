import asyncio

from lss.launchpad import Launchpad


async def main():
    launchpad = Launchpad()
    await launchpad.run()


if __name__ == "__main__":
    asyncio.run(main())
