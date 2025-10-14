# listen on Termux (Android)

## Quick Install

**Current method** (until package is approved):
```bash
curl -sSL https://raw.githubusercontent.com/gmoqa/listen/main/install-termux.sh | bash
```

**Future method** (once in termux-packages):
```bash
pkg install listen
```

## Package Status

🔄 **Pending submission to termux-packages**

We're working on getting `listen` into the official Termux repositories.
Track progress: [Issue #XXX](https://github.com/termux/termux-packages/issues/XXX)

## Manual Installation

If you prefer manual installation:

```bash
# Install system dependencies
pkg install python portaudio ffmpeg

# Install Python dependencies
pip install openai-whisper sounddevice numpy scipy

# Download and install listen
curl -sSL https://raw.githubusercontent.com/gmoqa/listen/main/listen.py -o $PREFIX/bin/listen
chmod +x $PREFIX/bin/listen
```

## Usage

### Basic
```bash
listen              # record and transcribe (english)
listen -l es        # spanish
listen -m tiny      # fastest model (recommended)
```

### Recommended for Mobile
```bash
listen --vad 2      # auto-stop after 2s of silence
listen -m tiny      # use lightweight model
```

## Permissions

On first run, allow microphone access when prompted by Android.

### Setup Storage
```bash
termux-setup-storage
```

## Recommended Models

- **tiny** - Fastest, ~1GB RAM (recommended)
- **base** - Balanced, ~2GB RAM (default)
- ❌ **medium/large** - Too heavy for mobile

## Troubleshooting

### Microphone not working
```bash
# Install termux-api
pkg install termux-api

# Test microphone
termux-microphone-record -f test.wav -l 1
termux-microphone-record -q
```

### Audio library issues
```bash
# Install/restart pulseaudio
pkg install pulseaudio
pulseaudio --start
```

### Out of memory
```bash
# Use smaller model
listen -m tiny

# Or use auto-stop to keep recordings short
listen --vad 2
```

## Alternative Control Methods

If SPACE key doesn't work reliably:

**Auto-stop (recommended)**
```bash
listen --vad 2      # stops after 2s of silence
```

**Signal control**
```bash
listen --signal-mode &
kill -SIGUSR1 $(pgrep -f listen)
```

## Uninstall

```bash
# If installed via script
rm $PREFIX/bin/listen
pip uninstall openai-whisper sounddevice numpy scipy

# If installed via pkg (future)
pkg uninstall listen
```

## Contributing to Termux Package

Want to help get `listen` into termux-packages? See [termux/README.md](termux/README.md)

## Support

- Issues: https://github.com/gmoqa/listen/issues
- Termux package: [Pending]
