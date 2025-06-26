import pyttsx3
import asyncio

_engine = pyttsx3.init()


async def speak(text):
    print(f"🗣️ Speaking: {text}")
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, lambda: _engine.say(text) or _engine.runAndWait())


async def main():
    await speak("Hello! This is a test of pyttsx3 speaking out loud.")

if __name__ == "__main__":
    asyncio.run(main())
