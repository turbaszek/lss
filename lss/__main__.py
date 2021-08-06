import asyncio

from lss.sequencer import Sequencer


async def main():
    launchpad = Sequencer()
    await launchpad.run()


if __name__ == "__main__":
    asyncio.run(main())
