# listen - configuration

edit these constants in `listen.py` (lines 1-27) to customize behavior

## audio settings

```python
SAMPLE_RATE = 16000  # Hz (whisper requires 16kHz)
CHANNELS = 1         # mono (1) or stereo (2)
DTYPE = 'float32'    # audio sample format
```

## vad (voice activity detection)

```python
VAD_THRESHOLD = 0.015       # volume threshold for silence
VAD_DEFAULT_DURATION = 2.0  # seconds of silence before auto-stop
```

lower threshold = more sensitive to quiet sounds
higher threshold = only loud sounds trigger recording

## server settings

```python
DEFAULT_SERVER_HOST = '0.0.0.0'  # listen on all interfaces
DEFAULT_SERVER_PORT = 5000        # http port
```

## optional dependencies

edit `requirements.txt` to enable features:

- **flask** - for `--server` flag
- **anthropic** - for `--claude` flag
- **piper-tts** - for text-to-speech
- **requests** - for web requests

minimal install only needs:
- openai-whisper
- sounddevice
- numpy
- scipy
