# Termux Package for listen

This directory contains the build script for packaging `listen` for Termux.

## For Users

Once this package is accepted into termux-packages, you can install it with:

```bash
pkg install listen
```

Until then, use the install script:

```bash
curl -sSL https://raw.githubusercontent.com/gmoqa/listen/main/install-termux.sh | bash
```

## For Package Maintainers

### Building the package

1. Clone termux-packages:
```bash
git clone https://github.com/termux/termux-packages
cd termux-packages
```

2. Copy this build script:
```bash
mkdir -p packages/listen
cp /path/to/listen/termux/build.sh packages/listen/
```

3. Build the package:
```bash
./build-package.sh listen
```

### Submitting to termux-packages

1. Fork https://github.com/termux/termux-packages
2. Create `packages/listen/build.sh` with the contents from this directory
3. Test the build:
   ```bash
   ./build-package.sh listen
   ```
4. Create a PR to termux-packages

### Package Structure

```
termux-packages/
└── packages/
    └── listen/
        └── build.sh
```

## Dependencies

- `python` - Python interpreter
- `portaudio` - Audio I/O library
- `ffmpeg` - Audio/video processing

Python packages (installed via pip):
- `openai-whisper` - Whisper transcription model
- `sounddevice` - Audio recording
- `numpy` - Numerical computing
- `scipy` - Scientific computing

## Notes

- The package is platform-independent (pure Python)
- Recommends `tiny` or `base` models for mobile devices
- Includes post-install message with usage instructions
- Documentation installed to `$PREFIX/share/doc/listen/`
