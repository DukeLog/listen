# Contributing listen to termux-packages

This guide helps you submit `listen` as an official Termux package.

## Prerequisites

- GitHub account
- Termux environment (for testing) or Docker
- Fork of https://github.com/termux/termux-packages

## Step-by-Step Guide

### 1. Fork termux-packages

```bash
# On GitHub, fork: https://github.com/termux/termux-packages
git clone https://github.com/YOUR_USERNAME/termux-packages
cd termux-packages
```

### 2. Create package directory

```bash
mkdir -p packages/listen
```

### 3. Copy build script

```bash
# Copy the build.sh from this repo
cp /path/to/listen/termux/build.sh packages/listen/
```

### 4. Calculate SHA256 checksum

```bash
# Download the release tarball
wget https://github.com/gmoqa/listen/archive/refs/tags/v1.0.0.tar.gz

# Calculate checksum
sha256sum v1.0.0.tar.gz

# Update build.sh with the actual checksum
# Replace SKIP_CHECKSUM with the real hash
```

### 5. Test the build

**Option A: Using Termux**
```bash
./build-package.sh listen
```

**Option B: Using Docker**
```bash
./scripts/run-docker.sh ./build-package.sh listen
```

### 6. Test installation

```bash
# Install the built package
apt install ./debs/listen_*.deb

# Test it works
listen --help
listen -m tiny  # test recording (if you have mic access)
```

### 7. Create Pull Request

```bash
# Commit your changes
git checkout -b add-listen-package
git add packages/listen/build.sh
git commit -m "New package: listen

listen is a minimal audio transcription tool that runs 100% on-premise.
It uses OpenAI Whisper for speech-to-text conversion.

Features:
- Voice activity detection (VAD)
- Signal-based control
- HTTP API server mode
- Multiple language support
- Optimized for mobile (tiny/base models)

Package details:
- Homepage: https://github.com/gmoqa/listen
- License: MIT
- Dependencies: python, portaudio, ffmpeg
- Platform independent: Yes
"

# Push to your fork
git push origin add-listen-package
```

### 8. Submit PR

1. Go to https://github.com/termux/termux-packages
2. Click "New Pull Request"
3. Select your fork and branch
4. Title: `New package: listen`
5. Description:

```markdown
## Package Information

- **Name**: listen
- **Description**: Minimal audio transcription tool - 100% on-premise
- **Homepage**: https://github.com/gmoqa/listen
- **License**: MIT
- **Version**: 1.0.0

## Why this package?

listen provides on-device speech-to-text transcription using OpenAI Whisper.
It's particularly useful for:
- Voice notes on mobile devices
- Offline transcription (no cloud/API required)
- Privacy-conscious users
- Termux users wanting voice input

## Testing

- [x] Builds successfully with `./build-package.sh listen`
- [x] Installs without errors
- [x] `listen --help` works
- [x] Basic recording and transcription works
- [x] Models (tiny/base) work on mobile devices

## Special considerations

- Recommends `tiny` or `base` models for mobile (memory constraints)
- Includes auto-stop via VAD (useful for mobile without keyboard)
- Post-install message guides users on mobile-optimized usage
```

## Troubleshooting

### Build fails with dependency issues

Check that dependencies are available in Termux:
```bash
pkg search python
pkg search portaudio
pkg search ffmpeg
```

### Package too large

The package itself is small (~500 lines Python). The models are downloaded
at runtime by Whisper, not included in the package.

### Python dependencies fail

If `pip install` fails during build, you may need to:
1. Add build dependencies to `TERMUX_PKG_BUILD_DEPENDS`
2. Use `--no-build-isolation` flag
3. Pre-build wheels for arm/aarch64

### Checksum mismatch

Make sure you're using the correct release tag and the checksum
matches the actual tarball:

```bash
curl -L https://github.com/gmoqa/listen/archive/refs/tags/v1.0.0.tar.gz | sha256sum
```

## PR Review Process

1. Maintainers will review your PR
2. They may request changes (formatting, dependencies, etc.)
3. CI will run automated tests
4. Once approved and merged, package will be available via `pkg install listen`

## After Merge

1. Update this repo's README.md to remove "coming soon"
2. Update TERMUX.md with the actual issue/PR number
3. Announce on relevant communities

## Resources

- [Termux Packages Documentation](https://github.com/termux/termux-packages/blob/master/README.md)
- [Package Build System](https://github.com/termux/termux-packages/wiki/Build-system)
- [Contributing Guidelines](https://github.com/termux/termux-packages/blob/master/CONTRIBUTING.md)

## Questions?

- Open an issue: https://github.com/gmoqa/listen/issues
- Ask on Termux: https://github.com/termux/termux-packages/discussions
