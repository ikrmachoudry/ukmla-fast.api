# ============================================
# 🔊 TTS MODULE — Edge TTS + Playsound
# ============================================

import asyncio
import os
import uuid
from edge_tts import Communicate
from playsound import playsound  # ✅ Cross-platform audio playback

# ============================================
# 🗣️ Default Voice Settings
# ============================================

DEFAULT_VOICE = "en-GB-RyanNeural"  # UK Male
DEFAULT_RATE = "+8%"                # Slightly faster than normal
DEFAULT_PITCH = "+0Hz"              # Neutral pitch

# ============================================
# 🔉 Speak Text Function
# ============================================


async def speak_text(text: str):
    """
    Converts text to speech using Edge TTS, plays the audio, and deletes the file.

    Args:
        text (str): The response text to be spoken aloud.
    """
    try:
        # Generate unique filename
        file_name = f"tts_{uuid.uuid4().hex}.mp3"

        # Configure TTS engine
        communicate = Communicate(
            text=text,
            voice=DEFAULT_VOICE,
            rate=DEFAULT_RATE,
            pitch=DEFAULT_PITCH
        )

        # Save TTS output
        await communicate.save(file_name)

        # Play the audio
        playsound(file_name)

        # Auto-delete after playing
        os.remove(file_name)

    except Exception as e:
        print(f"❌ TTS Error: {e}")
