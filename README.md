# listen

minimal audio transcription tool

## install

### homebrew (mac/linux)
```sh
brew tap gmoqa/listen
brew install listen
```

### termux (android)
```sh
# via package manager (coming soon - pending approval)
pkg install listen

# current install method (one-liner)
curl -sSL https://raw.githubusercontent.com/gmoqa/listen/main/install-termux.sh | bash
```

see [TERMUX.md](TERMUX.md) for detailed android setup

### arch linux
```sh
yay -S listen
```

### one-liner (generic linux/mac)
```sh
curl -sSL https://raw.githubusercontent.com/gmoqa/listen/main/install.sh | bash
```

## usage

### basic
```sh
listen              # record and transcribe (english)
listen -l es        # spanish
listen -m medium    # better model
listen -c           # send to claude
listen -v           # verbose mode
```

press SPACE to stop recording

### configuration

**set defaults (persistent)**
```sh
listen config -l es         # set spanish as default language
listen config -m tiny       # set tiny model as default
listen config --vad 3       # enable VAD with 3s silence
listen config --show        # view current config
listen config --reset       # delete config file
```

configuration is saved to `~/.listen/config.json`

**precedence**: CLI args > config file > defaults

```sh
listen config -l es -m tiny  # save defaults
listen                       # uses: es, tiny (from config)
listen -l en                 # uses: en (override), tiny (from config)
```

### advanced modes

**auto-stop with silence detection**
```sh
listen --vad 2      # stop after 2s of silence
```

**signal control (for scripts)**
```sh
listen --signal-mode &
kill -SIGUSR1 $(pgrep -f "listen.*signal")
```

**http api server**
```sh
listen -s                              # start server on :5000
listen -s --port 8080 --host 127.0.0.1
curl -X POST -F "audio=@file.mp3" http://localhost:5000/transcribe
```

## models

- tiny
- base (default)
- small
- medium
- large

## platform notes

### termux (android)

**microphone permissions**
```sh
# grant storage and microphone permissions
termux-setup-storage
# allow microphone when prompted
```

**recommended models for mobile**
- `tiny` - fastest, lowest memory (~1GB RAM)
- `base` - balanced (default, ~2GB RAM)
- avoid `medium`/`large` on phones (high memory usage)

**troubleshooting**
```sh
# if audio fails, try:
pkg install pulseaudio
pulseaudio --start

# check microphone access
termux-microphone-record -f test.wav -l 1
termux-microphone-record -q
```

## uninstall

**termux**
```sh
rm $PREFIX/bin/listen
pip uninstall openai-whisper sounddevice numpy scipy
```

**mac/linux**
```sh
rm -rf ~/.local/share/listen ~/.local/bin/listen
```

all processing happens locally on your device
