# listen

minimal audio transcription tool

100% on-premise audio transcription using OpenAI Whisper. No API keys, no cloud services, no data leaves your device.

## features

- record from microphone and transcribe in real-time
- transcribe audio files (mp3, wav, m4a, flac, ogg, etc.)
- multiple language support
- multiple stopping modes: manual (SPACE), auto (VAD), signal (SIGUSR1)
- scripting support with JSON output and quiet mode
- persistent configuration
- HTTP API server mode
- claude integration
- clipboard support
- works on macOS, Linux, Android (Termux)

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

### basic recording
```sh
listen              # record and transcribe (english)
listen -l es        # spanish
listen -l fr        # french
listen -m medium    # better model
listen -c           # send to claude
listen -v           # verbose mode
```

press SPACE to stop recording (default mode)

### stopping modes

**manual stop (default)**
```sh
listen              # press SPACE to stop
```

**auto-stop with silence detection (VAD)**
```sh
listen --vad 2      # stop after 2 seconds of silence
listen --vad 3      # stop after 3 seconds of silence
```

**signal control (for scripts/automation)**
```sh
listen --signal-mode &
PID=$!
# do something...
kill -SIGUSR1 $PID  # stop recording
```

### file processing
```sh
listen -f audio.mp3           # transcribe audio file
listen -f audio.wav -l es     # transcribe with language
listen -f audio.m4a -m medium # transcribe with better model
listen -f audio.mp3 -c        # transcribe and send to claude
```

supports: mp3, wav, m4a, flac, ogg, and other formats supported by ffmpeg

### scripting / automation
```sh
# output options
listen --quiet                           # no UI, just text
listen --json                            # JSON output
listen --clipboard                       # copy to clipboard
listen -o transcript.txt                 # save to file

# combine flags for automation
listen --quiet --json -o output.json     # silent JSON output
listen --quiet --json --signal-mode      # for background recording
listen --vad 2 --json                    # auto-stop with JSON
```

**example: background recording with signal**
```sh
listen --quiet --json --signal-mode -l es > output.json &
PID=$!
sleep 5  # record for 5 seconds
kill -SIGUSR1 $PID
wait $PID
cat output.json
```

### configuration

**set defaults (persistent)**
```sh
listen config -l es           # set spanish as default language
listen config -m tiny         # set tiny model as default
listen config --vad 3         # enable VAD with 3s silence
listen config --signal-mode   # toggle signal mode on/off
listen config --verbose       # toggle verbose mode
listen config --claude        # toggle claude integration
listen config --show          # view current config
listen config --reset         # delete config file
```

**server configuration**
```sh
listen config --host 0.0.0.0  # set server host
listen config --port 8080     # set server port
```

configuration is saved to `~/.listen/config.json`

**precedence**: CLI args > config file > defaults

```sh
listen config -l es -m tiny  # save defaults
listen                       # uses: es, tiny (from config)
listen -l en                 # uses: en (override), tiny (from config)
```

### http api server
```sh
listen -s                              # start server on :5000
listen -s --port 8080 --host 127.0.0.1
listen -s -m medium -l es              # server with specific model/language

# test the server
curl http://localhost:5000/health
curl -X POST -F "audio=@file.mp3" http://localhost:5000/transcribe
curl -X POST -F "audio=@file.mp3" -F "language=es" http://localhost:5000/transcribe
```

## models

### philosophy

this project is committed to always using the **best open source language model** available at any given time. when a superior open source model emerges, we will update to it. currently, we use OpenAI Whisper as it represents the state-of-the-art in open source speech recognition.

### available whisper models

models ordered by speed/accuracy tradeoff:

| model | size | speed | accuracy | use case |
|-------|------|-------|----------|----------|
| tiny | ~75MB | fastest | lowest | quick tests, mobile |
| base | ~150MB | fast | good | default, balanced |
| small | ~500MB | medium | better | more accuracy needed |
| medium | ~1.5GB | slow | high | production quality |
| large | ~3GB | slowest | highest | maximum accuracy |

**recommendations:**
- development/testing: `tiny` or `base`
- production: `small` or `medium`
- mobile/termux: `tiny` (avoid medium/large due to memory)

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

## development

### running tests

**quick start**
```sh
./run_tests.sh              # run all tests
./run_tests.sh quick        # quick run (minimal output)
./run_tests.sh coverage     # run with coverage report
./run_tests.sh config       # run only config tests
./run_tests.sh listen       # run only listen tests
```

**using pytest directly**
```sh
# run all tests
pytest

# run with coverage report
pytest --cov=. --cov-report=html

# run specific test file
pytest test_config.py -v

# run specific test class
pytest test_config.py::TestConfigDefaults -v

# run specific test
pytest test_config.py::TestConfigDefaults::test_get_defaults -v
```

### test structure
- `test_config.py` - tests for configuration management
- `test_listen.py` - tests for CLI and main functionality
- `conftest.py` - shared fixtures and test utilities
- `pytest.ini` - pytest configuration

### coverage
view coverage report after running tests with `--cov-report=html`:
```sh
open htmlcov/index.html  # mac
xdg-open htmlcov/index.html  # linux
```

## command reference

### all flags

**modes**
```sh
listen                    # default: record from microphone
listen -f FILE            # transcribe audio file
listen -s                 # start HTTP API server
listen config             # manage configuration
```

**recording options**
```sh
-l, --language LANG       # language code (en, es, fr, de, etc.)
-m, --model MODEL         # whisper model (tiny, base, small, medium, large)
-c, --claude              # send transcription to claude
-v, --verbose             # verbose debug output
```

**stopping modes**
```sh
# default: press SPACE to stop
--vad SECONDS             # auto-stop after N seconds of silence
--signal-mode             # stop with SIGUSR1 signal
```

**output options**
```sh
-q, --quiet               # no UI, only transcription text
-j, --json                # output in JSON format
--clipboard               # copy transcription to clipboard
-o, --output FILE         # write transcription to file
```

**server options**
```sh
--host HOST               # server host (default: 0.0.0.0)
--port PORT               # server port (default: 5000)
```

### examples

**basic recording**
```sh
listen                             # english, base model
listen -l es                       # spanish
listen -l es -m medium             # spanish with better model
```

**file transcription**
```sh
listen -f audio.mp3                # transcribe file
listen -f audio.mp3 -l es -m small # with options
```

**automation**
```sh
listen --quiet --json              # minimal output
listen --vad 2 --json              # auto-stop with JSON
listen --signal-mode --quiet &     # background recording
```

**server**
```sh
listen -s                          # start server
listen -s --port 8080 -m medium    # custom port and model
```

## uninstall

**homebrew**
```sh
brew uninstall listen
brew untap gmoqa/listen
```

**arch linux**
```sh
yay -R listen
# or
sudo pacman -R listen
```

**termux**
```sh
rm $PREFIX/bin/listen
pip uninstall openai-whisper sounddevice numpy scipy
```

**manual install**
```sh
rm -rf ~/.local/share/listen ~/.local/bin/listen
```

## notes

- all processing happens locally on your device
- no API keys required
- no cloud services or external dependencies
- first run downloads the specified Whisper model (~75MB-3GB)
- models are cached for future use
