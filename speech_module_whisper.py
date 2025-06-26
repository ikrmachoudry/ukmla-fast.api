import asyncio
import edge_tts
import pygame
import time
import uuid
import os

VOICE = "en-GB-RyanNeural"  # British Male
TEXT = "Hello Doctor, this is a test of Edge TTS with a UK accent."


async def main():
    filename = f"temp_{uuid.uuid4().hex}.mp3"
    communicate = edge_tts.Communicate(TEXT, voice=VOICE)
    await communicate.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.quit()
    os.remove(filename)

asyncio.run(main())
