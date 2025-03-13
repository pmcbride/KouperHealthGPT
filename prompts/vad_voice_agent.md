I'll provide a concise, clean, and practical example Python script combining all essential components into a single file:

**TL;DR:**
The script integrates the OpenAI Realtime API with voice interaction (microphone input, assistant speech playback) using **server-side VAD**, which automatically detects when you're done speaking, seamlessly outputs assistant responses as audio, and displays conversation transcripts in your terminal.

---

### ✅ **Full Python Example Script**
```python
import asyncio
import websockets
import json
import base64
import sounddevice as sd
import numpy as np
from collections import deque

# --- SETTINGS ---
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
MODEL = "gpt-4o-realtime-preview-2024-10-01"
VOICE = "openai/en-US/MikaMultilingual-v1"
SAMPLE_RATE = 16000
CHANNELS = 1
AUDIO_BLOCK_SIZE = 1024  # bytes per audio frame

# --- AUDIO SETTINGS ---
AUDIO_FORMAT = 'pcm_s16le'  # 16-bit PCM
SAMPLE_RATE = 24000  # GPT-4o realtime recommended sample rate
CHANNELS = 1

# Buffer for audio playback
audio_buffer = deque()

# Play audio asynchronously
def audio_callback(outdata, frames, time, status):
    global audio_buffer
    if len(audio_buffer) >= frames:
        chunk = [audio_buffer.popleft() for _ in range(frames)]
        outdata[:] = np.array(chunk).reshape(-1, CHANNELS)
    else:
        outdata.fill(0)

# Initialize audio playback stream
output_stream = sd.OutputStream(
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype='int16',
    callback=audio_callback,
    blocksize=1024
)

# --- WebSocket Handling ---
async def realtime_chat():
    uri = f"wss://api.openai.com/v1/realtime?model={MODEL}"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }

    async with websockets.connect(uri, extra_headers=headers) as websocket:
        # Configure session
        session_config = {
            "type": "session.update",
            "session": {
                "turn_detection": {"type": "server_vad"},
                "input_audio_format": AUDIO_FORMAT,
                "output_audio_format": AUDIO_FORMAT,
                "voice": VOICE,
                "instructions": "You are a helpful voice assistant.",
                "modalities": ["text", "audio"],
                "temperature": 0.7
            }
        }
        await websocket.send(json.dumps(session_update))
        print("Session configured. Speak now...")

        # Start audio input stream
        with sd.RawInputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16') as stream, audio_buffer:
            print("Listening... Speak now!")
            async def send_audio():
                while True:
                    audio_data, _ = sd.RawInputStream.read(stream, 1024)
                    audio_base64 = base64.b64encode(audio_data).decode('ascii')
                    message = {"type": "input_audio_buffer.append", "audio": audio_base64}
                    await websocket.send(json.dumps(message))

            async def receive_audio():
                async for message in websocket:
                    data = json.loads(message)
                    event_type = data.get("type")

                    if event_type := event.get("type"):
                        if etype == "transcription.complete":
                            text = event.get("text", "")
                            print(f"\nYou said: {text}\n")
                        elif etype == "response.audio.delta":
                            audio_chunk = base64.b64decode(data.get("delta"))
                            audio_np = np.frombuffer(audio_chunk, dtype='int16')
                            audio_buffer.extend(audio_np)
                        elif etype == "response.complete":
                            response_text = data.get("text", "")
                            print(f"Assistant: {response_text}\n")

            async def receive_audio():
                async for message in websocket:
                    data = json.loads(message)
                    etype = data.get("type")
                    if etype == "transcription.complete":
                        print(f"👤 You: {data.get('text', '')}")
                    elif etype == "response.complete":
                        print(f"🤖 Assistant: {data.get('text', '')}")
                    elif etype == "response.audio.delta":
                        audio_chunk = base64.b64decode(data.get("delta"))
                        audio_np = np.frombuffer(audio_chunk, dtype='int16')
                        audio_buffer.extend(audio_np)

            # Run send and receive concurrently
            await asyncio.gather(send_audio(), receive_audio())

    await send_audio_receive_events(uri, headers)

async def main():
    with audio_buffer:
        with sd.RawInputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16'):
            with audio_buffer:
                with sd.OutputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16', callback=audio_callback):
                    await realtime_chat()

if __name__ == "__main__":
    print("Initializing OpenAI Realtime Voice Assistant...")
    asyncio.run(realtime_chat())
```

---

### What does this script do?

- **Realtime Audio Streaming with WebSockets**: Connects to OpenAI’s Realtime API (`gpt-4o`) via WebSocket.
- **Voice Activity Detection (VAD)**: Using OpenAI's server-side VAD, the assistant automatically detects when the user finishes speaking and starts responding, ensuring a smooth conversational flow.
- **Audio Processing**: Uses `sounddevice` to capture audio from the microphone and play audio responses seamlessly.
- **Outputting text**: Clearly prints text transcriptions to the terminal.

## 📌 Requirements and Installation

```bash
pip install websockets sounddevice numpy
```

If not installed:
```bash
pip install sounddevice numpy websockets
```

### Running the script:
Replace `"YOUR_OPENAI_API_KEY"` with your valid OpenAI API key and run:

```shell
python realtime_agent.py
```

### Dependencies Installation (condensed):

```shell
pip install websockets sounddevice numpy
```

---

### **Final notes:**

- **Real-world adjustments:**
  Adjust audio settings (`sample_rate`, `blocksize`) to best match your audio hardware.

- **API Key security:**
  Secure your API key, do not commit to version control. Use environment variables in production.

- **Error handling:**
  This simplified script doesn't fully handle all network/audio errors. You may need more robust error-handling in a production scenario.

- **Further UI:**
  If a more complex UI is needed (e.g., GUI or web-based), consider frameworks like Streamlit, Gradio, or Flask with WebRTC to handle audio streaming visually.

This fully-integrated, concise Python example should give you a solid starting point for seamless, hands-free conversational interactions leveraging OpenAI’s Realtime API, Agents SDK (if you add it for advanced tasks separately), and server-side VAD for smooth audio interactions.