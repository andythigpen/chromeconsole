import asyncio
import ui

loop = asyncio.get_event_loop()

def main():
    app = loop.create_task(ui.run_async())
    try:
        loop.run_until_complete(app)
    finally:
        loop.close()


if __name__ == "__main__":
    main()
